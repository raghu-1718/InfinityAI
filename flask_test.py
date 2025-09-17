from flask import Flask
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def root():
    logger.info("Root endpoint called")
    return {"message": "Hello World"}

@app.route('/health')
def health():
    logger.info("Health endpoint called")
    return {"status": "ok"}

if __name__ == "__main__":
    logger.info("Starting Flask server...")
    app.run(host="0.0.0.0", port=9001, debug=True)
