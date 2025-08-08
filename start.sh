#!/bin/bash

echo "🚀 Starting Credit Approval System..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build and start the application
echo "📦 Building and starting containers..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check if the web service is running
if docker-compose ps | grep -q "web.*Up"; then
    echo "✅ Application is running!"
    echo "🌐 API: http://localhost:8000/api/"
    echo "🔧 Admin: http://localhost:8000/admin/"
    echo ""
    echo "📊 To ingest data, run:"
    echo "   docker-compose exec web python manage.py ingest_data"
    echo ""
    echo "🧪 To test the API, run:"
    echo "   python test_api.py"
    echo ""
    echo "📋 To view logs, run:"
    echo "   docker-compose logs -f"
else
    echo "❌ Application failed to start. Check logs with:"
    echo "   docker-compose logs"
    exit 1
fi 