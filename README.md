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
