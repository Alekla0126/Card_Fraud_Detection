# wsgi.py or run.py (or whatever the filename is)

from app import app  # Import the Flask app instance from the app package/module
import os

# Check if this script is the main program and not imported elsewhere
if __name__ == "__main__":
    # Retrieve port number from environment or default to 5000
    port = int(os.environ.get('PORT', 5000))

    # Start the Flask application
    app.run(host='0.0.0.0', port=port)