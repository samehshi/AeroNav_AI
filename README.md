# 📡 NANSC Intelligent Operations Console

**AI-Powered Civil Aviation Telecommunications Assistant for Operations and Training**

![NANSC Intelligent Operations Console](docs/images/Gemini Generated Image.jpeg)

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

## 🏗️ Architecture

**4-Layer Enterprise Architecture:**

```
Layer 4: User Interface
├── Gradio Dashboard
├── Interactive Chat
├── Batch Processing Tools
└── Telemetry Monitoring

Layer 3: Agent Orchestration
├── EnterpriseAgent
├── Google Gemini 2.5 Flash
├── Tool Detection & Calling
└── Session Management

Layer 2: Knowledge & Tools
├── ICAOTools (Airport, AFTN, Web Search)
├── RAGEngine (Document Processing)
└── GoogleEmbeddings (Vector Store)

Layer 1: State & Configuration
├── SystemConfig
├── ObservabilityService
└── SessionManager
```

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

## 📊 System Health

The system includes comprehensive health checking:
- API key configuration validation
- Model initialization verification
- Tool availability testing
- Storage system checks
- Telemetry service validation
- RAG engine status monitoring

## 🔧 Technical Highlights

- **Production-Grade Error Handling**: Graceful degradation when components fail
- **Kaggle-Optimized**: Works seamlessly in Kaggle environments
- **Async Processing**: Non-blocking operations for better performance
- **Custom Embeddings**: Avoids pydantic_v1 compatibility issues
- **Enterprise Architecture**: Clean separation of concerns
- **Comprehensive Documentation**: Every component thoroughly explained

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

## 🎥 Demo

The notebook is structured for an excellent demonstration:
1. **Problem**: Industry challenges in civil aviation telecommunications
2. **Solution**: AI agent overview and capabilities
3. **Architecture**: 4-layer enterprise architecture explanation
4. **Demo**: Live demonstration of all features

## 📞 Contact

- **Author**: Sameh Shehata Abdelaziz
- **Environment**: Kaggle
- **Version**: 1.0

---

**Built with Google Gemini, LangChain, ChromaDB, and Gradio**

**Keywords**: AI Agent, Multi-Agent Orchestration, Civil Aviation, Telecommunications, ICAO, AFTN, AMHS, RAG, LangChain, Google Gemini, Gradio, ChromaDB, Enterprise AI