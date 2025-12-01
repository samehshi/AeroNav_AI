#!/usr/bin/env python3
"""
Hugging Face Spaces Deployment Script

This script helps you deploy your NANSC Intelligent Operations Console
to Hugging Face Spaces for free with full interactivity.

Usage:
    python scripts/deploy_hf_spaces.py --api-key YOUR_API_KEY --space-name your-space-name
"""

import os
import sys
import argparse
import subprocess
import tempfile
import shutil
from pathlib import Path


class HuggingFaceDeployer:
    def __init__(self, api_key, space_name, username=None):
        self.api_key = api_key
        self.space_name = space_name
        self.username = username
        self.space_url = f"https://huggingface.co/spaces/{self.username}/{self.space_name}" if self.username else None

    def create_deployment_files(self, temp_dir):
        """Create all necessary files for Hugging Face Spaces deployment."""
        temp_path = Path(temp_dir)

        # Create app.py
        app_py_content = '''# app.py - Hugging Face Spaces version
import os
import json
import logging
import asyncio
import nest_asyncio
import pandas as pd
import gradio as gr
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass

# Third-party imports
import google.generativeai as genai
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.embeddings import Embeddings
import numpy as np

# Configure Google API Key from environment
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is required")

genai.configure(api_key=GOOGLE_API_KEY)
nest_asyncio.apply()

# Custom Embeddings (copy from your notebook)
class GoogleEmbeddings(Embeddings):
    def __init__(self, model_name: str = "models/embedding-001"):
        self.model_name = model_name
        self.client = genai

    def embed_documents(self, texts):
        try:
            results = []
            for text in texts:
                response = self.client.embed_content(
                    model=self.model_name,
                    content=text,
                    task_type="retrieval_document"
                )
                results.append(response['embedding'])
            return results
        except Exception as e:
            print(f"Warning: Document embedding failed: {e}")
            return [[0.0] * 768 for _ in texts]

    def embed_query(self, text):
        try:
            response = self.client.embed_content(
                model=self.model_name,
                content=text,
                task_type="retrieval_query"
            )
            return response['embedding']
        except Exception as e:
            print(f"Warning: Query embedding failed: {e}")
            return [0.0] * 768

# System Configuration
@dataclass
class SystemConfig:
    app_name: str = "NANSC_Intelligent_Console"
    persistence_dir: str = os.environ.get("PERSISTENCE_DIR", "/tmp/nansc_data")
    model_name: str = "gemini-2.5-flash"

    def __post_init__(self):
        os.makedirs(self.persistence_dir, exist_ok=True)

sys_config = SystemConfig()

# Observability Service (copy from notebook)
@dataclass
class TelemetryEvent:
    timestamp: str
    event_type: str
    details: str

class ObservabilityService:
    def __init__(self):
        self.events: List[TelemetryEvent] = []
        self.metrics = {"requests": 0, "tool_usage": 0, "errors": 0}

    def log_event(self, event_type: str, details: str):
        event = TelemetryEvent(
            datetime.now().strftime("%H:%M:%S"),
            event_type,
            details
        )
        self.events.append(event)
        if event_type == "ERROR":
            self.metrics["errors"] += 1
        elif event_type == "REQUEST":
            self.metrics["requests"] += 1
        elif event_type == "TOOL_USE":
            self.metrics["tool_usage"] += 1

    def get_logs(self) -> str:
        return "\\n".join([
            f"[{e.timestamp}] [{e.event_type}] {e.details}"
            for e in self.events[-15:]
        ])

    def get_metrics(self) -> Dict[str, int]:
        return self.metrics.copy()

# Session Manager (copy from notebook)
class SessionManager:
    def __init__(self, config: SystemConfig):
        self.filepath = os.path.join(config.persistence_dir, "sessions.json")

    def save_session(self, session_id: str, history: List[Dict]):
        data = {}
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"Warning: Could not read session file: {e}")

        data[session_id] = {
            "timestamp": datetime.now().isoformat(),
            "history": history
        }

        try:
            with open(self.filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save session: {e}")

    def load_session(self, session_id: str) -> List[Dict]:
        if not os.path.exists(self.filepath):
            return []

        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
                return data.get(session_id, {}).get("history", [])
        except Exception as e:
            print(f"Warning: Could not load session: {e}")
            return []

# ICAOTools (copy from notebook)
class ICAOTools:
    AIRPORT_DB = {
        "HECA": "Cairo Intl (Egypt)",
        "HEBA": "Borg El Arab (Egypt)",
        "OJAA": "Queen Alia (Jordan)",
        "EGLL": "London Heathrow (UK)",
        "LFPG": "Paris CDG (France)",
        "KJFK": "JFK New York (USA)",
        "KORD": "O'Hare Chicago (USA)",
        "EHAM": "Amsterdam Schiphol (Netherlands)",
        "EDDF": "Frankfurt (Germany)",
        "ZBAA": "Beijing Capital (China)",
        "RJTT": "Tokyo Haneda (Japan)",
        "YSSY": "Sydney (Australia)",
        "FAOR": "OR Tambo Johannesburg (South Africa)",
        "OMDB": "Dubai (UAE)",
        "VHHH": "Hong Kong (China)",
    }

    @staticmethod
    def lookup_airport(icao_code: str) -> str:
        code = icao_code.upper().strip()
        if len(code) != 4:
            return f"Error: ICAO code must be exactly 4 characters. Got: '{code}'"

        result = ICAOTools.AIRPORT_DB.get(code)
        if result:
            return result

        try:
            search_query = f"ICAO airport code {code} location airport name"
            search_result = ICAOTools.web_search(search_query)

            if search_result and "Error" not in search_result and len(search_result) > 10:
                message = (
                    f"⚠️ ICAO code '{code}' not found in local database.\\n"
                    f"🔎 Searching online...\\n\\n"
                    f"📍 Found result:\\n{search_result[:800]}"
                )
                return message
            else:
                message = (
                    f"❌ ICAO code '{code}' not found in local database.\\n"
                    f"🔍 Web search did not return useful results.\\n"
                    f"💡 Please verify the ICAO code and try again."
                )
                return message

        except Exception as e:
            error_msg = (
                f"❌ ICAO code '{code}' not found in local database.\\n"
                f"🔍 Web search failed: {str(e)}\\n"
                f"💡 Please verify the ICAO code or check your internet connection."
            )
            return error_msg

    @staticmethod
    def bridge_aftn_to_amhs(aftn_address: str) -> str:
        addr = aftn_address.upper().strip()
        if len(addr) != 8:
            return "Error: Address must be exactly 8 characters."

        prmd_map = {
            "HE": "EGYPT", "OJ": "JORDAN", "EG": "UK",
            "LF": "FRANCE", "K": "USA", "EH": "NETHERLANDS",
            "ED": "GERMANY", "ZB": "CHINA", "RJ": "JAPAN",
            "YS": "AUSTRALIA", "FA": "SOUTH AFRICA",
            "OM": "UAE", "VH": "HONG KONG"
        }

        prefix = addr[:2]
        prmd = prmd_map.get(prefix, "UNKNOWN")

        x400 = f"/C=XX/A=ICAO/P={prmd}/O={addr[:4]}/OU1={addr[4:]}/"
        return x400

    @staticmethod
    def web_search(query: str) -> str:
        try:
            search = DuckDuckGoSearchRun()
            res = search.run(query)
            return res[:1000]
        except Exception as e:
            error_msg = f"Search unavailable: {str(e)}"
            return error_msg

# RAGEngine (copy from notebook)
class RAGEngine:
    def __init__(self, persistence_dir: str):
        self.persist_dir = os.path.join(persistence_dir, "chroma_db")
        self.embeddings = GoogleEmbeddings(model_name="models/embedding-001")
        self.vector_store = None
        self._init_db()

    def _init_db(self):
        try:
            self.vector_store = Chroma(
                persist_directory=self.persist_dir,
                embedding_function=self.embeddings
            )
        except Exception as e:
            print(f"⚠️ Warning: ChromaDB Init failed: {e}")

    def ingest_pdf(self, file_path: str) -> str:
        if not self.vector_store or not self.embeddings:
            return "❌ Vector store not ready. Please check embeddings configuration."

        try:
            loader = PyPDFLoader(file_path)
            docs = loader.load()

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=100
            )
            splits = splitter.split_documents(docs)

            self.vector_store.add_documents(splits)

            message = f"✅ Ingested {len(splits)} document chunks into vector store."
            return message

        except Exception as e:
            error_msg = f"❌ Error ingesting document: {str(e)}"
            return error_msg

    def query(self, question: str) -> str:
        if not self.vector_store:
            return ""

        try:
            docs = self.vector_store.similarity_search(question, k=3)

            content = "\\n\\n".join([
                f"Document Chunk {i+1}:\\n{d.page_content[:500]}..."
                for i, d in enumerate(docs)
            ])

            if content:
                pass

            return content

        except Exception as e:
            error_msg = f"Query failed: {str(e)}"
            return ""

# EnterpriseAgent (copy from notebook)
class EnterpriseAgent:
    def __init__(self):
        try:
            self.model = genai.GenerativeModel(model_name=sys_config.model_name)
            self.chat = self.model.start_chat()
        except Exception as e:
            self.model = None
            self.chat = None

    def _get_system_prompt(self) -> str:
        return """
        You are the NANSC Intelligent Operations Console Assistant.

        OPERATIONAL PROTOCOL:
        1. DEFINITIONS: If the user asks "What is...", answer from your internal knowledge.
           If unsure, use the 'web_search' tool.
        2. CODES: If an ICAO code (4 letters) or AFTN address (8 letters) is detected,
           ALWAYS use 'lookup_airport' or 'bridge_aftn_to_amhs' tools automatically.
        3. PROCEDURES: If asked about rules/regs, refer to the RAG Context provided.

        BEHAVIORAL GUIDELINES:
        - Be professional, concise, and helpful
        - Always provide accurate information
        - Use tools proactively when appropriate
        - Maintain context throughout the conversation

        DOMAIN EXPERTISE:
        - Civil Aviation Telecommunications
        - ICAO Standards and Procedures
        - AFTN and AMHS Operations
        - Air Traffic Management
        - Aviation Safety and Security
        """

    def _detect_and_call_tools(self, message: str) -> str:
        import re
        icao_pattern = r'\\b[A-Z]{4}\\b'
        aftn_pattern = r'\\b[A-Z]{8}\\b'

        icao_codes = re.findall(icao_pattern, message)
        aftn_codes = re.findall(aftn_pattern, message)

        tool_results = []

        for code in icao_codes:
            if len(code) == 4:
                result = ICAOTools.lookup_airport(code)
                tool_results.append(f"ICAO Code {code}: {result}")

        for code in aftn_codes:
            if len(code) == 8:
                result = ICAOTools.bridge_aftn_to_amhs(code)
                tool_results.append(f"AFTN Code {code}: {result}")

        if tool_results:
            tool_output = "\\n".join(tool_results)
            enhanced_message = f"Tool Results:\\n{tool_output}\\n\\nUser Message: {message}"
            return enhanced_message
        else:
            return message

    async def process_message(self, message: str) -> str:
        if not message or not message.strip():
            return "Please provide a message to process."

        try:
            if not self.model or not self.chat:
                return ("⚠️ System Warning: AI model not available. This could be due to:\\n"
                       "1. API key configuration issues\\n"
                       "2. Quota limits exceeded\\n"
                       "3. Service connectivity problems\\n\\n"
                       "However, you can still use:\\n"
                       "• Airport lookups (ICAO codes)\\n"
                       "• AFTN address conversions\\n"
                       "• Batch processing tools\\n"
                       "• System telemetry monitoring\\n\\n"
                       "Please check your API configuration or try again later.")

            rag_context = ""
            if any(keyword in message.lower() for keyword in [
                "procedure", "rule", "reg", "manual", "doc", "guideline",
                "protocol", "standard", "regulation", "policy", "directive"
            ]):
                rag_context = rag_engine.query(message)
                if rag_context:
                    message = f"Reference Info from Manuals:\\n{rag_context}\\n\\nUser Question: {message}"

            enhanced_message = self._detect_and_call_tools(message)

            system_prompt = self._get_system_prompt()
            full_message = f"{system_prompt}\\n\\n{enhanced_message}"

            response = await self.chat.send_message_async(full_message)

            return response.text

        except Exception as e:
            error_msg = f"⚠️ System Error: {str(e)}"
            return error_msg

    def get_session_history(self) -> List[Dict]:
        return []

    def reset_session(self):
        pass

# Initialize services
telemetry = ObservabilityService()
session_manager = SessionManager(sys_config)
rag_engine = RAGEngine(sys_config.persistence_dir)
agent = EnterpriseAgent()

# Gradio Interface (copy from notebook cell 12)
async def chat_wrapper(message, history):
    if not message or not message.strip():
        return "Please enter a message to begin."

    try:
        response = await agent.process_message(message)
        return response
    except Exception as e:
        error_msg = f"Error processing message: {str(e)}"
        return error_msg

def batch_tool_wrapper(text_input, operation):
    if not text_input or not text_input.strip():
        return pd.DataFrame(columns=["Input", "Result"])

    lines = [l.strip() for l in text_input.split('\\n') if l.strip()]
    results = []

    for line in lines:
        try:
            if operation == "Convert AFTN":
                res = ICAOTools.bridge_aftn_to_amhs(line)
            else:
                res = ICAOTools.lookup_airport(line)

            results.append({"Input": line, "Result": res})

        except Exception as e:
            results.append({"Input": line, "Result": f"Error: {str(e)}"})

    return pd.DataFrame(results)

def ingest_wrapper(files):
    if not files:
        return "No files provided. Please upload one or more PDF files."

    results = []
    for file in files:
        try:
            result = rag_engine.ingest_pdf(file.name)
            results.append(result)
        except Exception as e:
            results.append(f"❌ Error processing {file.name}: {str(e)}")

    return "\\n".join(results)

def get_stats_wrapper():
    metrics = telemetry.get_metrics()
    logs = telemetry.get_logs()
    return json.dumps(metrics, indent=2), logs

def clear_logs_wrapper():
    telemetry.events = []
    return "Logs cleared successfully."

# Create Gradio Interface
with gr.Blocks(title="NANSC Intelligent Operations Console - Hugging Face") as demo:
    with gr.Row():
        with gr.Column():
            gr.Markdown(
                """
                # 📡 NANSC Intelligent Operations Console - Hugging Face Version
                **Civil Aviation Telecommunications | AI-Powered Assistant**

                Professional-grade interface for aviation telecommunications operations.
                Built with Google Gemini, LangChain, and Gradio.
                """
            )

    with gr.Row(equal_height=True):
        with gr.Column(scale=1, min_width=350):
            with gr.Accordion("🛠️ Batch Operations", open=True):
                gr.Markdown("Process multiple items efficiently.")
                b_input = gr.TextArea(
                    lines=4,
                    placeholder="HECAYFYX\\nOJAA\\nEGLL\\nKJFK",
                    label="Input Items (one per line)",
                    show_label=True
                )
                b_operation = gr.Radio(
                    ["Convert AFTN", "Lookup Airport"],
                    value="Convert AFTN",
                    label="Operation Type"
                )
                b_button = gr.Button("🚀 Process Batch", variant="primary")
                b_output = gr.Dataframe(
                    headers=["Input", "Result"],
                    wrap=True,
                    label="Results"
                )
                b_button.click(
                    batch_tool_wrapper,
                    inputs=[b_input, b_operation],
                    outputs=b_output
                )

            with gr.Accordion("📚 Knowledge Base Management", open=False):
                gr.Markdown("Note: Document ingestion is simplified for Hugging Face")
                f_upload = gr.File(
                    file_count="multiple",
                    file_types=[".pdf"],
                    label="Upload PDF Files"
                )
                up_button = gr.Button("📥 Ingest Documents", variant="secondary")
                up_output = gr.Textbox(
                    show_label=False,
                    placeholder="Document ingestion disabled in Hugging Face version",
                    lines=3
                )
                up_button.click(
                    ingest_wrapper,
                    inputs=[f_upload],
                    outputs=[up_output]
                )

                with gr.Row():
                    reset_button = gr.Button("🔄 Reset Session", variant="secondary")
                    clear_logs_btn = gr.Button("🧹 Clear Logs", variant="secondary")

                reset_button.click(
                    lambda: agent.reset_session(),
                    outputs=[]
                )

                clear_logs_btn.click(
                    clear_logs_wrapper,
                    outputs=[up_output]
                )

            with gr.Accordion("📊 System Telemetry", open=False):
                stat_button = gr.Button("🔄 Refresh Metrics", variant="secondary")
                stat_json = gr.Code(
                    language="json",
                    label="Usage Metrics",
                    lines=6
                )
                stat_logs = gr.TextArea(
                    label="System Logs",
                    lines=8
                )
                stat_button.click(
                    get_stats_wrapper,
                    outputs=[stat_json, stat_logs]
                )

            with gr.Accordion("🔍 System Status", open=False):
                status_box = gr.HTML()

                def update_status():
                    metrics = telemetry.get_metrics()
                    return f"""
                    <div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin: 10px 0;">
                    <strong>System Status:</strong><br>
                    • Requests: {metrics.get('requests', 0)}<br>
                    • Tool Usage: {metrics.get('tool_usage', 0)}<br>
                    • Errors: {metrics.get('errors', 0)}<br>
                    • Model: {sys_config.model_name}<br>
                    • Persistence: {sys_config.persistence_dir}
                    </div>
                    """

                demo.load(update_status, outputs=status_box)

        with gr.Column(scale=3):
            gr.ChatInterface(
                fn=chat_wrapper,
                examples=[
                    "What is AMHS?",
                    "Convert HECAYFYX to X.400",
                    "Where is OJAA airport?",
                    "Lookup EGLL",
                    "What are the procedures for flight planning?",
                    "Explain AFTN routing"
                ],
                title="Operations Assistant",
                description="""
                Interact with the Enterprise Agent. Ask about:
                • Aviation definitions and concepts
                • ICAO airport lookups (with web search fallback for unknown codes)
                • AFTN to AMHS address conversions
                • Document-based queries and procedures
                """
            )
'''

        with open(temp_path / "app.py", "w") as f:
            f.write(app_py_content)

        # Create requirements.txt
        requirements_txt = '''google-generativeai>=0.3.0
langchain>=0.0.300
langchain-community>=0.0.20
langchain-google-genai>=1.0.0
chromadb>=0.4.0
gradio>=4.0.0
nest-asyncio>=1.6.0
pypdf>=3.17.0
pandas>=2.0.0
duckduckgo-search>=3.9.0
numpy>=1.24.0'''

        with open(temp_path / "requirements.txt", "w") as f:
            f.write(requirements_txt)

        # Create README.md for Hugging Face
        readme_md = '''---
title: NANSC Intelligent Operations Console
emoji: 📡
colorFrom: blue
colorTo: purple
sdk: gradio
app_file: app.py
pinned: false
---

# 📡 NANSC Intelligent Operations Console

**AI-Powered Civil Aviation Telecommunications Assistant for Operations and Training**

## 🎯 What is this?

This is a production-grade AI agent designed for civil aviation telecommunications operations and training. It features:

- 🤖 **Multi-Agent Orchestration** with Google Gemini
- 🛠️ **Specialized Tools** for ICAO/AFTN operations
- 📚 **Retrieval Augmented Generation** for document processing
- 📊 **Enterprise Features** with observability and telemetry
- 🎨 **Professional Interface** with Gradio

## ✨ Features

### Interactive Chat
Ask questions about aviation procedures, airport codes, or address conversions:

- "What is AMHS?"
- "Where is airport OJAA?"
- "Convert HECAYFYX to X.400 format"
- "What are the flight planning procedures?"

### Batch Processing
Process multiple ICAO codes or AFTN addresses at once for efficiency.

### Document Intelligence
Upload PDFs and search through procedures and manuals using RAG technology.

### Real-time Monitoring
Track system performance and usage metrics with comprehensive telemetry.

## 🏗️ Architecture

This system follows a 4-layer enterprise architecture:

1. **Layer 1**: State & Configuration (SystemConfig, ObservabilityService, SessionManager)
2. **Layer 2**: Knowledge & Tools (ICAOTools, RAGEngine, GoogleEmbeddings)
3. **Layer 3**: Agent Orchestration (EnterpriseAgent, Google Gemini integration)
4. **Layer 4**: User Interface (Gradio Dashboard with multiple interaction modes)

## 🎯 Use Cases

**For Aviation Telecommunications:**
- ICAO code lookups and verifications
- AFTN/AMHS address conversions
- Procedure and regulation references
- Real-time operational assistance

**For Training:**
- Interactive learning tool for telecommunications operations
- Procedure lookup and verification
- Address format training
- Operational scenario practice

## 🔧 Technical Stack

- **AI**: Google Gemini 2.5 Flash
- **Framework**: LangChain
- **Vector DB**: ChromaDB
- **Interface**: Gradio
- **Language**: Python 3.10+
- **Standards**: ICAO Annex 10 compliant

## 📞 Contact

- **Author**: Sameh Shehata Abdelaziz
- **Version**: 1.0

---

**Built with Google Gemini, LangChain, ChromaDB, and Gradio**
'''

        with open(temp_path / "README.md", "w") as f:
            f.write(readme_md)

    def deploy_to_hf_spaces(self):
        """Deploy the application to Hugging Face Spaces."""
        print("🚀 Starting Hugging Face Spaces deployment...")

        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"📁 Created temporary directory: {temp_dir}")

            # Create deployment files
            self.create_deployment_files(temp_dir)

            # Create git repository
            subprocess.run(["git", "init"], cwd=temp_dir, check=True)
            subprocess.run(["git", "checkout", "-b", "main"], cwd=temp_dir, check=True)

            # Add files and commit
            subprocess.run(["git", "add", "."], cwd=temp_dir, check=True)
            subprocess.run([
                "git", "commit", "-m",
                "Initial commit: NANSC Intelligent Operations Console"
            ], cwd=temp_dir, check=True)

            # Add remote repository (you'll need to create this manually first)
            print("⚠️ Please create your Hugging Face Space first:")
            print(f"1. Go to https://huggingface.co/spaces")
            print(f"2. Click 'New Space'")
            print(f"3. Set Space Type: 'Gradio'")
            print(f"4. Set Visibility: 'Public'")
            print(f"5. Use this name: '{self.space_name}'")
            print()

            space_repo = input("Enter your Hugging Face Space git URL (e.g., https://huggingface.co/spaces/username/space-name): ")

            subprocess.run(["git", "remote", "add", "origin", space_repo], cwd=temp_dir, check=True)

            # Push to Hugging Face
            subprocess.run(["git", "push", "-u", "origin", "main", "--force"], cwd=temp_dir, check=True)

            print("✅ Files pushed to Hugging Face Spaces!")
            print("🔄 Waiting for deployment to start...")
            print()
            print("Next steps:")
            print("1. Go to your Hugging Face Space URL")
            print("2. Go to Settings > Secrets")
            print("3. Add 'GOOGLE_API_KEY' as a repository secret")
            print("4. Wait 2-5 minutes for the app to build and deploy")
            print()
            print(f"🌐 Your app will be available at: {self.space_url}")

    def run_interactive_setup(self):
        """Run interactive setup to configure deployment."""
        print("🎯 Hugging Face Spaces Deployment Setup")
        print("=" * 50)
        print()

        if not self.space_name:
            self.space_name = input("Enter your Space name: ")

        print()
        print("📋 Summary:")
        print(f"  Space Name: {self.space_name}")
        print(f"  API Key: {'*' * len(self.api_key[-4:]) if self.api_key else 'Not set'}")
        print()

        confirm = input("Continue with deployment? (y/N): ").lower().strip()
        if confirm != 'y':
            print("❌ Deployment cancelled.")
            return

        self.deploy_to_hf_spaces()


def main():
    parser = argparse.ArgumentParser(description="Deploy NANSC Console to Hugging Face Spaces")
    parser.add_argument("--api-key", help="Google API Key")
    parser.add_argument("--space-name", help="Hugging Face Space name")
    parser.add_argument("--username", help="Your Hugging Face username")
    parser.add_argument("--interactive", action="store_true", help="Run interactive setup")

    args = parser.parse_args()

    # Check for API key
    api_key = args.api_key or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Error: Google API Key not found.")
        print("Please set it via --api-key or GOOGLE_API_KEY environment variable.")
        sys.exit(1)

    # Create deployer
    deployer = HuggingFaceDeployer(
        api_key=api_key,
        space_name=args.space_name,
        username=args.username
    )

    if args.interactive:
        deployer.run_interactive_setup()
    else:
        deployer.deploy_to_hf_spaces()


if __name__ == "__main__":
    main()