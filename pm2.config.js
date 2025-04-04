module.exports = {
    apps: [
      {
        name: 'fastapi-app',
        script: '/Users/home/reps-ai-backend/reps-ai-dashboard-backend/venv/bin/uvicorn',
        args: [
          'main:app',
          '--reload',
          '--host', '0.0.0.0',
          '--port', '8000'
        ],
        cwd: '/Users/home/reps-ai-backend/reps-ai-dashboard-backend',
        interpreter: 'none'
      }
    ]
  };
  