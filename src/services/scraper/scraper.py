from flask import request, jsonify
from flask_smorest import Blueprint
import easyocr
import pytesseract
from PIL import Image
import numpy as np
from src.schemas import ScraperFile
from src.domain.enums.scraper_libs import ScraperLibs

scraper_bp = Blueprint("scraper", __name__, description="Operações de OCR")

easyocr_reader = easyocr.Reader(['en', 'pt'])

@scraper_bp.route('/extract-text/<string:ocr_type>', methods=['POST'])
@scraper_bp.response(200, ScraperFile)
def extract_text(ocr_type):

    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    
    image = Image.open(file)

    extracted_text = ''

    match ocr_type.lower():
        case ScraperLibs.EASYOCR.value:
            extracted_text = use_easyocr(image)
        case ScraperLibs.PYTESSERACT.value:
            extracted_text = use_pytesseract(image)
        case _:
            return jsonify({'error': 'Invalid OCR type. Use "easyocr" or "pytesseract".'}), 400

    return {
        'ocrType': ocr_type,
        'extractedText': ' '.join(extracted_text) if isinstance(extracted_text, list) else extracted_text
    }
    
def use_pytesseract(image):
    config = '--oem 3 --psm 11'
    extracted_text = pytesseract.image_to_string(image, config = config)
    return extracted_text.replace('\n', ' ')

def use_easyocr(image):
    image_np = np.array(image)
    return easyocr_reader.readtext(image_np, detail=0)
