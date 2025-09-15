from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Use Azure Redis Cache for rate limit storage
# Replace <azure-redis-host>, <password> with your Azure Redis details
limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri="redis://:<password>@<azure-redis-host>:6379/0"
)

@app.route("/health")
@limiter.limit("10/minute")
def health():
    return {"status": "ok"}

# Example MongoDB config (if using Azure MongoDB)
# limiter = Limiter(
#     get_remote_address,
#     app=app,
#     storage_uri="mongodb://<azure-mongo-host>:27017/"
# )

# Add your other routes and limits as needed
