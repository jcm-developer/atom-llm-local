# 🤖 Atom LLM Local

Intelligent chat system with advanced document generation and data visualization capabilities.

## ✨ Key Features

- 💬 **Intelligent Chat**: Conversational interface with local AI and ChatGPT
- 📊 **Chart Generation**: Automatically creates data visualizations (bar, line, pie, scatter)
- 📄 **PDF Generation**: Generates professionally formatted PDF documents
- 🔄 **Model Switching**: Toggle between private local model and ChatGPT
- 🎨 **Modern Interface**: Elegant design with glass effects and gradients
- 🖼️ **Image Visualization**: Full-screen preview with interactive modal

## 📂 Project Structure

```
atom-llm-local/
├── backend/              # Backend API (FastAPI + Python)
│   ├── main.py          # Main server with endpoints
│   ├── tools/           # Generation tools
│   │   ├── generate_pdf.py      # PDF generator
│   │   └── generate_chart.py    # Chart generator
│   ├── files/           # Generated files (PDFs, images)
│   ├── requirements.txt # Python dependencies
│   └── Dockerfile       # Backend Docker image
├── frontend/            # Frontend (Vue.js + Vite)
│   ├── src/
│   │   ├── views/       # Main views
│   │   ├── components/  # Vue components
│   │   └── style.css    # Global styles
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml   # Service orchestration
└── .env                # Environment variables

```

## 📋 Requirements

- 🐳 **Docker** and **Docker Compose** (recommended)
- 📦 **Node.js** v20+ and npm (for local development)
- 🐍 **Python** 3.9+ (for backend local development)
- 🌐 **Anything LLM** (gateway to local model)
- 🖥️ **LM Studio** (local inference server)

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/jcm-developer/atom-llm-local.git
cd atom-llm-local
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
# API Keys
OPENAI_API_KEY=your_openai_api_key
ANYTHING_LLM_API_KEY=your_anything_llm_api_key

# URLs
ANYTHING_LLM_URL=http://localhost:3001
```

### 3. Start with Docker (Recommended)

```bash
# Start the backend
docker-compose up -d backend

# Verify it's running
docker logs backend

# Backend will be available at http://localhost:8000
```

### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev

# El frontend estará disponible en http://localhost:5173
```

## 🔄 Flujo de Trabajo

```
Usuario → Frontend (Vue.js) → Backend (FastAPI) → Anything LLM → LM Studio
                    ↓
              Generación de PDFs
              Generación de Gráficas
```

### Arquitectura de Servicios

1. **Frontend (Puerto 5173)**: Interfaz de usuario en Vue.js
2. **Backend (Puerto 8000)**: API REST con FastAPI
3. **Anything LLM (Puerto 3001)**: Gateway hacia el modelo local
4. **LM Studio**: Model inference server

## 🎯 Detailed Features

### 1. 💬 Intelligent Chat

**Features:**
- Natural conversation with AI
- Conversation history
- Markdown format in responses
- Animated typing indicator

**Usage:**
```
User: "Tell me about AI"
Bot: [Model response...]
```

### 2. 📊 Generación de Gráficas

**Tipos de gráficas disponibles:**
- 📊 **Barras**: Comparaciones entre categorías
- 📈 **Líneas**: Evolución temporal
- 🥧 **Circular**: Distribución porcentual
- 📍 **Dispersión**: Correlaciones de datos

**Comandos:**
```
"Genera una gráfica de barras de los ingresos por año"
"Crea un gráfico circular de las ventas por producto"
"Muestra una gráfica de líneas de la evolución mensual"
```

**Formato de datos:**
El modelo debe responder con JSON:
```json
{
  "2020": 50000000,
  "2021": 55000000,
  "2022": 60000000,
  "2023": 58000000
}
```

**Features:**
- ✅ Inline visualization in chat
- ✅ Click to enlarge in modal
- ✅ Styled download button
- ✅ High resolution (300 DPI)
- ✅ Professional styles with matplotlib

### 3. 📄 PDF Generation

**Commands:**
```
"Generate a PDF about climate change"
"Create a PDF document of the annual report"
```

**Features:**
- ✅ Professional format with margins
- ✅ Standard A4 size
- ✅ Readable fonts (11pt)
- ✅ Automatic justification
- ✅ Styled download button

**Chat message:**
```
Here is your PDF
[📥 Download PDF]
```

### 4. 🔄 Model Switching

**Available models:**

| Model | Icon | Description | Functions |
|-------|------|-------------|-----------|
| **Local** 💻 | `computer` | Private model (LM Studio) | Chat + PDFs + Charts |
| **ChatGPT** ☁️ | `cloud` | OpenAI API | Chat only |

**How to switch:**
1. Click the toggle button (input corner)
2. **Blue** icon = ChatGPT active
3. **Gray** icon = Local model active

## 🎨 User Interface

### Visual Elements

