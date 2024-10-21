from flask import Flask
from flask_smorest import Api
from flask_cors import CORS

from src.services.scraper.scraper import scraper_bp

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["API_TITLE"] = "Scraper"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"

api = Api(app)

api.register_blueprint(scraper_bp)
