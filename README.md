# InfinityAI.Pro - AI-Powered Trading Platform

```bash


```bash


```bash



- **AI/ML Trading Models**: MLflow integration for model management and deployment

   # InfinityAI.Pro - AI-Powered Trading Platform
- **Real-time Market Data**: Integration with Dhan API for live market data
- **Automated Trading**: Intelligent signal generation and trade execution
- **Risk Management**: Advanced risk assessment and portfolio optimization
- **Web Dashboard**: Modern React-based user interface
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **Multi-Deployment**: Support for Docker, Azure, Vercel, and Podman
- **Database Support**: MySQL/PostgreSQL with SQLite fallback

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Node.js 18+ and npm
- Poetry (Python dependency management)
- Docker (optional, for containerized deployment)

### Installation (Local Dev)

1. **Clone the repository**
   ```bash
   git clone https://github.com/raghu-1718/InfinityAI.git
   cd InfinityAI.Pro
   ```

1. **Backend Setup**

```bash
   # Install Python dependencies
   poetry install

   # Activate virtual environment
   poetry shell

   # Set up environment variables
   cp config/.env.example config/.env
   # Edit config/.env with your database and API credentials
   ```

1. **Database Setup**

```bash
   # For SQLite (development)
   export TESTING=1

   # For production database, update DATABASE_URL in .env
   poetry run python init_auth_db.py
   ```

1. **Frontend Setup**

```bash
   cd dashboard
   npm install
   npm start
   ```

1. **Start the Application**

```bash
# Backend (SQLite dev mode, from repo root)
pip install -r requirements.txt
./scripts/dev_backend.sh

# Frontend (Node 18 required)
cd dashboard
# Use Node 18 with nvm
export NVM_DIR="$HOME/.nvm"; [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" || [ -s "/usr/local/share/nvm/nvm.sh" ] && . "/usr/local/share/nvm/nvm.sh"
nvm install 18
nvm use 18
export REACT_APP_API_URL=http://localhost:8000
npm ci || npm install
npm start
```

Notes:
- Root endpoint `/` now returns a simple JSON banner; health is at `/health` and docs at `/docs`.
- Set `CORS_ALLOW_ORIGINS` if you run the frontend from a different origin.

## 📖 API Documentation

Once the backend is running, visit:

- API Docs: <http://localhost:8000/docs> (Swagger UI)
- Alternative Docs: <http://localhost:8000/redoc>
- OpenAPI Schema: <http://localhost:8000/openapi.json>

### Key Endpoints

- `GET /health` - Health check
- `POST /login` - User authentication
- `GET /api/trade/*` - Trading operations
- `GET /api/ai/*` - AI/ML operations
- `WebSocket /socket.io/*` - Real-time updates

## 🏗️ Architecture

```text
InfinityAI.Pro/
├── engine/                 # Core application logic
│   └── app/
│       ├── main.py        # FastAPI application
│       └── routes/        # API route handlers
├── core/                   # Business logic
│   ├── models.py          # Database models
│   ├── usermanager.py     # User management
│   └── broker/            # Trading broker integrations
├── dashboard/             # React frontend
├── shared/                # Shared utilities
├── config/                # Configuration files
└── infra/                 # Infrastructure as Code

```text


## 🚀 Deployment

### Production Deployment (Azure)

The application supports multiple deployment strategies:

#### 1. Azure Web App (Container) + ACR

- CI builds and pushes image to ACR: `infinityaiprodacr.azurecr.io/infinityai-backend:latest`
- Deployment config points App Service `infinityai-backend-app` to that image.
- Health check path: `/health`

Optional helper script:
- `scripts/update_appservice_container.ps1` (sets ACR pull, image, and health path)

```bash
# Using Azure Developer CLI
azd up

# Or using deployment scripts
./deploy-azure-enhanced.ps1

### 2. Podman (Preferred for local)

```bash
podman-compose -f podman-compose.yaml up --build
```

### 3. Docker (Alternate)

```bash
docker-compose up --build

```text


<!-- Vercel deployment removed: using Azure Static Web Apps -->

### Environment Configuration

Create `.env` files in the following locations:

- `config/.env` - Backend configuration
- `dashboard/.env` - Frontend configuration

Example `config/.env`:


```env
DATABASE_URL=mysql+pymysql://user:password@host:port/database
SECRET_KEY=your-secret-key-here
TESTING=0
```text

Example `dashboard/.env`:

```env
REACT_APP_API_URL=https://www.infinityai.pro
```text

## 🔧 Configuration

### Database Configuration

The application supports multiple database backends:

- **SQLite** (Development): Automatic setup with `TESTING=1`
- **MySQL**: Production-ready with connection pooling
- **PostgreSQL**: Enterprise-grade database support

### AI/ML Configuration

Configure MLflow tracking server:
```env
MLFLOW_TRACKING_URI=http://localhost:5000

```text

### Trading API Configuration

Set up Dhan API credentials:
```env
DHAN_CLIENT_ID=your-client-id
DHAN_ACCESS_TOKEN=your-access-token
### Custom Domain

- Frontend (Azure Static Web Apps): add your domain (e.g., `www.infinityai.pro`), validate DNS TXT, and set CNAME.
- Backend (Azure Web App): add custom domain, upload/enable certificate, and ensure CORS allows your domain(s) via `CORS_ALLOW_ORIGINS`.

```

## 🧪 Testing

```bash
# Run backend tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=.

# Run frontend tests
cd dashboard
npm test
```

## 📊 Monitoring & Logging

- **Health Checks**: `/health` endpoint for container orchestration
- **Logging**: Structured logging with configurable levels
- **Metrics**: Integration with Azure Application Insights
- **MLflow**: Experiment tracking and model versioning

## 🔒 Security

- JWT-based authentication
- Password hashing with bcrypt
- Azure Key Vault integration for secrets
- CORS configuration for cross-origin requests
- Input validation and sanitization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/raghu-1718/InfinityAI/issues)
- **Documentation**: [Wiki](https://github.com/raghu-1718/InfinityAI/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/raghu-1718/InfinityAI/discussions)

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://reactjs.org/) - Frontend framework
- [MLflow](https://mlflow.org/) - ML lifecycle management
- [Dhan API](https://dhan.co/) - Trading API
- [Azure](https://azure.microsoft.com/) - Cloud platform

---

**InfinityAI.Pro** - Where AI meets Trading Intelligence 🚀</content>
```
