#!/bin/bash

# Build the Docker image
docker build -t reps-ai-backend:latest -f Dockerfile .

# Run the Docker container
docker run -d --name reps-ai-backend -p 8000:8000 reps-ai-backend:latest 