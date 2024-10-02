from flask import request, jsonify
from flask_smorest import Blueprint
import easyocr
import pytesseract
from PIL import Image
import numpy as np
import torch

scraper_bp = Blueprint("scraper", __name__, description="Operações de OCR")

easyocr_reader = easyocr.Reader(['en', 'pt'])

@scraper_bp.route('/extract-text/<string:ocr_type>', methods=['POST'])
def extract_text(ocr_type):
    print(torch.cuda.is_available())

    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    image = Image.open(file)

    extracted_text = ''

    image_np = np.array(image)

    match ocr_type.lower():
        case 'easyocr':
            try:
                extracted_text = easyocr_reader.readtext(image_np, detail=0)
            except Exception as e:
                extracted_text = f"Erro no EasyOCR: {str(e)}"
        case 'pytesseract':
            try:
                extracted_text = pytesseract.image_to_string(image)
                extracted_text = extracted_text.replace('\n', ' ')
            except Exception as e:
                extracted_text = f"Erro no Tesseract: {str(e)}"
        case _:
            return jsonify({'error': 'Invalid OCR type. Use "easyocr" or "pytesseract".'}), 400

    return jsonify({
        'ocr_type': ocr_type,
        'extracted_text': ' '.join(extracted_text) if isinstance(extracted_text, list) else extracted_text
    })
