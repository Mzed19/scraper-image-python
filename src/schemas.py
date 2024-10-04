from marshmallow import fields, Schema

class ScraperFile(Schema):
    extractedText = fields.Str(required=True)
    ocrType = fields.Str(required=True)
