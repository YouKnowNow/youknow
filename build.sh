#!/bin/bash

echo "Building frontend..."
cd frontend
npm run build
cd ..

echo "Frontend build complete! The Flask app will now serve the built React app."
echo "Run 'docker-compose up' to start the application."
