# ApplyCopilot - Your AI Job Application Assistant

An intelligent tool that helps you throughout your job application process. ApplyCopilot creates tailored cover letters for specific job openings and helps you answer employer questions based on your resume, powered by AI.

## 🚀 Features

### 📝 Cover Letter Generator
- **Dual Resume Support**: Supports both AI Engineer and Data-related role resumes
- **Resume Analysis**: Automatically extracts relevant skills and experiences using FAISS vector search
- **Style Matching**: Learns from multiple cover letter examples to maintain consistent writing style
- **Job-Specific Customization**: Tailors content to match specific job requirements
- **PDF & Text Export**: Creates professional documents in multiple formats

### 💬 Employer Q&A Assistant
- **Interactive Chatbot**: Answer employer and recruiter questions based on your indexed resume
- **Context-Aware Responses**: Uses RAG (Retrieval-Augmented Generation) to provide accurate answers from your resume
- **Professional Tone**: Maintains a professional and helpful tone in all responses
- **Practice Mode**: Includes example questions to help you prepare for interviews
- **Persistent Chat**: Clear and restart conversations as needed

### 🎨 User Interface
- **Tabbed Interface**: Easy switching between Cover Letter Generator and Employer Q&A modes
- **Web-Based**: User-friendly Gradio interface accessible in your browser
- **Real-time Feedback**: Status messages and progress indicators

## 🛠️ Implementation Details

- Built with **LangChain** for document processing and LLM integration
- Uses **FAISS** for efficient vector storage and semantic search
- Leverages **OpenAI Embeddings** for text analysis (text-embedding-3-small)
- **GPT-4o Mini** for cover letter generation and chat responses
- **Gradio** web interface with tabbed navigation
- Implements **ReportLab** for PDF document generation
- **Centralized Logging** for application monitoring
- Modular architecture with clean separation of concerns

## 🧩 How It Works

### Cover Letter Generation
1. **Document Processing**:
   - Loads your resume from PDF
   - Splits content into manageable chunks
   - Creates vector embeddings for semantic search

2. **Style Learning**:
   - Analyzes your existing cover letters for tone and format
   - Extracts structural elements and writing patterns

3. **Content Generation**:
   - Retrieves relevant resume sections based on job description
   - Generates tailored content using LLM (GPT-4o Mini)
   - Maintains your personal writing style and format

4. **Document Creation**:
   - Formats content with professional styling
   - Outputs a ready-to-submit PDF or TXT document

### Employer Q&A Assistant
1. **Resume Indexing**:
   - Indexes your resume into a searchable vector store
   - Creates semantic embeddings for efficient retrieval

2. **Question Answering**:
   - Retrieves relevant context from your resume based on the question
   - Generates professional responses using the retrieved information
   - Maintains conversation history for context-aware responses

3. **Interactive Chat**:
   - Real-time chat interface with employers/recruiters
   - Example questions to practice your responses
   - Easy conversation management (clear, save)

## 📋 Requirements

- Python 3.12+
- OpenAI API key for embeddings and generation
- Required Python packages (see requirements.txt)

## 🔧 Setup

1. Clone this repository:

```bash
git clone https://github.com/mcikalmerdeka/ApplyCopilot
cd ApplyCopilot
```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   # Or using uv:
   uv add -r requirements.txt
   ```
4. Create a `.env` file with your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   ```
5. Ensure your documents are in place:
   - Resumes: `data/resumes/` (ai_engineer_resume.pdf, data_related_resume.pdf)
   - Cover letter examples: `data/cover_letter_examples/` (example PDFs)
6. **(Optional)** Set your name in `src/config/settings.py`:
   - Edit `CANDIDATE_NAME = "Muhammad Cikal Merdeka"` to your full name for proper signature in generated cover letters

## 🚀 Usage

### Starting the Application

Simply run the main application file:

```bash
uv run app.py
```

