#!/bin/bash
# startup.sh - Azure App Service startup script for GraphRAG Chatbot

echo "🚀 Starting Nestlé AI Chatbot GraphRAG deployment..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating required directories..."
mkdir -p logs

# Set proper permissions
echo "🔒 Setting permissions..."
chmod +x app.py

# Test Neo4j connection
echo "🔌 Testing Neo4j connection..."
python -c "
from backend.neo4j_connection import neo4j_conn
if neo4j_conn.connect():
    print('✅ Neo4j connection successful')
else:
    print('❌ Neo4j connection failed')
    exit(1)
"

# Test OpenAI configuration
echo "🤖 Testing OpenAI configuration..."
python -c "
import os
from openai import OpenAI
api_key = os.getenv('OPENAI_API_KEY')
if api_key and api_key.startswith('sk-'):
    try:
        client = OpenAI(api_key=api_key)
        print('✅ OpenAI configuration successful')
    except Exception as e:
        print(f'⚠️ OpenAI configuration issue: {e}')
else:
    print('❌ OpenAI API key not configured')
"

# Initialize Neo4j data if needed
echo "📊 Checking Neo4j data initialization..."
python -c "
from backend.neo4j_connection import neo4j_conn
from backend.neo4j_data_initializer import data_initializer

try:
    with neo4j_conn.get_session() as session:
        result = session.run('MATCH (n) RETURN count(n) as count')
        count = result.single()['count']
        
        if count == 0:
            print('📊 No data found, initializing...')
            data_initializer.initialize_data()
        else:
            print(f'✅ Found {count} nodes in Neo4j')
except Exception as e:
    print(f'❌ Data initialization error: {e}')
"

# Start the application
echo "🌐 Starting FastAPI application..."
if [ "$ENVIRONMENT" = "development" ]; then
    echo "🔧 Running in development mode..."
    uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000} --reload
else
    echo "🚀 Running in production mode..."
    gunicorn app:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000} --timeout 120 --access-logfile - --error-logfile -
fi