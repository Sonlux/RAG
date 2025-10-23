# BookBot - Advanced RAG-Based PDF QA System

BookBot is a sophisticated full-stack AI web application that enables users to upload PDF documents, organize them into libraries, and ask intelligent questions using advanced Retrieval-Augmented Generation (RAG) with hybrid search capabilities. The system provides accurate, contextual responses from uploaded documents while maintaining comprehensive chat history.

## 🚀 Key Features

### Core Functionality

- **Multi-Library Organization**: Create and manage separate document libraries for different projects or topics
- **Advanced PDF Processing**: Intelligent parsing with metadata extraction (page numbers, sections, chapters)
- **Hybrid Search System**: Combines keyword matching with semantic search for superior retrieval accuracy
- **Dual Chat Modes**:
  - Library-wide search across all documents
  - Single PDF focused conversations
- **Persistent Chat History**: Maintain conversation context across sessions
- **Real-time Streaming**: Live AI response generation with typing indicators
- **CLI Metadata Extraction**: Command-line tool for batch processing 10,000+ PDFs and exporting metadata to CSV

### Advanced RAG Features

- **Smart Keyword Extraction**: Automatically identifies names, entities, and specific terms
- **Context-Aware Responses**: Leverages conversation history for follow-up questions
- **Source Attribution**: Shows which documents and pages information comes from
- **Fallback Mechanisms**: Multiple retrieval strategies ensure robust performance

### User Experience

- **Modern UI**: Built with shadcn/ui components and Radix UI primitives
- **Responsive Design**: Works seamlessly across desktop and mobile devices
- **PDF Preview**: In-browser document viewing capabilities
- **Dark/Light Theme**: Automatic theme switching with system preference detection

## 🛠 Tech Stack

### Frontend

- **React 18** with TypeScript for type-safe development
- **Vite** for fast development and optimized builds
- **shadcn/ui** + **Radix UI** for accessible, customizable components
- **TailwindCSS** for utility-first styling
- **React Router** for client-side navigation
- **React Query** for efficient data fetching and caching
- **React Hook Form** with Zod validation
- **Lucide React** for consistent iconography

### Backend

- **FastAPI** with automatic OpenAPI documentation
- **LangChain** for RAG pipeline orchestration
- **ChromaDB** for vector storage and similarity search
- **Sentence Transformers** for document embeddings
- **PyMuPDF** for robust PDF parsing
- **Supabase** for user authentication and metadata storage
- **NVIDIA API** with Llama 4 Maverick for language generation

### AI/ML Stack

- **LLM**: Meta Llama 4 Maverick (17B parameters) via NVIDIA API
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Vector Database**: ChromaDB with persistent storage
- **Hybrid Retrieval**: Custom implementation combining semantic + keyword search

## 📋 Prerequisites

- **Node.js** (v18+ recommended)
- **Python** (v3.9+)
- **NVIDIA API Key** (for LLM access)
- **Supabase Account** (for authentication)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/Sonlux/RAG.git
cd RAG
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the root directory:

```env
# --- SUPABASE CONFIG ---
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# --- LLM API ---
NVIDIA_API_KEY=your_nvidia_api_key
LLM_MODEL=meta/llama-4-maverick-17b-128e-instruct

# --- VECTOR DB ---
CHROMA_DB_DIR=chroma_db

# --- EMBEDDING MODEL ---
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# --- SYSTEM SETTINGS ---
DEFAULT_CHUNK_SIZE=800
DEFAULT_CHUNK_OVERLAP=200
API_HOST=0.0.0.0
API_PORT=8000
```

### 4. Start Backend Server

```bash
cd backend
uvicorn main:app --reload
```

Backend API will be available at http://localhost:8000

### 5. Frontend Setup

```bash
cd frontend
npm install

# Create frontend environment file
echo "VITE_API_BASE_URL=http://localhost:8000" > .env

# Start development server
npm run dev
```

Frontend will be available at http://localhost:5173

## 📁 Project Structure

