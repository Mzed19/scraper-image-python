import io
import os
import cv2
import numpy as np
import pdfplumber
import easyocr
import pytesseract
from PIL import Image
from flask import request, jsonify, render_template
from flask_smorest import Blueprint
from pdf2image import convert_from_bytes
from google import genai
from src.schemas import ScraperFile
from src.domain.enums.scraper_libs import ScraperLibs
from dotenv import load_dotenv
from google.genai import types
import tempfile

scraper_bp = Blueprint("scraper", __name__, description="Operações de OCR de alta precisão")

easyocr_reader = easyocr.Reader(['en', 'pt'])

def preprocess_image(pil_image):
    """
    Aplica técnicas de Visão Computacional para limpar a imagem
    antes de enviar para os motores de OCR.
    """
    img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    processed = cv2.adaptiveThreshold(
        cv2.GaussianBlur(gray, (5, 5), 0), 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    return processed

def extract_from_pdf(file_bytes_io):
    """
    Tenta extrair texto nativo. Se for PDF escaneado, retorna lista de imagens.
    """
    text = ""
    with pdfplumber.open(file_bytes_io) as pdf:
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
    
    if len(text.strip()) > 15:
        return text.strip(), None
    
    file_bytes_io.seek(0)
    images = convert_from_bytes(file_bytes_io.read())
    return None, images

@scraper_bp.route('/')
def index():
    return render_template('index.html', metrics={})

@scraper_bp.route('/extract-text/<string:ocr_type>', methods=['POST'])
@scraper_bp.response(200, ScraperFile)
def extract_text(ocr_type):
    if 'image' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado sob a chave "image"'}), 400

    file = request.files['image']
    file_content = file.read()
    filename = file.filename.lower()
    
    extracted_chunks = []

    try:
        if filename.endswith('.pdf'):
            text_nativo, images = extract_from_pdf(io.BytesIO(file_content))
            if text_nativo:
                return {'ocrType': 'pdf_text', 'extractedText': text_nativo}
            process_list = images
        else:
            process_list = [Image.open(io.BytesIO(file_content))]

        for img in process_list:
            img_cleaned = preprocess_image(img)

            if ocr_type.lower() == ScraperLibs.EASYOCR.value:
                res = easyocr_reader.readtext(img_cleaned, detail=0)
                extracted_chunks.append(" ".join(res))
            
            elif ocr_type.lower() == ScraperLibs.PYTESSERACT.value:
                config = '--oem 3 --psm 3 -l por+eng'
                res = pytesseract.image_to_string(img_cleaned, config=config)
                extracted_chunks.append(res)

            elif ocr_type.lower() == ScraperLibs.GEMINI.value:
                res = gemini_ocr(img)
                extracted_chunks.append(res)


        return {
            'ocrType': ocr_type,
            'extractedText': "\n".join(extracted_chunks).strip()
        }

    except Exception as e:
        print(f"Erro interno: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
def gemini_ocr(pil_image):
    load_dotenv()
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    try:
        prompt = "Analise esta imagem e extraia todo o texto visível. Mantenha a formatação original."

        response = client.models.generate_content(
            model="gemini-3-flash-preview", contents=[prompt, pil_image]
        )
        
        return response.text

    except Exception as e:
        return f"Erro no Gemini OCR: {str(e)}"