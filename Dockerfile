FROM python:3.10
EXPOSE 5000
WORKDIR /app
COPY requirements.txt .
RUN apt-get update
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-por \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*
    

COPY . .
CMD ["tail", "-f", "/dev/null"]
# execute after up container flask run --host 0.0.0.0