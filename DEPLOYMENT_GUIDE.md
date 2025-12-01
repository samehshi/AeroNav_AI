# 🚀 NANSC Intelligent Operations Console - Deployment Guide

## 📋 Overview

This guide provides step-by-step instructions for deploying your NANSC Intelligent Operations Console to various platforms. Choose the deployment option that best fits your needs.

---

## 🎯 Quick Reference

| Platform | Cost | Interactivity | Setup Time | Best For | Difficulty |
|----------|------|--------------|------------|----------|------------|
| **Hugging Face Spaces** | $0 | ✅ Full | 5 minutes | **AI Agent Demos** | ⭐⭐⭐ Easy |
| **GitHub Pages** | $0 | ❌ Static | 10 minutes | Portfolio/Demo | ⭐⭐⭐⭐ Medium |
| **Streamlit Cloud** | $0 | ✅ Full | 10 minutes | General Apps | ⭐⭐⭐⭐ Medium |
| **Google Cloud Run** | $5-50/mo | ✅ Full | 15 minutes | Production | ⭐⭐⭐⭐⭐ Advanced |

---

## 🤖 Option 1: Hugging Face Spaces (Recommended)

### 🎯 Why Choose This?
- ✅ **Completely free** with full interactivity
- ✅ **AI-optimized platform** built specifically for AI applications
- ✅ **5-minute deployment** with automatic setup
- ✅ **Professional appearance** perfect for competitions
- ✅ **Generous free tier** with no credit card required