This will launch the Gradio web interface at `http://127.0.0.1:7860`

### Using the Web Interface

#### Tab 1: 📝 Cover Letter Generator

1. **Select Resume Type**: Choose between "AI Engineer" or "Data Related" resume
2. **Index Resume**: Click "Index Resume" to create/load the vector store
3. **Enter Job Details**:
   - Company Name
   - Job Title
   - Full Job Description
4. **Generate**: Click "Generate Cover Letter" to create your personalized cover letter
5. **Download**: Download the generated cover letter in TXT or PDF format

#### Tab 2: 💬 Employer Q&A Assistant

1. **Select Resume Type**: Choose which resume to use for answering questions
2. **Load Resume**: Click "Load Resume" to index your resume for the chatbot
3. **Start Chatting**:
   - Type employer questions in the chat box
   - Or click on example questions to practice
   - The AI will answer based on your resume content
4. **Manage Conversations**:
   - Use "Clear Chat" to start a new conversation
   - Review your chat history for reference

### Example Use Cases

**Cover Letter Generation**:
```python
from src.core.generator import CoverLetterGenerator
from src.core.vector_store import VectorStoreManager

# Initialize components
generator = CoverLetterGenerator()
vector_store = VectorStoreManager()

# Load and index resume
vector_store.load_and_index_resume("data/resumes/data_related_resume.pdf")
vector_store.save_vector_store("data/vector_stores/data_related")

# Assign to generator
generator.vector_store_manager = vector_store

# Load examples
generator.load_cover_letter_examples()

# Generate cover letter
cover_letter = generator.generate_cover_letter(
    job_description="Your job description here...",
    company_name="Company Name",
    job_title="Position Title"
)

# Save output
file_path = generator.save_cover_letter(
    cover_letter,
    company_name="Company Name",
    job_title="Position Title",
    format="pdf"  # or "txt"
)
```

**Employer Q&A Chatbot**:
```python
from src.core.chatbot import EmployerQAChatbot
from src.core.vector_store import VectorStoreManager

# Initialize components
vector_store = VectorStoreManager()
vector_store.load_and_index_resume("data/resumes/ai_engineer_resume.pdf")

chatbot = EmployerQAChatbot(vector_store)

# Answer employer questions
response = chatbot.chat(
    message="What is your experience with Python?",
    history=[]  # Previous conversation history
)
print(response)
```

## 📊 Project Structure

```
├── app.py                         # Main application entry point
├── src/
│   ├── config/
│   │   ├── settings.py            # Application configuration (paths, model, CANDIDATE_NAME)
│   │   ├── logging_config.py      # Centralized logging setup
│   │   └── prompts.py             # LLM prompt templates (cover letter + Q&A)
│   ├── core/
│   │   ├── generator.py           # Cover letter generation logic
│   │   ├── chatbot.py             # Employer Q&A chatbot handler
│   │   └── vector_store.py        # FAISS vector store management
│   └── ui/
│       └── gradio_interface.py    # Gradio web interface with tabs
├── data/
│   ├── resumes/                   # Resume PDF files
│   ├── cover_letter_examples/     # Example cover letters
│   ├── vector_stores/             # FAISS indices (auto-generated)
│   └── output/                    # Generated cover letters
├── requirements.txt               # Python dependencies
├── pyproject.toml                 # Project metadata
└── README.md                      # This file
```

## ⚠️ Considerations

- Ensure your `.env` file with API keys is not committed to version control
- The quality of generated content depends on:
  - The completeness of your resume
  - The quality of your existing cover letter templates
  - The specificity of the job description
- The chatbot can only answer questions based on information present in your indexed resume

## 🔒 Privacy

- All processing happens through API calls to OpenAI
- Your resume and cover letter data will be sent to OpenAI services
- Generated content and chat conversations are stored locally
- No data is retained on external servers beyond the API calls

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

---

**Made with ❤️ by Muhammad Cikal Merdeka**
