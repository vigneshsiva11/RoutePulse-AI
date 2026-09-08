from flask import Flask
from flask_cors import CORS
from config import Config
from utils.db import db
from routes.traffic_routes import traffic_bp
from routes.control_routes import control_bp
from routes.emv_routes import emv_bp

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db.init_app(app)
with app.app_context():
    db.create_all()


# Register blueprints
app.register_blueprint(control_bp, url_prefix="/control")
app.register_blueprint(traffic_bp, url_prefix="/traffic")
app.register_blueprint(emv_bp, url_prefix="/emv")

if __name__ == "__main__":
    app.run(port=5000, debug=False)
