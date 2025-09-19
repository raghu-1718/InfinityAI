# InfinityAI.Pro Usage Guide

## Quick Start (Local Development)

### Backend
```bash
# Install dependencies
pip install -r requirements.txt

# Start backend (SQLite dev mode with CORS)
./scripts/dev_backend.sh
```
- Backend runs on http://localhost:8000
- Health check: http://localhost:8000/health
- API docs: http://localhost:8000/docs

### Frontend
```bash
# Start React dashboard (auto-switches to Node 18)
./scripts/dev_frontend.sh
```
- Frontend runs on http://localhost:3000
- Automatically points to local backend at http://localhost:8000

## Production URLs

- **Backend API**: https://www.infinityai.pro
- **Frontend**: Azure Static Web Apps (infinityai-frontend)
- **Health Check**: https://www.infinityai.pro/health
- **API Documentation**: https://www.infinityai.pro/docs

## Key Features

### Trading API
- Real-time market data via Dhan API integration
- Automated trading signals and execution
- Portfolio management and risk assessment
- Trade logging and analytics

### AI/ML Components
- MLflow model management
- Predictive trading models
- Market sentiment analysis
- Performance monitoring and drift detection

### Authentication
- JWT-based authentication system
- Role-based access control (RBAC)
- Secure password hashing with bcrypt

## API Endpoints

### Core Endpoints
- `GET /` - API information and links
- `GET /health` - Health check and database status
- `GET /docs` - Interactive API documentation
- `POST /login` - User authentication

### Trading Endpoints
- `GET /trading/signals` - Get trading signals
- `POST /trading/execute-order` - Execute trading orders
- `GET /trading/recent-trades/{user_id}` - Get recent trades
- `POST /trading/auto-trading` - Toggle auto-trading

### AI/ML Endpoints
- `GET /api/ai/models` - List available models
- `POST /api/ai/train` - Train models
- `POST /api/ai/predict` - Generate predictions
- `GET /api/ai/models/leaderboard` - Model performance ranking

## Environment Configuration

### Required Secrets (GitHub/Azure)
- `AZURE_CREDENTIALS` - Azure service principal for deployment
- `DATABASE_URL` - Production database connection string
- `CORS_ALLOW_ORIGINS` - Allowed origins for CORS (defaults to https://www.infinityai.pro)

### Optional Environment Variables
- `TESTING=1` - Use SQLite for local development
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` - Database credentials
- `DHAN_CLIENT_ID`, `DHAN_ACCESS_TOKEN` - Trading API credentials
- `SECRET_KEY` - JWT signing key

## Deployment Architecture

### Backend (Azure App Service)
- **Service**: infinityai-backend-app
- **Container**: infinityaiprodacr.azurecr.io/infinityai-backend:latest
- **Resource Group**: InfinityAI-Prod-RG-West
- **Health Path**: `/health`
- **Port**: 8000

### Frontend (Azure Static Web Apps)
- **Service**: infinityai-frontend
- **Build**: Node.js 18, React production build
- **Deploy**: Automatic on push to main (dashboard/ folder)

### Database
- **Service**: infinityai-prod-db (Azure Database for MySQL Flexible Server)
- **Migrations**: Automated via Alembic in CI/CD pipeline

## Monitoring & Logging

### Application Insights
- **Backend**: infinityai-backend-app-insights
- **Structured JSON logging** with correlation IDs
- **Health monitoring** and alerting
- **Performance metrics** and telemetry

### Log Analytics
- **Workspace**: managed-infinityai-backend-app-insights-ws
- **Query capabilities** for debugging and analysis

## Security Features

- **JWT Authentication** with configurable expiration
- **Password Hashing** using bcrypt
- **CORS Protection** with domain allowlisting
- **Azure Key Vault** integration for secrets management
- **Managed Identity** for secure Azure resource access

## Development Workflow

1. **Local Development**
   - Backend: SQLite database (TESTING=1)
   - Frontend: Node 18 with hot reload
   - CORS enabled for localhost:3000

2. **CI/CD Pipeline**
   - Tests run with SQLite (fast, isolated)
   - Docker image built and pushed to ACR
   - Deployed to Azure App Service
   - Database migrations run automatically
   - App settings configured post-deployment

3. **Production Monitoring**
   - Health checks every 30 seconds
   - Application Insights telemetry
   - Automated scaling based on demand

## Troubleshooting

### Common Issues

**Frontend won't install (EBADENGINE)**
- Ensure Node 18 is active: `nvm use 18`
- Or use the provided script: `./scripts/dev_frontend.sh`

**Backend connection errors**
- Check `TESTING=1` is set for local development
- Verify database credentials for production
- Confirm CORS_ALLOW_ORIGINS includes your frontend domain

**Deployment failures**
- Verify GitHub secrets are configured
- Check Azure resource names match configuration
- Ensure App Service has AcrPull permission

### Health Check URLs
- **Local**: http://localhost:8000/health
- **Production**: https://www.infinityai.pro/health

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-09-19T...",
  "version": "1.0.0",
  "service": "infinityai-backend-app"
}
```

## Support

For issues or questions:
- Check the [Deployment Alignment](DEPLOYMENT_ALIGNMENT.md) documentation
- Review CI/CD logs in GitHub Actions
- Monitor Application Insights for runtime issues