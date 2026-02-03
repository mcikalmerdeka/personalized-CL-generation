# AI-Powered Cover Letter Generator

An intelligent tool that creates tailored cover letters for specific job openings by analyzing user-provided resumes/CVs and preferred writing styles, generating personalized content that aligns perfectly with targeted job descriptions.

## 🚀 Features

- **Dual Resume Support**: Supports both AI Engineer and Data-related role resumes
- **Resume Analysis**: Automatically extracts relevant skills and experiences using FAISS vector search
- **Style Matching**: Learns from multiple cover letter examples to maintain consistent writing style
- **Job-Specific Customization**: Tailors content to match specific job requirements
- **Web Interface**: User-friendly Gradio interface for easy interaction
- **PDF & Text Export**: Creates professional documents in multiple formats
- **Multiple AI Models**: Supports both OpenAI (GPT-4o) and Anthropic (Claude) models
- **Persistent Vector Storage**: FAISS-based indexing with local persistence

## 🛠️ Implementation Details

- Built with **LangChain** for document processing and LLM integration
- Uses **FAISS** for efficient vector storage and semantic search
- Leverages **OpenAI Embeddings** for text analysis (text-embedding-3-small)
- **Gradio** web interface for user interaction
- Implements **ReportLab** for PDF document generation
- **Centralized Logging** for application monitoring
- Modular architecture with clean separation of concerns

## 🧩 How It Works

1. **Document Processing**:
   - Loads your resume from PDF
   - Splits content into manageable chunks
   - Creates vector embeddings for semantic search

2. **Style Learning**:
   - Analyzes your existing cover letter for tone and format
   - Extracts structural elements and writing patterns

3. **Content Generation**:
   - Retrieves relevant resume sections based on job description
   - Generates tailored content using LLM (GPT-4o or Claude)
   - Maintains your personal writing style and format

4. **PDF Creation**:
   - Formats content with professional styling
   - Outputs a ready-to-submit PDF document

## 📋 Requirements

- Python 3.12+
- OpenAI API key for embeddings and generation
- (Optional) Anthropic API key for Claude models
- Required Python packages (see requirements.txt)

## 🔧 Setup

1. Clone this repository:

```bash
git clone https://github.com/mcikalmerdeka/personalized-CL-generation
cd personalized-CL-generation
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
   ANTHROPIC_API_KEY=your_anthropic_api_key  # Optional
   ```
5. Ensure your documents are in place:
   - Resumes: `data/resumes/` (ai_engineer_resume.pdf, data_related_resume.pdf)
   - Cover letter examples: `data/cover_letter_examples/` (example PDFs)
6. **(Optional)** Set your name for the cover letter signature in `src/config/settings.py`:
   - Edit `CANDIDATE_NAME = "Muhammad Cikal Merdeka"` to your full name so generated letters are signed correctly this is done because sometimes your name actually not included in the top-k results of the FAISS vector store retrieval process.

## 🚀 Usage

### Starting the Application

Simply run the main application file:

```bash
uv run app.py
```

This will launch the Gradio web interface at `http://127.0.0.1:7860`

### Using the Web Interface

1. **Select Resume Type**: Choose between "AI Engineer" or "Data Related" resume
2. **Index Resume**: Click "Index Resume" to create/load the vector store
3. **Enter Job Details**:
   - Company Name
   - Job Title
   - Full Job Description
4. **Generate**: Click "Generate Cover Letter" to create your personalized cover letter
5. **Download**: Download the generated cover letter in TXT or PDF format

### Programmatic Usage

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

## 📊 Project Structure

```
├── app.py                         # Main application entry point
├── src/
│   ├── config/
│   │   ├── settings.py            # Application configuration (paths, model, CANDIDATE_NAME)
│   │   ├── logging_config.py      # Centralized logging setup
│   │   └── prompts.py             # LLM prompt templates
│   ├── core/
│   │   ├── generator.py           # Cover letter generation logic
│   │   └── vector_store.py        # FAISS vector store management
│   └── ui/
│       └── gradio_interface.py    # Gradio web interface
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
- The quality of generated cover letters depends on:
  - The completeness of your resume
  - The quality of your existing cover letter template
  - The specificity of the job description

## 🔒 Privacy

- All processing happens through API calls to OpenAI/Anthropic
- Your resume and cover letter data will be sent to these services
- Generated content is stored locally in the `data/output/` directory
