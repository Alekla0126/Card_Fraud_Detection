from auth import auth_blueprint
from main import main_blueprint
from app import create_app
import os

app = create_app()

# Register blueprints
app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(main_blueprint)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)