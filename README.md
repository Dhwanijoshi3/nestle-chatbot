# 🏠 Nestlé AI Chatbot - Made with Nestlé Canada

An intelligent AI-powered chatbot specifically designed for the Made with Nestlé Canada website. Features GraphRAG technology, real-time web scraping, and comprehensive product knowledge.

![Nestlé Chatbot](https://img.shields.io/badge/Nestlé-Chatbot-8B4513?style=for-the-badge&logo=nestlé)
![FastAPI](https://img.shields.io/badge/FastAPI-0.108.0-009688?style=flat-square&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)
![Azure](https://img.shields.io/badge/Azure-Deployed-0078d4?style=flat-square&logo=microsoft-azure)

## 🌟 Features

- **🤖 AI-Powered Responses** - GPT-based conversational AI with Nestlé-specific knowledge
- **🧠 GraphRAG Technology** - Knowledge graph-based retrieval for contextual responses
- **🌐 Real-time Web Scraping** - Dynamic content fetching from madewithnestle.ca
- **🎨 Beautiful UI** - Modern, responsive chatbot interface
- **☁️ Cloud Deployment** - Ready for Azure App Service deployment
- **📱 Mobile Responsive** - Works seamlessly on all devices

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API key
- Git

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/nestle-ai-chatbot.git
   cd nestle-ai-chatbot
   ```

2. **Set up virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

6. **Access the chatbot:**
   Open http://localhost:8000 in your browser

## 📁 Project Structure

```
nestle-ai-chatbot/
├── 📄 app.py                 # Main FastAPI application
├── 📄 requirements.txt       # Python dependencies
├── 📄 .env.example          # Environment variables template
├── 📄 startup.sh            # Azure deployment script
├── 📄 README.md             # This file
├── 📁 backend/              # Backend modules
│   ├── 📄 __init__.py
│   ├── 📄 openai_interface.py    # OpenAI integration
│   ├── 📄 retriever.py           # Graph retrieval logic
│   ├── 📄 web_scraper.py         # Web scraping functionality
│   └── 📄 graph_builder.py       # Knowledge graph construction
├── 📁 frontend/             # Frontend files
│   ├── 📄 index.html        # Main HTML template
│   ├── 📄 style.css         # Chatbot styling
│   └── 📄 script.js         # Interactive functionality
└── 📁 graph/               # Knowledge graph storage
    └── 📄 graph.pkl        # Pickled NetworkX graph
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file from `.env.example`:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
ENVIRONMENT=development
PORT=8000
DEBUG=True
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
MAX_SEARCH_RESULTS=5
```

### OpenAI API Key Setup

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Go to API Keys section
4. Create a new API key
5. Add it to your `.env` file

## 🌐 Deployment

### Azure App Service Deployment

1. **Create Azure Resources:**
   ```bash
   # Create Resource Group
   az group create --name nestle-chatbot-rg --location "East US"
   
   # Create App Service Plan
   az appservice plan create --name nestle-chatbot-plan --resource-group nestle-chatbot-rg --sku B1 --is-linux
   
   # Create Web App
   az webapp create --resource-group nestle-chatbot-rg --plan nestle-chatbot-plan --name nestle-chatbot-app --runtime "PYTHON|3.11"
   ```

2. **Configure Deployment:**
   ```bash
   # Set up GitHub deployment
   az webapp deployment source config --name nestle-chatbot-app --resource-group nestle-chatbot-rg --repo-url https://github.com/YOUR_USERNAME/nestle-ai-chatbot --branch main --manual-integration
   ```

3. **Set Environment Variables:**
   ```bash
   # Add OpenAI API key
   az webapp config appsettings set --resource-group nestle-chatbot-rg --name nestle-chatbot-app --settings OPENAI_API_KEY="your_api_key_here"
   
   # Add other settings
   az webapp config appsettings set --resource-group nestle-chatbot-rg --name nestle-chatbot-app --settings ENVIRONMENT="production" PORT="8000"
   ```

### Manual Deployment Steps

1. **GitHub Setup:**
   - Create new repository: `nestle-ai-chatbot`
   - Push your code to the repository

2. **Azure Portal Setup:**
   - Create App Service with Python 3.11
   - Connect to GitHub repository
   - Add environment variables in Configuration

3. **Testing:**
   - Access your app at `https://your-app-name.azurewebsites.net`

## 📖 API Documentation

### Endpoints

- **GET /** - Main chatbot interface
- **POST /chat** - Send message to chatbot
- **GET /health** - Health check endpoint

### Chat API Usage

```javascript
// Send message to chatbot
const response = await fetch('/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ question: "Tell me about KitKat" })
});

const data = await response.json();
console.log(data.answer);      // AI response
console.log(data.sources);     // Reference URLs
```

## 🧠 Knowledge Graph

The chatbot uses a comprehensive knowledge graph containing:

- **50+ Nestlé entities** (brands, products, concepts)
- **Semantic relationships** between entities
- **Rich descriptions** for contextual understanding
- **Dynamic expansion** capabilities

### Graph Management

```python
# Build new graph
from backend.graph_builder import build_graph
build_graph()

# Add new node
from backend.graph_builder import add_node_to_graph
add_node_to_graph("New Product", "Description", [("Nestlé Canada", "produces")])

# View graph info
from backend.graph_builder import view_graph_info
view_graph_info()
```

## 🛠️ Technologies Used

- **Backend:** FastAPI, Python 3.11+
- **AI/ML:** OpenAI GPT, Sentence Transformers, NetworkX
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Deployment:** Azure App Service
- **Data:** FAISS, BeautifulSoup, Requests

## 📊 Performance & Monitoring

### Health Monitoring

The application includes built-in health checks:

```bash
# Check application health
curl https://your-app.azurewebsites.net/health
```

Response:
```json
{
  "status": "healthy",
  "graph_loaded": true,
  "nodes_count": 45,
  "environment": "production"
}
```

### Performance Optimization

- **Caching:** Graph embeddings cached in memory
- **Async Processing:** Non-blocking web scraping
- **Error Handling:** Graceful fallbacks for all components
- **Resource Management:** Efficient memory usage

## 🔍 Troubleshooting

### Common Issues

1. **Graph Not Loading:**
   ```bash
   # Rebuild the graph
   python -c "from backend.graph_builder import build_graph; build_graph()"
   ```

2. **OpenAI API Errors:**
   - Verify API key in environment variables
   - Check API usage limits
   - Ensure proper network connectivity

3. **Web Scraping Issues:**
   - Check internet connectivity
   - Verify target websites are accessible
   - Review rate limiting settings

### Debug Mode

Enable debug logging:
```bash
export DEBUG=True
python app.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `