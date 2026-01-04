# Docker Setup for Collab Commerce

This project has been dockerized with Docker and Docker Compose.

## Quick Answer to Your Question

**Do NOT delete your virtual environment (`env/`) folder!**

- You can keep it for **local development** outside Docker
- It is **automatically excluded** from Docker builds via `.dockerignore`
- Docker containers don't need virtual environments (they provide isolation)

## Prerequisites

- Docker Desktop installed and running
- Docker Compose installed

## Running with Docker

1. **Build and start all services:**
   ```bash
   docker-compose up --build
   ```

2. **Run in detached mode (background):**
   ```bash
   docker-compose up -d
   ```

3. **Stop services:**
   ```bash
   docker-compose down
   ```

4. **View logs:**
   ```bash
   docker-compose logs -f web
   ```

## Services

- **web**: Django application running on Daphne (port 8000)
- **redis**: Redis server for Channels/WebSocket support (port 6379)

## First Time Setup

If running for the first time, you may need to run migrations:

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## Environment Variables

Create a `.env` file in the root directory if you need to override settings:

```env
REDIS_HOST=redis
REDIS_PORT=6379
DJANGO_SETTINGS_MODULE=collab_commerce.settings
SECRET_KEY=your-secret-key
DEBUG=True
```

## Local Development vs Docker

- **Local Development**: Activate `env` virtual environment and run `python manage.py runserver`
- **Docker**: Use `docker-compose up` - no virtual environment needed

## Notes

- The `env/` folder is excluded from Docker builds via `.dockerignore`
- Redis connection automatically uses the `redis` service name in Docker
- Media and static files are persisted in Docker volumes

