from config import ConfigClass
from app import create_app, db
from flask_cors import CORS
import os

app = create_app(ConfigClass)
CORS(app, resources={r"/predict": {"origins": "*"}})

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)