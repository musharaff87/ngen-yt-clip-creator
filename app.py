from flask import Flask
from routes import init_routes
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Initialize routes
init_routes(app)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)