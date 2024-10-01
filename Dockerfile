FROM python:3.10
EXPOSE 5000
WORKDIR /app
COPY requirements.txt .
RUN apt-get update
RUN apt-get install -y libtesseract-dev tesseract-ocr
RUN pip install -r requirements.txt
COPY . .
CMD ["flask", "run", "--host", "0.0.0.0"]