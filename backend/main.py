import os
import re
import json
import requests
import base64
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from mcp.server import Server
import mcp.types as types
import logging
from pathlib import Path
from tools.generate_pdf import generate_pdf
from tools.generate_chart import generate_chart

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
    logger.info("📨 New request received at /api/chat")

    body = await request.json()
    user_message = body.get("message", "")
    is_using_chatgpt = body.get("isUsingChatGPT", False)

    logger.info(f"💬 User message: {user_message[:100]}...")
    logger.info(f"🤖 Using ChatGPT: {is_using_chatgpt}")

    try:
        logger.info("🔍 Checking if it's a PDF generation request...")
        should_generate_pdf = (
            ("generar" in user_message.lower() or "genera" in user_message.lower()) 
            and "pdf" in user_message.lower()
            and not is_using_chatgpt
        )
        
        logger.info("🔍 Checking if it's a chart generation request...")
        should_generate_chart = (
            ("generar" in user_message.lower() or "genera" in user_message.lower() or "crear" in user_message.lower() or "crea" in user_message.lower()) 
            and ("gráfica" in user_message.lower() or "grafica" in user_message.lower() or "gráfico" in user_message.lower() or "grafico" in user_message.lower() or "chart" in user_message.lower())
            and not is_using_chatgpt
        )
        
        # Detect chart type
        chart_type = 'bar'  # Default
        if should_generate_chart:
            if "línea" in user_message.lower() or "linea" in user_message.lower() or "line" in user_message.lower():
                chart_type = 'line'
            elif "circular" in user_message.lower() or "pie" in user_message.lower() or "pastel" in user_message.lower():
                chart_type = 'pie'
            elif "dispersión" in user_message.lower() or "dispersion" in user_message.lower() or "scatter" in user_message.lower():
                chart_type = 'scatter'
        
        if should_generate_chart:
            logger.info(f"📊 Action detected: chart generation type {chart_type} with local model!")
            logger.info("📝 Getting data from local model first...")
            
            # Create specific prompt to get data in JSON format
            json_prompt = f"""{user_message}

IMPORTANT: Respond ONLY with a valid JSON object in this exact format:
{{"label1": value1, "label2": value2, "label3": value3}}

Example for football club income:
{{"2020": 50000000, "2021": 55000000, "2022": 60000000, "2023": 58000000}}

- Keys must be labels or categories (years, months, names, etc.)
- Values must be numbers
- DO NOT include explanatory text, ONLY the JSON
- DO NOT use markdown or code blocks, ONLY pure JSON"""
            
            logger.info(f"🏠 Calling local model to generate data...")
            response = requests.post(
                f"{ANYTHING_LLM_URL}/api/v1/workspace/rag/chat",
                headers={
                    "Authorization": f"Bearer {ANYTHING_LLM_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={"message": json_prompt, "rules": "Answer always in the user language. Return ONLY valid JSON, no explanatory text."},
                timeout=180,
            )
            data = response.json()
            text_response = data.get("textResponse", "").replace("**", "").strip()
            
            logger.info(f"📄 Model response: {text_response[:200]}...")
            
            logger.info(f"📄 Data generated ({len(text_response)} characters)")
            
            import time
            timestamp = int(time.time())
            topic = user_message.lower().replace("genera", "").replace("generar", "").replace("crea", "").replace("crear", "").replace("gráfica", "").replace("grafica", "").replace("gráfico", "").replace("grafico", "").replace("chart", "").replace("un", "").replace("de", "").strip()
            topic_slug = re.sub(r'[^\w\s-]', '', topic).strip().replace(' ', '_')[:50]
            filename = f"chart_{chart_type}_{topic_slug}_{timestamp}.png"
            filepath = FILES_DIR / filename
            
            logger.info(f"📊 Generating chart: {filename}")
            logger.info(f"📊 Saving to: {filepath}")
            generate_chart(filepath, text_response, chart_type)
            logger.info(f"✅ Chart generated successfully!")
            logger.info(f"📂 File exists: {filepath.exists()}")
            logger.info(f"📊 File size: {filepath.stat().st_size if filepath.exists() else 0} bytes")
            
            # Read image and convert to base64 to display in chat
            with open(filepath, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            response_data = {
                "type": "image",
                "filename": filename,
                "imageData": f"data:image/png;base64,{image_data}",
                "url": f"http://localhost:8000/files/{filename}",
                "message": f"Chart type {chart_type} generated successfully",
            }
            logger.info(f"📤 Sending response to frontend with base64 image")
            return response_data
        
        if should_generate_pdf:
            logger.info("🧾 Action detected: PDF generation with local model!")
            logger.info("📝 Getting content from local model first...")
            
            logger.info(f"🏠 Calling local model to generate content...")
            response = requests.post(
                f"{ANYTHING_LLM_URL}/api/v1/workspace/rag/chat",
                headers={
                    "Authorization": f"Bearer {ANYTHING_LLM_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={"message": user_message, "rules": "Answer always in the user language"},
                timeout=180,
            )
            data = response.json()
            text_response = data.get("textResponse", "").replace("**", "").strip()
            
            logger.info(f"📄 Content generated ({len(text_response)} characters)")
            
            import time
            timestamp = int(time.time())
            topic = user_message.lower().replace("genera", "").replace("generar", "").replace("pdf", "").replace("un", "").replace("de", "").strip()
            topic_slug = re.sub(r'[^\w\s-]', '', topic).strip().replace(' ', '_')[:50]
            filename = f"document_{topic_slug}_{timestamp}.pdf"
            filepath = FILES_DIR / filename
            
            logger.info(f"📝 Generating PDF: {filename}")
            logger.info(f"📝 Saving to: {filepath}")
            generate_pdf(filepath, text_response)
            logger.info(f"✅ PDF generated successfully!")
            logger.info(f"📂 File exists: {filepath.exists()}")
            logger.info(f"📊 File size: {filepath.stat().st_size if filepath.exists() else 0} bytes")
            
            response_data = {
                "type": "file",
                "filename": filename,
                "url": f"http://localhost:8000/files/{filename}",
                "message": "PDF generated successfully",
            }
            logger.info(f"📤 Sending response to frontend: {json.dumps(response_data, indent=2)}")
            return response_data
        
        logger.info("💬 Not PDF generation (or using ChatGPT), processing as normal message...")
        
        if is_using_chatgpt:
            logger.info("🌐 Calling ChatGPT API...")
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
                timeout=180,
            )
            data = response.json()
            text_response = data["choices"][0]["message"]["content"].strip()
            return {"type": "text", "response": text_response}

        logger.info(f"🏠 Calling local model: {ANYTHING_LLM_URL}/api/v1/workspace/rag/chat")
        response = requests.post(
            f"{ANYTHING_LLM_URL}/api/v1/workspace/rag/chat",
            headers={
                "Authorization": f"Bearer {ANYTHING_LLM_API_KEY}",
                "Content-Type": "application/json",
            },
            json={"message": user_message, "rules": "Answer always in the user language"},
            timeout=180,
        )

        data = response.json()
        text_response = data.get("textResponse", "").replace("**", "").strip()

        logger.info("💡 Text response from local model sent.")
        return {"type": "text", "response": text_response}

    except Exception as e:
        logger.error(f"❌ Error in chat_router: {str(e)}")
        return {"type": "error", "response": str(e)}


# File retrieval endpoint
@app.get("/files/{filename}")
async def get_file(filename: str):
    """Returns a generated file (PDF or PNG)."""
    logger.info(f"📥 File download request: {filename}")
    file_path = FILES_DIR / filename
    logger.info(f"📂 Full path: {file_path}")
    logger.info(f"📂 File exists: {file_path.exists()}")
    
    if not file_path.exists():
        logger.warning(f"❌ File not found: {filename}")
        return {"error": "File not found"}
    
    # Determine file type
    if filename.endswith('.png'):
        media_type = "image/png"
    elif filename.endswith('.pdf'):
        media_type = "application/pdf"
    else:
        media_type = "application/octet-stream"
    
    logger.info(f"✅ Sending file: {filename} ({file_path.stat().st_size} bytes, type: {media_type})")
    return FileResponse(
        file_path, 
        filename=filename,
        media_type=media_type,
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

    logger.info("🚀 Starting Atom LLM server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
