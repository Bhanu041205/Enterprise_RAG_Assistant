# 🧠 Enterprise RAG Assistant

An AI-powered Enterprise Retrieval-Augmented Generation (RAG) Assistant designed to answer questions from internal organizational documents.

The system retrieves relevant information from company documents and uses Google Gemini to generate grounded answers based only on retrieved company knowledge.

---

## 🏢 Organization

**TechNova Solutions**

The project uses internal company policies and standard operating procedures as its knowledge base.

---

## 🎯 Objective

The objective is to build an intelligent enterprise assistant that allows employees to quickly search and understand internal company policies and procedures using natural-language questions.

Instead of manually searching through multiple documents, users can ask questions directly to the AI assistant.

---

## ✨ Key Features

- 🤖 AI-powered question answering
- 📚 Retrieval-Augmented Generation (RAG)
- 🔎 Semantic document search
- 🧠 Sentence Transformer embeddings
- ⚡ FAISS vector similarity search
- 💬 Google Gemini response generation
- 📄 Multiple DOCX company documents
- 🗂️ Document-specific pages
- 📚 Source cards with retrieved documents
- 📊 Relevance scores
- 🎨 Streamlit web interface

---

## 🏗️ System Architecture

```text
Company Documents (.docx)
        ↓
Document Loading
        ↓
Text Processing / Chunking
        ↓
Sentence Transformer
all-MiniLM-L6-v2
        ↓
FAISS Vector Index
        ↓
User Question
        ↓
Query Embedding
        ↓
FAISS Similarity Search
        ↓
Relevant Context + Sources
        ↓
Google Gemini
        ↓
Grounded AI Answer + Sources
```

---

## 🔄 RAG Pipeline

### 1. Document Collection

Company policies and SOP documents are stored as DOCX files.

### 2. Document Loading

Documents are loaded using `python-docx`.

### 3. Text Processing

Text is extracted and divided into searchable chunks.

### 4. Embedding Generation

Each chunk is converted into a numerical vector using:

`all-MiniLM-L6-v2`

### 5. Vector Storage

The embeddings are stored in a FAISS vector index.

The embedding dimension is **384**.

### 6. User Query

The employee enters a natural-language question.

Example:

`How many annual leave days are provided?`

### 7. Query Embedding

The question is converted into the same embedding space as the document chunks.

### 8. Similarity Search

FAISS searches for semantically relevant document chunks.

### 9. Context Retrieval

The retrieved passages are provided to the language model as context.

### 10. Answer Generation

Google Gemini generates the final response using the retrieved company information.

### 11. Source Display

The application displays:

- Document name
- Chunk ID
- Relevance score
- Retrieved passage count

---

## 🧰 Technologies Used

| Component | Technology |
|---|---|
| Programming Language | Python |
| Frontend | Streamlit |
| LLM | Google Gemini |
| Embeddings | Sentence Transformers |
| Embedding Model | all-MiniLM-L6-v2 |
| Vector Store | FAISS |
| Document Processing | python-docx |
| Numerical Processing | NumPy |
| Development | Google Colab / VS Code |
| Storage | Google Drive |

---

## 📁 Project Structure

```text
Enterprise_RAG_Assistant/
│
├── Data/
│   └── documents/
│       ├── Acceptable_Use_Policy.docx
│       ├── Attendance_Policy.docx
│       ├── Employee_Handbook.docx
│       ├── IT_Security_Policy.docx
│       ├── Leave_Policy.docx
│       ├── Procurement_SOP.docx
│       ├── Travel_Policy.docx
│       └── Work_From_Home_Policy.docx
│
├── src/
│   └── rag_engine.py
│
├── app/
│   └── app.py
│
├── vectorstore/
│   ├── tech_nova.index
│   └── chunks.pkl
│
├── requirements.txt
└── README.md
```

---

## 📄 Knowledge Base

The knowledge base currently contains 8 organizational documents:

1. Acceptable Use Policy
2. Attendance Policy
3. Employee Handbook
4. IT Security Policy
5. Leave Policy
6. Procurement SOP
7. Travel Policy
8. Work From Home Policy

---

## 🚀 Installation

Clone the repository:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Enterprise_RAG_Assistant
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🔑 Gemini API Configuration

The application requires a Google Gemini API key.

Windows PowerShell:

```powershell
$env:GEMINI_API_KEY="YOUR_API_KEY"
```

Linux / macOS:

```bash
export GEMINI_API_KEY="YOUR_API_KEY"
```

**Never commit the API key to GitHub.**

For deployment platforms, configure the key using environment variables or secret management.

---

## ▶️ Run the Application

From the project root:

```bash
streamlit run app/app.py
```

---

## 💬 Example Questions

### Leave Policy

`How many annual leave days are provided?`

### Work From Home

`What is the work from home policy?`

### Attendance

`What are the attendance requirements?`

### Travel

`What is the company's travel policy?`

### IT Security

`What are the IT security requirements?`

---

## 🔎 Source Transparency

Each generated answer can display its retrieved sources.

The source information includes:

- 📄 Document name
- 🔹 Chunk ID
- 📊 Relevance score
- 📚 Retrieved passage count

This provides traceability between the generated response and the internal company knowledge base.

---

## 🛡️ Grounded Answering

The RAG prompt instructs the language model to answer using retrieved company documents rather than unrelated external knowledge.

If relevant information cannot be found, the system can return:

`This information is not available in the provided company documents.`

This helps reduce unsupported answers and hallucinations.

---

## ⚙️ Current Configuration

```text
Embedding Model: all-MiniLM-L6-v2
Embedding Dimension: 384
Vector Store: FAISS
LLM: gemini-3.5-flash-lite
Relevance Threshold: 0.20
```

---

## 🔮 Future Improvements

- 🔐 Enterprise authentication
- 👥 Role-based access control
- 🗄️ Production vector database
- 📊 Admin dashboard
- 📝 PDF support
- 📑 Additional document formats
- 💾 Conversation persistence
- 📈 RAG evaluation metrics
- 🔍 Hybrid search
- 🧠 Reranking models
- ☁️ Cloud deployment
- 🔄 Automatic document ingestion
- 📌 Document version management
- 🔒 Enterprise-level data security

---

## 📌 Project Status

- ✅ Document ingestion
- ✅ Embedding generation
- ✅ FAISS vector search
- ✅ RAG retrieval
- ✅ Gemini generation
- ✅ Source tracking
- ✅ Document-specific filtering
- ✅ Streamlit frontend
- ✅ Document-specific pages
- ✅ requirements.txt
- 🔄 VS Code setup
- 🔄 GitHub repository
- 🔄 Deployment

---

## 📜 License

This project is developed for educational and demonstration purposes.
