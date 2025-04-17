from flask import Flask, request, render_template, jsonify
import requests
from captcha_extract import gemini_output, regex_search
import os
import glob
import fitz
from werkzeug.utils import secure_filename



app = Flask(__name__)

# Configurations
UPLOAD_FOLDER = 'uploads'
PDF_FOLDER = os.path.join(UPLOAD_FOLDER, 'pdf')
IMAGE_FOLDER = os.path.join(UPLOAD_FOLDER, 'images')
CONVERTED_FOLDER = os.path.join(UPLOAD_FOLDER, 'converted')

for folder in [PDF_FOLDER, IMAGE_FOLDER, CONVERTED_FOLDER]:
    os.makedirs(folder, exist_ok=True)
[os.remove(f) for f in glob.glob(os.path.join(PDF_FOLDER, "*"))]
[os.remove(f) for ext in ('*.jpeg', '*.jpg', '*.png') for f in glob.glob(os.path.join(UPLOAD_FOLDER, ext))]
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_pdf_to_images(pdf_path, output_folder):
    pdf_document = fitz.open(pdf_path)
    
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        image_filename = os.path.join(output_folder, f'page_{page_num + 1}.png')
        pix.save(image_filename)
        break
    return image_filename

@app.route('/upload', methods=['POST'])
def upload_file():    
    file_url = request.form['file_url']
    response = requests.get(file_url)
    if response.status_code == 200:    
        # Get the content type from the response headers
        content_type = response.headers.get('Content-Type')
        print("content_type: ", content_type)
        if 'pdf' in content_type:
            file_extension = 'pdf'
        elif 'image' in content_type:
            if 'jpeg' in content_type:
                file_extension = 'jpg'
            elif 'jpg' in content_type:
                file_extension = 'jpg'
            elif 'png' in content_type:
                file_extension = 'png'
        elif 'jpg' in content_type:
            file_extension = 'jpg'
        elif 'png' in content_type:
            file_extension = 'png'
                
        content = response.content
        # pure_name = f'file_{1}'
        # extension = file
        ori_img_new = f"file_{1}.{file_extension}"
        save_folder = PDF_FOLDER
        ext=''
        if file_extension=='pdf':    
            image_path = os.path.join(save_folder, ori_img_new)
            
            with open(image_path, 'wb') as file:
                        file.write(content)
            image_path = convert_pdf_to_images(os.path.join(save_folder, ori_img_new), CONVERTED_FOLDER)
            ext = 'png'
        else:
            image_path = os.path.join(UPLOAD_FOLDER, ori_img_new)
            with open(image_path, 'wb') as file:
                        file.write(content)  
            ext = file_extension      
        # Save the content to a file
        system_prompt = """
            You are a very professional captcha reader & extractor. 
            You are specifically trained to recognize alphanumeric characters accurately, including both uppercase and lowercase letters. 
            Pay special attention to the difference between similar-looking characters, such as 'j' and '9'. Always ensure that lowercase and uppercase distinctions are preserved.

            """
        user_prompt = """Directive: Read the captcha image and display the content below.

            Instruction: Do not return any other text but what is inside the image. Return English text only of what is contained. Do not include any hex content or such.

            Make sure thereshould not be any blankspace between values/digit.

            Response Structure: {\"captcha\": <text goes here>}

            Only return the JSON data. Do not include any json indicators such as ```json etc.
            Note : Sometimes captcha image can consist overlapped values/digits. In that case, look for values with similar and most visible /font size.

            Prompt: Read the following image, and tell me the content in the box"""
        ans = gemini_output(image_path, system_prompt, user_prompt,ext)
        result = regex_search(ans)   
        return result
   
    
if __name__ == '__main__':
    app.run(debug=True)