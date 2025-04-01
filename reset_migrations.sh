# Reset the database migration history
alembic stamp base

# Create a new migration with your changes
alembic revision --autogenerate -m "reset migrations with user id as UUID"