```
RAG/
├── backend/
│   ├── api/                    # FastAPI route handlers
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── chat.py            # Chat and Q&A endpoints
│   │   ├── history.py         # Chat history management
│   │   ├── libraries.py       # Library CRUD operations
│   │   └── upload.py          # PDF upload and processing
│   ├── db/                    # Database configurations
│   ├── ingestion/             # PDF processing pipeline
│   │   ├── chunker.py         # Document chunking strategies
│   │   ├── embed_store.py     # Vector storage operations
│   │   └── pdf_loader.py      # PDF parsing utilities
│   ├── rag_pipeline/          # RAG implementation
│   │   ├── llm_interface.py   # LLM API integration
│   │   ├── memory_manager.py  # Chat history management
│   │   ├── rag_chain.py       # Main RAG orchestration
│   │   └── retriever.py       # Hybrid search implementation
│   └── main.py                # FastAPI application entry point
├── frontend/
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   │   ├── ui/           # shadcn/ui components
│   │   │   ├── CreateLibraryModal.tsx
│   │   │   ├── PDFList.tsx
│   │   │   └── PDFUploadZone.tsx
│   │   ├── contexts/         # React context providers
│   │   ├── hooks/            # Custom React hooks
│   │   ├── layouts/          # Page layout components
│   │   ├── pages/            # Main application pages
│   │   │   ├── Chat.tsx      # Chat interface
│   │   │   ├── Dashboard.tsx # Main dashboard
│   │   │   ├── History.tsx   # Chat history viewer
│   │   │   ├── LibraryView.tsx # Library management
│   │   │   └── Settings.tsx  # User settings
│   │   └── main.tsx          # React application entry point
│   ├── public/               # Static assets
│   └── package.json          # Frontend dependencies
├── chroma_db/                # Vector database storage
├── uploads/                  # Uploaded PDF storage
├── .env                      # Environment configuration
├── requirements.txt          # Python dependencies
└── README.md
```

## 🎯 Usage Guide

### Getting Started

1. **Create a Library**: Organize your documents by topic or project
2. **Upload PDFs**: Drag and drop or browse to upload documents
3. **Start Chatting**: Ask questions about your uploaded content
4. **Review History**: Access previous conversations and responses

### CLI Metadata Extraction

Extract metadata from large PDF collections:

```bash
# Extract metadata from all PDFs in a directory
cd backend
python cli_metadata_extractor.py -i ./documents -o metadata.csv

# Process 10,000 corporate documents
python cli_metadata_extractor.py -i /path/to/corporate_docs -o corporate_metadata.csv --verbose

# Extract from multiple files
python cli_metadata_extractor.py -i file1.pdf file2.pdf file3.pdf -o metadata.csv
```

**What gets extracted:**

- Creation date & modification date
- Author, title, subject
- File size & page count
- Internal links and annotations
- Creator & producer software

**See full documentation:** [`backend/CLI_METADATA_README.md`](backend/CLI_METADATA_README.md)

### Chat Modes

- **Library Mode**: Search across all documents in a library
- **Single PDF Mode**: Focus questions on a specific document

### Advanced Features

- **Follow-up Questions**: The system understands context and pronouns
- **Source Citations**: See exactly which documents provided information
- **Conversation Memory**: Maintains context across multiple exchanges

## 🔧 API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation.

### Key Endpoints

- `POST /upload` - Upload and process PDF documents
- `POST /chat` - Send questions and receive AI responses
- `GET /libraries` - List all document libraries
- `GET /history/{library}` - Retrieve chat history
- `POST /chat/new` - Create new chat session

## 🚀 Deployment

### Backend Deployment

```bash
# Build for production
pip install -r requirements.txt

# Run with production server
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Frontend Deployment

```bash
cd frontend
npm run build
# Deploy the dist/ folder to your hosting service
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- **NVIDIA** for providing powerful LLM APIs
- **LangChain** for the comprehensive RAG framework
- **ChromaDB** for efficient vector storage
- **Supabase** for backend-as-a-service platform
- **shadcn/ui** for beautiful, accessible UI components
- **Radix UI** for low-level UI primitives
- **Vercel** for the inspiration on modern web development

## 📊 Performance & Scalability

- **Hybrid Search**: Combines keyword and semantic search for 95%+ retrieval accuracy
- **Efficient Chunking**: Smart document segmentation preserves context
- **Streaming Responses**: Real-time AI response generation
- **Persistent Storage**: ChromaDB ensures fast similarity search at scale
- **Optimized Embeddings**: Lightweight model balances speed and accuracy

---

**Built with ❤️ for the AI community**
