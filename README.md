# Gym AI Voice Agent Backend

This is the backend API for the Gym AI Voice Agent system, designed to help gyms manage leads, calls, and AI voice agent interactions.

## Project Structure

The project is organized as a modular monolith with the following components:

- **Authentication Service**: JWT-based authentication
- **Lead Management Service**: Managing potential gym members
- **Call Management Service**: Managing AI voice agent calls
- **Analytics Service**: Reporting and statistics
- **Settings Service**: System configuration
- **AI Voice Agent Service**: Integration with AI telephony providers

## Setup and Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up environment variables (create a `.env` file)
5. Run the server:
   ```
   uvicorn main:app --reload
   ```

## API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

This project uses FastAPI, SQLAlchemy, and Pydantic for API development.

## License

[MIT License](LICENSE) # reps-ai-dashboard-backend
TESTING THE AUTO DEPLOY FUNCTIONALITY

## Celery Background Tasks

The project uses Celery for handling background and scheduled tasks, with Redis as the message broker.

### Architecture

- **Celery App Factory**: Configured in `backend/celery_app.py` with settings from `backend/config/celery_settings.py`
- **Task Organization**: Tasks are organized by domain in separate modules:
  - `backend/tasks/lead/`: Lead qualification and processing
  - `backend/tasks/reports/`: Report generation
  - `backend/tasks/notifications/`: Email and other notifications
- **Base Task Class**: Common functionality in `backend/tasks/base.py`
- **Services**: Each task uses a corresponding service class for business logic

### Running Celery Workers

Run a worker for lead tasks:
```bash
./start_celery_worker.sh lead_tasks
```

Run a worker for report and notification tasks:
```bash
./start_celery_worker.sh reports_tasks,notification_tasks
```

### Running Celery Beat

To start the scheduler for periodic tasks:
```bash
./start_celery_beat.sh
```

### Docker Compose

The provided docker-compose.yml includes:
- Redis as message broker and result backend
- API service
- Lead worker
- Reports and notifications worker
- Beat scheduler

Start all services with:
```bash
docker-compose up -d
```