**Download Buttons:**
- Blue-purple gradient (#1d7efd → #8f6fff)
- Material Icons icon
- Hover effect with elevation
- Soft shadows

**Image Modal:**
- Transparent black background (90%)
- Click outside to close
- Smooth animations (fadeIn/zoomIn)
- Responsive centered image

**Theme:**
- Dark mode by default
- Glass effects (backdrop-filter)
- Consistent colors
- Poppins typography

## 🛠️ Useful Commands

### Backend (Docker)

```bash
# Start backend
docker-compose up -d backend

# View logs in real-time
docker logs -f backend

# Stop backend
docker-compose down

# Rebuild after changes
docker-compose up -d --build backend

# Restart backend
docker-compose restart backend
```

### Frontend

```bash
# Install dependencies
npm install

# Development with hot-reload
npm run dev

# Build for production
npm run build

# Preview build
npm run preview
```

### Python (Local Development)

```bash
# Activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r backend/requirements.txt

# Run server
cd backend
python main.py
```

## 🌍 Environment Variables

### Backend (.env in root)

```env
# OpenAI API
OPENAI_API_KEY=sk-...                          # OpenAI API key

# Anything LLM
ANYTHING_LLM_URL=http://localhost:3001         # Gateway URL
ANYTHING_LLM_API_KEY=ABC123...                 # Anything LLM API key
```

### Frontend (frontend/.env)

```env
# Only needed if using ChatGPT
VITE_OPENAI_API_KEY=sk-...
```

**Note:** `VITE_*` variables are injected at build time. If you change these variables, you need to rebuild the frontend.

## 📡 API Endpoints

### Backend (Port 8000)

#### POST `/api/chat`
Main endpoint for chat and content generation.

**Request:**
```json
{
  "message": "Generate a sales chart",
  "isUsingChatGPT": false
}
```

**Response (Text):**
```json
{
  "type": "text",
  "response": "Here is the information..."
}
```

**Response (Image):**
```json
{
  "type": "image",
  "filename": "chart_bar_sales_1234567890.png",
  "imageData": "data:image/png;base64,...",
  "url": "http://localhost:8000/files/chart_bar_sales_1234567890.png",
  "message": "Bar chart generated successfully"
}
```

**Response (PDF):**
```json
{
  "type": "file",
  "filename": "document_report_1234567890.pdf",
  "url": "http://localhost:8000/files/document_report_1234567890.pdf",
  "message": "PDF generated successfully"
}
```

#### GET `/files/{filename}`
Download generated files (PDFs or images).

**Response:**
- Content-Type: `application/pdf` or `image/png`
- Content-Disposition: `attachment; filename={filename}`

## 🔍 Command Detection

### Chart Generation

**Keywords:**
- Action: `generar`, `genera`, `crear`, `crea`, `generate`, `create`
- Object: `gráfica`, `grafica`, `gráfico`, `grafico`, `chart`

**Detected types:**
- `línea`, `linea`, `line` → Line chart
- `circular`, `pie`, `pastel` → Pie chart
- `dispersión`, `dispersion`, `scatter` → Scatter plot
- Default → Bar chart

**Examples:**
```
✅ "Generate a chart of revenue"
✅ "Create a pie chart of sales"
✅ "Show a line chart of monthly data"
```

### PDF Generation

**Keywords:**
- Action: `generar`, `genera`, `generate`
- Object: `pdf`

**Example:**
```
✅ "Generate a PDF about the topic"
✅ "Generate a PDF document of the report"
```

## 🐛 Troubleshooting

### Error: "Failed to fetch"

**Cause:** Backend is not running.

**Solution:**
```bash
docker-compose up -d backend
docker logs backend  # Verify it's running
```

### Error: "Python not found"

**Cause:** Trying to run backend without Docker.

**Solution:**
```bash
# Use Docker (recommended)
docker-compose up -d backend

# Or install Python and dependencies
pip install -r backend/requirements.txt
```

### Chart not generating correctly

**Cause:** Model is not responding in JSON format.

**Solution:**
- Verify the model responds with `{"key": value}`
- Check backend logs: `docker logs -f backend`
- Example of correct response:
  ```json
  {"2020": 50000, "2021": 55000, "2022": 60000}
  ```

### PDF downloads automatically

**Cause:** Old code version.

**Solution:**
- Update repository: `git pull`
- Rebuild backend: `docker-compose up -d --build backend`

### Image not showing in chat

**Cause:** Response type is not `"image"`.

**Solution:**
- Check backend response in browser console
- Should be `data.type === 'image'` with `data.imageData`

## 📦 Main Dependencies

### Backend (Python)

```txt
fastapi==0.104.1        # Web framework
uvicorn==0.24.0        # ASGI server
python-dotenv==1.0.0   # Environment variables
requests==2.31.0       # HTTP client
reportlab==4.0.7       # PDF generation
matplotlib==3.8.2      # Chart generation
pandas==2.1.4          # Data processing
mcp==1.0.0             # Model Context Protocol
```

### Frontend (Node.js)

```json
{
  "vue": "^3.4.0",
  "vite": "^5.0.0"
}
```

## 🚀 Roadmap

- [ ] Support for more chart types (histograms, box plots)
- [ ] Export charts in multiple formats (SVG, JPG)
- [ ] PDF editor with customizable templates
- [ ] Persistent conversation history
- [ ] Configurable dark/light mode
- [ ] Internationalization (i18n)
- [ ] Unit and integration tests

## 📝 License

This project is licensed under the license specified in the `LICENSE` file.

## 👨‍💻 Author

**JCM Developer**
- GitHub: [@jcm-developer](https://github.com/jcm-developer)

## 🤝 Contributing

Contributions are welcome. Please:

1. Fork the project
2. Create a branch for your feature (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

If you encounter any issues or have questions:
- Open an [Issue](https://github.com/jcm-developer/atom-llm-local/issues)
- Check the [Troubleshooting](#-troubleshooting) section

---

⭐ If this project has been useful to you, consider giving it a star on GitHub!
