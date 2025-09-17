from fastapi import FastAPI
import uvicorn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
def root():
    logger.info("Root endpoint called")
    return {"message": "Hello World"}

@app.get("/health")
def health():
    logger.info("Health endpoint called")
    try:
        result = {"status": "ok"}
        logger.info(f"Returning health result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in health endpoint: {e}")
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    logger.info("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=9000, log_level="info")