# Government Services Assistant - Prototype

An AI-powered conversational agent that provides citizens with step-by-step guidance for navigating government services.

## Architecture

- **Backend**: FastAPI (Python) - REST API with async support
- **Frontend**: Next.js (React) - Server-side rendered web application
- **Database**: PostgreSQL - Relational data storage
- **Cache**: Redis - Session management and caching
- **Containerization**: Docker Compose - Orchestrated deployment

## Features (Prototype)

✅ Chat interface for government service guidance
✅ Service information retrieval (Aadhaar name change example)
✅ Document upload capability
✅ Dashboard for user data
✅ RESTful API with OpenAPI documentation
✅ Docker Compose setup for easy deployment

## Prerequisites

- Docker and Docker Compose installed
- (Optional) Google Gemini API key for AI features

## Quick Start

1. **Clone and setup environment**

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your configuration (optional for prototype)
# The prototype works with default values
```

2. **Start the application**

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

3. **Access the application**

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## Services

### Backend (FastAPI)
- Port: 8000
- Auto-reload enabled for development
- OpenAPI docs at `/docs`
- Health check at `/health`

### Frontend (Next.js)
- Port: 3000
- Hot reload enabled
- Chat interface for user interaction

### PostgreSQL
- Port: 5432
- Database: govt_services
- Initialized with sample schema

### Redis
- Port: 6379
- Used for session management

## API Endpoints

### Services
- `GET /api/v1/services` - List all services
- `GET /api/v1/services/{service_id}` - Get service details

### Chat
- `POST /api/v1/chat` - Send chat message
- `GET /api/v1/chat/history` - Get conversation history

### Documents
- `POST /api/v1/documents/upload` - Upload document
- `GET /api/v1/documents` - List documents
- `GET /api/v1/documents/{doc_id}` - Get document
- `DELETE /api/v1/documents/{doc_id}` - Delete document

### Dashboard
- `GET /api/v1/dashboard` - Get dashboard data

## Development

### Backend Development

```bash
# Access backend container
docker-compose exec backend bash

# Run tests (when implemented)
pytest

# Check logs
docker-compose logs -f backend
```

### Frontend Development

```bash
# Access frontend container
docker-compose exec frontend sh

# Check logs
docker-compose logs -f frontend
```

### Database Access

```bash
# Access PostgreSQL
docker-compose exec postgres psql -U govt_user -d govt_services

# View tables
\dt

# Query services
SELECT * FROM services;
```

## Stopping the Application

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clears database)
docker-compose down -v
```

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   ├── core/            # Configuration
│   │   └── models/          # Data models
│   ├── db/                  # Database initialization
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── pages/               # Next.js pages
│   ├── styles/              # CSS styles
│   ├── Dockerfile
│   ├── package.json
│   └── tsconfig.json
├── docker-compose.yml
├── .env.example
└── README.md
```

## Next Steps for Full Implementation

1. **AI Integration**: Connect Google Gemini API for intelligent responses
2. **Authentication**: Implement JWT-based user authentication
3. **Database Models**: Create SQLAlchemy models and migrations
4. **Session Management**: Implement Redis-based session storage
5. **Document Storage**: Add encrypted document storage
6. **Multi-language Support**: Implement translation service
7. **Testing**: Add unit and integration tests
8. **Browser Automation**: Implement Playwright-based automation
9. **Browser Extension**: Create Chrome/Firefox extension
10. **Production Setup**: Add nginx, SSL, monitoring

## Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
lsof -i :3000  # or :8000, :5432, :6379

# Stop the process or change ports in docker-compose.yml
```

### Database Connection Issues
```bash
# Restart PostgreSQL service
docker-compose restart postgres

# Check PostgreSQL logs
docker-compose logs postgres
```

### Frontend Not Loading
```bash
# Rebuild frontend
docker-compose up -d --build frontend

# Check if backend is accessible
curl http://localhost:8000/health
```

## License

This is a prototype for demonstration purposes.

## Support

For issues and questions, please refer to the design document.
