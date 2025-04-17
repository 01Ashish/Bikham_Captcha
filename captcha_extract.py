from pathlib import Path
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("api_key1")

genai.configure(api_key=api_key)

def regex_search(var):
    text = str(var)
    start_index = text.find('{')

    # Find the ending index of the last }
    end_index = text.rfind('}')

    # Extract the desired content
    clean_text = text[start_index:end_index + 1]
    data = json.loads(clean_text)
    return data

MODEL_CONFIG = {
  "temperature": 0.2,
  "top_p": 1,
  "top_k": 32,
  "max_output_tokens": 4096,
}

## Safety Settings of Model
safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  }
]

model = genai.GenerativeModel(model_name = "gemini-2.5-pro-preview-03-25",
                              generation_config = MODEL_CONFIG,
                              safety_settings = safety_settings)

def pdf_format(pdf_path,ext):
    pdf = Path(pdf_path)

    pdf_parts = [
            {
                "mime_type": f"image/{ext}", ## Mime type are PNG - image/png. JPEG - image/jpeg. WEBP - image/webp
                "data": pdf.read_bytes()
            }
        ]

    # if file_extension == 'pdf':
    #     pdf_parts = [
    #         {
    #             "mime_type": f"application/{file_extension}", ## Mime type are PNG - image/png. JPEG - image/jpeg. WEBP - image/webp
    #             "data": pdf.read_bytes()
    #         }
    #     ]
    # else:
    #     pdf_parts = [
    #         {
    #             "mime_type": f"image/{file_extension}", ## Mime type are PNG - image/png. JPEG - image/jpeg. WEBP - image/webp
    #             "data": pdf.read_bytes()
    #         }
    #     ]
    return pdf_parts


def gemini_output(pdf_path, system_prompt, user_prompt,ext):

    pdf_info = pdf_format(pdf_path,ext)
    input_prompt= [system_prompt, pdf_info[0], user_prompt]
    response = model.generate_content(input_prompt)
    return response.text









