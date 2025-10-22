import os
import re
import json
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from mcp.server import Server
import mcp.types as types
import logging
from pathlib import Path
from tools.generate_pdf import generate_pdf

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANYTHING_LLM_URL = os.getenv("ANYTHING_LLM_URL")
ANYTHING_LLM_API_KEY = os.getenv("ANYTHING_LLM_API_KEY")

# MCP Server and FastAPI app
mcp_server = Server("atom-llm-server")
app = FastAPI(title="Atom LLM Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Files configuration
FILES_DIR = Path("files")
FILES_DIR.mkdir(exist_ok=True)

# Chat endpoint
@app.post("/api/chat")
async def chat_router(request: Request):
    """
    Receives a message from the frontend and routes it to the appropriate model.
    If the message contains keywords like 'generar' and 'pdf', it triggers a local tool.

    Args:
        request (Request): The incoming request containing the message and model choice.

    Returns:
        dict: A response dictionary containing either text or file information.
    """
    logger.info("📨 Nueva petición recibida en /api/chat")

    body = await request.json()
    user_message = body.get("message", "")
    is_using_chatgpt = body.get("isUsingChatGPT", False)

    logger.info(f"💬 Mensaje del usuario: {user_message[:100]}...")
    logger.info(f"🤖 Usando ChatGPT: {is_using_chatgpt}")

    try:
        logger.info("🔍 Verificando si es una petición de generación de PDF...")
        should_generate_pdf = (
            ("generar" in user_message.lower() or "genera" in user_message.lower()) 
            and "pdf" in user_message.lower()
            and not is_using_chatgpt
        )
        
        if should_generate_pdf:
            logger.info("🧾 ¡Acción detectada: generación de PDF con modelo local!")
            logger.info("📝 Obteniendo contenido del modelo local primero...")
            
            logger.info(f"🏠 Llamando a modelo local para generar contenido...")
            response = requests.post(
                f"{ANYTHING_LLM_URL}/api/v1/workspace/rag/chat",
                headers={
                    "Authorization": f"Bearer {ANYTHING_LLM_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={"message": user_message, "rules": "Answer always in the user language"},
                timeout=60,
            )
            data = response.json()
            text_response = data.get("textResponse", "").replace("**", "").strip()
            
            logger.info(f"📄 Contenido generado ({len(text_response)} caracteres)")
            
            import time
            timestamp = int(time.time())
            topic = user_message.lower().replace("genera", "").replace("generar", "").replace("pdf", "").replace("un", "").replace("de", "").strip()
            topic_slug = re.sub(r'[^\w\s-]', '', topic).strip().replace(' ', '_')[:50]
            filename = f"documento_{topic_slug}_{timestamp}.pdf"
            filepath = FILES_DIR / filename
            
            logger.info(f"📝 Generando PDF: {filename}")
            logger.info(f"📝 Guardando en: {filepath}")
            generate_pdf(filepath, text_response)
            logger.info(f"✅ PDF generado exitosamente!")
            logger.info(f"📂 Archivo existe: {filepath.exists()}")
            logger.info(f"📊 Tamaño del archivo: {filepath.stat().st_size if filepath.exists() else 0} bytes")
            
            response_data = {
                "type": "file",
                "filename": filename,
                "url": f"http://localhost:8000/files/{filename}",
                "message": "PDF generado correctamente",
            }
            logger.info(f"📤 Enviando respuesta al frontend: {json.dumps(response_data, indent=2)}")
            return response_data
        
        logger.info("💬 No es generación de PDF (o está usando ChatGPT), procesando como mensaje normal...")
        
        if is_using_chatgpt:
            logger.info("🌐 Llamando a ChatGPT API...")
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "Answer always in the user language"},
                        {"role": "user", "content": user_message},
                    ],
                },
                timeout=60,
            )
            data = response.json()
            text_response = data["choices"][0]["message"]["content"].strip()
            return {"type": "text", "response": text_response}

        logger.info(f"🏠 Llamando a modelo local: {ANYTHING_LLM_URL}/api/v1/workspace/rag/chat")
        response = requests.post(
            f"{ANYTHING_LLM_URL}/api/v1/workspace/rag/chat",
            headers={
                "Authorization": f"Bearer {ANYTHING_LLM_API_KEY}",
                "Content-Type": "application/json",
            },
            json={"message": user_message, "rules": "Answer always in the user language"},
            timeout=60,
        )

        data = response.json()
        text_response = data.get("textResponse", "").replace("**", "").strip()

        logger.info("💡 Respuesta textual del modelo local enviada.")
        return {"type": "text", "response": text_response}

    except Exception as e:
        logger.error(f"❌ Error en chat_router: {str(e)}")
        return {"type": "error", "response": str(e)}


# File retrieval endpoint
@app.get("/files/{filename}")
async def get_file(filename: str):
    """Returns a generated file."""
    logger.info(f"📥 Solicitud de descarga de archivo: {filename}")
    file_path = FILES_DIR / filename
    logger.info(f"📂 Ruta completa: {file_path}")
    logger.info(f"📂 Archivo existe: {file_path.exists()}")
    
    if not file_path.exists():
        logger.warning(f"❌ Archivo no encontrado: {filename}")
        return {"error": "Archivo no encontrado"}
    
    logger.info(f"✅ Enviando archivo: {filename} ({file_path.stat().st_size} bytes)")
    return FileResponse(
        file_path, 
        filename=filename,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# MCP Tool listing
@mcp_server.list_tools()
async def list_tools():
    return [
        types.Tool(
            name="chat",
            description="Send a message to either ChatGPT or the local model",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "isUsingChatGPT": {"type": "boolean"},
                },
                "required": ["message"],
            },
        )
    ]


# Run the app
if __name__ == "__main__":
    import uvicorn

    logger.info("🚀 Iniciando servidor Atom LLM...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