### 📋 Prerequisites
- [Hugging Face account](https://huggingface.co)
- GitHub repository with your code

### 🚀 Deployment Steps

#### Step 1: Prepare Your Files

**Create `app.py`:**
```python
# app.py - Hugging Face Spaces version
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

# Copy all your classes from the notebook:
# - TelemetryEvent, ObservabilityService
# - SessionManager
# - ICAOTools
# - RAGEngine
# - EnterpriseAgent

# Your Gradio interface (from cell 12)
# ... (paste your demo interface code)

# The interface will be automatically loaded by Hugging Face Spaces
```

**Create `requirements.txt`:**
```
google-generativeai>=0.3.0
langchain>=0.0.300
langchain-community>=0.0.20
langchain-google-genai>=1.0.0
chromadb>=0.4.0
gradio>=4.0.0
nest-asyncio>=1.6.0
pypdf>=3.17.0
pandas>=2.0.0
duckduckgo-search>=3.9.0
numpy>=1.24.0
```

**Create `README.md` for Hugging Face:**
```markdown
---
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
```

#### Step 2: Deploy to Hugging Face

1. **Create New Space:**
   - Go to [huggingface.co/spaces](https://huggingface.co/spaces)
   - Click "New Space"
   - Set **Space Type**: `Gradio`
   - Set **Visibility**: `Public`
   - Click "Create Space"

2. **Upload Files:**
   - Upload `app.py`
   - Upload `requirements.txt`
   - Upload `README.md`
   - Click "Commit changes"

3. **Configure Environment:**
   - Go to Settings > Secrets
   - Add `GOOGLE_API_KEY` as a secret
   - Set **Secret Type**: `Repository secret`

4. **Wait for Deployment:**
   - Hugging Face will automatically build and deploy your app
   - This usually takes 2-5 minutes
   - You'll see the live app at `https://huggingface.co/spaces/yourusername/your-space-name`

### 🎉 Done! Your app is live!

---

## 🌐 Option 2: GitHub Pages (Static)

### 🎯 Why Choose This?
- ✅ **Free static hosting** for portfolio/demo purposes
- ✅ **Custom domain support**
- ✅ **Great for documentation** and static content
- ✅ **Professional presentation**

### 🚀 Deployment Steps

#### Step 1: Create Static HTML

**Create `export_to_html.py`:**
```python
# export_to_html.py
import gradio as gr

# Import your demo interface from the notebook
# ... (import your demo interface)

# Export to static HTML
demo.launch(
    server_name="0.0.0.0",
    server_port=7860,
    enable_queue=True,
    share=True  # Creates temporary public link for testing
)
```

#### Step 2: Create GitHub Repository

```bash
# Create new repository on GitHub (don't initialize with README)
git clone https://github.com/yourusername/nansc-console.git
cd nansc-console
```

#### Step 3: Create Static Site

**Create `index.html`:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NANSC Intelligent Operations Console</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        h1 {
            color: #667eea;
            text-align: center;
            margin-bottom: 30px;
        }
        .info-box {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin: 30px 0;
            border-radius: 8px;
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .feature-card {
            background: #fff;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .badge {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            margin: 5px;
        }
        .btn {
            background: #667eea;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            text-decoration: none;
            display: inline-block;
            font-weight: bold;
            margin: 10px 5px;
            transition: background 0.3s;
        }
        .btn:hover {
            background: #5568d3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📡 NANSC Intelligent Operations Console</h1>
        <div class="info-box">
            <h3>🚀 Live Demo</h3>
            <p>This is a static demo of the NANSC Intelligent Operations Console. The full interactive version is available on Hugging Face Spaces.</p>
            <a href="https://huggingface.co/spaces/yourusername/nansc-console" class="btn" target="_blank">🔗 Open Live Demo</a>
            <a href="https://github.com/yourusername/nansc-console" class="btn" target="_blank">📁 View Source Code</a>
        </div>

        <div class="features">
            <div class="feature-card">
                <h4>🤖 Multi-Agent Orchestration</h4>
                <p>Intelligent coordination of multiple specialized tools for civil aviation telecommunications operations.</p>
                <span class="badge">AI Agent</span>
                <span class="badge">Google Gemini</span>
                <span class="badge">Tool Calling</span>
            </div>
            <div class="feature-card">
                <h4>🛠️ Specialized Tools</h4>
                <p>ICAO airport lookup, AFTN-to-AMHS conversion, and web search integration for enhanced capabilities.</p>
                <span class="badge">ICAO Lookup</span>
                <span class="badge">AFTN Converter</span>
                <span class="badge">Web Search</span>
            </div>
            <div class="feature-card">
                <h4>📚 Retrieval Augmented Generation</h4>
                <p>Document processing and intelligent search through procedures and manuals using RAG technology.</p>
                <span class="badge">RAG</span>
                <span class="badge">ChromaDB</span>
                <span class="badge">Document AI</span>
            </div>
            <div class="feature-card">
                <h4>📊 Enterprise Features</h4>
                <p>Professional-grade observability, session management, and batch processing capabilities.</p>
                <span class="badge">Telemetry</span>
                <span class="badge">Session Mgmt</span>
                <span class="badge">Batch Processing</span>
            </div>
        </div>

        <div class="info-box">
            <h3>📋 Competition Features</h3>
            <ul>
                <li>✅ Multi-agent orchestration with custom tools</li>
                <li>✅ Retrieval Augmented Generation (RAG) implementation</li>
                <li>✅ Session management and observability</li>
                <li>✅ Async processing and error handling</li>
                <li>✅ Professional documentation and architecture</li>
                <li>✅ Google Gemini integration</li>
            </ul>
        </div>

        <div class="info-box">
            <h3>🔧 Technical Stack</h3>
            <p><strong>AI & Frameworks:</strong> Google Gemini 2.5 Flash, LangChain, ChromaDB</p>
            <p><strong>Interface:</strong> Gradio, HTML/CSS</p>
            <p><strong>Architecture:</strong> 4-Layer Enterprise Design</p>
            <p><strong>Deployment:</strong> Hugging Face Spaces (Free)</p>
        </div>

        <div class="info-box">
            <h3>🎯 Use Cases</h3>
            <p><strong>For Aviation Telecommunications:</strong> ICAO code lookups, AFTN/AMHS conversions, procedure references</p>
            <p><strong>For Training:</strong> Interactive learning tool for telecommunications operations</p>
            <p><strong>For Operations:</strong> Real-time assistance for message switching and navigation services</p>
        </div>

        <div style="text-align: center; margin-top: 40px;">
            <p><strong>📧 Contact:</strong> Sameh Shehata Abdelaziz</p>
            <p><strong>📁 Repository:</strong> <a href="https://github.com/yourusername/nansc-console" target="_blank">github.com/yourusername/nansc-console</a></p>
        </div>
    </div>
</body>
</html>
```

**Create `README.md`:**
```markdown
# 📡 NANSC Intelligent Operations Console

**AI-Powered Civil Aviation Telecommunications Assistant for Operations and Training**

## 🎯 Problem Statement

**Civil aviation telecommunications operators face critical challenges in their day-to-day operations:**

1. **Time-Consuming Manual Lookups**: ICAO airport codes require manual database searches, slowing down operations
2. **Complex Address Conversions**: AFTN to AMHS conversions require specialized telecommunications knowledge
3. **Buried Procedures**: Critical operational procedures are scattered across lengthy documents and manuals
4. **No Centralized Assistant**: Operators must juggle multiple tools and references, increasing cognitive load

**Impact on Operations and Training:**
- Operators spend significant time on routine information retrieval
- Manual processes increase the risk of errors in critical telecommunications operations
- Difficulty accessing procedures quickly can impact training effectiveness
- Fragmented tools reduce operational efficiency and increase training complexity

**Our Solution:**
An AI-powered operations console that automates these tasks, providing instant access to airport information, seamless address conversions, and intelligent document search - all through a unified interface designed for operational and training environments.

## ✨ Features

### 🤖 Multi-Agent Orchestration
- **EnterpriseAgent**: Intelligent orchestration of multiple specialized tools
- **Automatic Tool Detection**: Regex-based detection of ICAO codes and AFTN addresses
- **Context-Aware Responses**: Smart integration of tool results with LLM responses

### 🛠️ Specialized Tools
- **ICAO Airport Lookup**: Instant airport information with web search fallback
- **AFTN to AMHS Conversion**: Automatic address format conversion (8-char to X.400)
- **Web Search Integration**: Enhanced capabilities for unknown airport codes

### 📚 Retrieval Augmented Generation (RAG)
- **Document Ingestion**: PDF processing and vector storage
- **Intelligent Search**: Semantic similarity search through procedures and manuals
- **Context Injection**: Automatic integration of relevant document chunks

### 📊 Enterprise Features
- **Session Management**: Conversation history persistence
- **Observability**: Comprehensive telemetry, logging, and metrics
- **Batch Processing**: Handle multiple operations efficiently
- **Health Monitoring**: Real-time system status and diagnostics

### 🎨 Professional Interface
- **Gradio Dashboard**: Professional, user-friendly interface
- **Multiple Interaction Modes**: Chat, batch processing, document management
- **Real-time Telemetry**: Live system monitoring and analytics

## 🚀 Quick Start

### Prerequisites
- Google API Key (stored in Kaggle Secrets as 'GOOGLE_API_KEY')
- Python 3.8+

### Installation
```bash
pip install -q -U google-generativeai langchain langchain-google-genai chromadb gradio nest_asyncio pypdf pandas duckduckgo-search
```

### Usage

1. **Interactive Chat**: Ask questions about aviation procedures, airport codes, or address conversions
2. **Batch Processing**: Process multiple ICAO codes or AFTN addresses at once
3. **Document Upload**: Upload PDFs for RAG-powered search
4. **Telemetry Monitoring**: Track system performance and usage metrics

### Example Queries
- "What is AMHS?"
- "Where is airport OJAA?"
- "Convert HECAYFYX to X.400 format"
- "What are the flight planning procedures?"
- "Lookup XXXX (unknown ICAO code - will trigger web search)"

## 📁 Project Structure

```
NANSC_AI-Agent/
├── 📓 Notebooks
├── ├── Aero_NAV_Agents_Kaggle.ipynb    # Main notebook (competition-ready)
├── ├── Aero_NAV_Agents.ipynb           # Original notebook
├── ├── Aero_NAV_Agents_Local.ipynb     # Local development version
├── ├── day_01.md → day_05.md           # Development documentation
├── 📄 Documentation
├── ├── ISSUES_AND_FIXES_SUMMARY.md     # Technical documentation
├── ├── COMPETITION_ALIGNMENT_REPORT.md # Competition analysis
├── ├── QUICK_ENHANCEMENT_KIT.md       # Enhancement guide
├── 🎨 Assets
├── ├── docs/
├── ├── └── images/
├── ├── └── └── Gemini Generated Image.jpeg
└── README.md                           # This file
```

## 📞 Contact

- **Author**: Sameh Shehata Abdelaziz
- **Environment**: Kaggle
- **Version**: 1.0

---

**Built with Google Gemini, LangChain, ChromaDB, and Gradio**

**Keywords**: AI Agent, Multi-Agent Orchestration, Civil Aviation, Telecommunications, ICAO, AFTN, AMHS, RAG, LangChain, Google Gemini, Gradio, ChromaDB, Enterprise AI
```

#### Step 4: Deploy to GitHub Pages

```bash
# Initialize git and deploy
git init
git add .
git commit -m "Initial commit: NANSC Console GitHub Pages"
git branch -M main
git remote add origin https://github.com/yourusername/nansc-console.git
git push -u origin main

# Enable GitHub Pages
echo "✅ Repository created! Now enable GitHub Pages in your repository settings:"
echo "1. Go to Settings > Pages"
echo "2. Select 'Deploy from a branch'"
echo "3. Choose 'main' branch and '/' folder"
echo "4. Click 'Save'"
```

### 🎉 Done! Your site is live!

---

## ☁️ Option 3: Google Cloud Run (Production)

### 🎯 Why Choose This?
- ✅ **Production-grade hosting** with automatic scaling
- ✅ **Global access** with Google's infrastructure
- ✅ **Enterprise features** like custom domains and SSL
- ✅ **Pay-per-use** pricing model

### 📋 Prerequisites
- Google Cloud account with billing enabled
- Google Cloud SDK installed
- Google API key in Secret Manager

### 🚀 Deployment Steps

#### Step 1: Prepare Files

**Create `app.py`:**
```python
# app.py - Cloud Run version
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

# [Include all your existing code from the notebook here]
# Copy cells 4-12 into this file, adjusting imports as needed

# Your existing demo interface (from cell 12)
# ... (paste your demo interface code)

# The interface will be automatically loaded by Hugging Face Spaces
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 8080)))
```

**Create `requirements.txt`:**
```
google-generativeai>=0.3.0
langchain>=0.0.300
langchain-community>=0.0.20
langchain-google-genai>=1.0.0
chromadb>=0.4.0
gradio>=4.0.0
nest-asyncio>=1.6.0
pypdf>=3.17.0
pandas>=2.0.0
duckduckgo-search>=3.9.0
numpy>=1.24.0
```

**Create `Dockerfile`:**
```dockerfile
# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Expose port
EXPOSE 8080

# Set environment variables
ENV PYTHONPATH=/app
ENV PERSISTENCE_DIR=/tmp/nansc_data

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Run the application
CMD ["python", "app.py"]
```

**Create `cloudbuild.yaml`:**
```yaml
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/nansc-console:$COMMIT_SHA', '.']

  # Push the container image to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/nansc-console:$COMMIT_SHA']

  # Deploy container image to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'nansc-console'
      - '--image=gcr.io/$PROJECT_ID/nansc-console:$COMMIT_SHA'
      - '--region=us-central1'
      - '--platform=managed'
      - '--allow-unauthenticated'
      - '--set-env-vars=GOOGLE_API_KEY=$$GOOGLE_API_KEY'
    secretEnv: ['GOOGLE_API_KEY']

availableSecrets:
  secretManager:
    - versionName: projects/$PROJECT_ID/secrets/GOOGLE_API_KEY/versions/latest
      env: 'GOOGLE_API_KEY'
```

#### Step 2: Set Up Google Cloud

```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com run.googleapis.com

# Create secret in Google Secret Manager
echo "your-google-api-key-here" | gcloud secrets create GOOGLE_API_KEY --data-file=-

# Grant Cloud Build access to the secret
gcloud secrets add-iam-policy-binding GOOGLE_API_KEY \
    --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

#### Step 3: Deploy

```bash
# Option A: Using Cloud Build (recommended)
gcloud builds submit --config cloudbuild.yaml .

# Option B: Direct deployment
gcloud run deploy nansc-console \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars=GOOGLE_API_KEY=$GOOGLE_API_KEY
```

### 🎉 Done! Your app is live on Cloud Run!

---

## 📊 Cost Comparison

| Platform | Compute Cost | Network Cost | Storage Cost | Total Monthly Cost |
|----------|-------------|--------------|--------------|-------------------|
| **Hugging Face Spaces** | $0 | Included | Included | **$0** |
| **GitHub Pages** | $0 | Included | Included | **$0** |
| **Streamlit Cloud** | $0 | Included | Included | **$0** |
| **Google Cloud Run** | $0.000024/vCPU-sec | $0.12/GB egress | $0.10/GB | **$5-50** |

---

## 🎯 Which Option Should You Choose?

### 🏆 **For Competition: Hugging Face Spaces**
- ✅ Free with full interactivity
- ✅ AI-optimized platform
- ✅ Professional appearance
- ✅ Easy 5-minute setup
- ✅ Perfect for showcasing AI agents

### 📁 **For Portfolio: GitHub Pages**
- ✅ Free static hosting
- ✅ Custom domain support
- ✅ Great for documentation
- ✅ Professional presentation

### 🏢 **For Production: Google Cloud Run**
- ✅ Enterprise-grade hosting
- ✅ Global access and scaling
- ✅ Custom domains and SSL
- ✅ Professional monitoring

---

## 🔧 Troubleshooting

### Common Issues

**Hugging Face Spaces:**
- **Error**: "Module not found"
  - **Solution**: Check `requirements.txt` syntax
- **Error**: "API key not found"
  - **Solution**: Verify secret is set in Settings > Secrets

**GitHub Pages:**
- **Error**: "Site not loading"
  - **Solution**: Check Pages settings in repository settings
- **Error**: "Mixed content"
  - **Solution**: Use HTTPS URLs for all resources

**Google Cloud Run:**
- **Error**: "Container failed to start"
  - **Solution**: Check Dockerfile and entrypoint
- **Error**: "Permission denied"
  - **Solution**: Verify IAM permissions and secret access

### Getting Help

- **Hugging Face**: [Discord Community](https://huggingface.co/join/discord)
- **GitHub Pages**: [GitHub Docs](https://docs.github.com/en/pages)
- **Google Cloud Run**: [Cloud Run Docs](https://cloud.google.com/run/docs)

---

## 📞 Support

If you encounter issues:

1. **Check the logs** in your deployment platform
2. **Verify environment variables** are set correctly
3. **Test locally** before deploying
4. **Consult the troubleshooting section** above
5. **Reach out for help** in the respective communities

---

**Ready to deploy! 🚀**

Choose your deployment option and get your NANSC Intelligent Operations Console live on the internet!