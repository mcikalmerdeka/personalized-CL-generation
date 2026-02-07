import os
from pathlib import Path
import gradio as gr
from dotenv import load_dotenv

from src.config.logging_config import setup_logger
from src.config.settings import RESUMES_DIR, VECTOR_STORES_DIR
from src.core.generator import CoverLetterGenerator

# Load environment variables
load_dotenv()

logger = setup_logger(__name__)


class CoverLetterUI:
    """Gradio UI for the cover letter generator."""
    
    def __init__(self):
        """Initialize the UI and generator."""
        self.generator = CoverLetterGenerator()
        self.current_resume_type = None
        logger.info("Initialized CoverLetterUI")
    
    def index_resume(self, resume_type: str) -> str:
        """
        Index a resume and create/load vector store.
        
        Args:
            resume_type: Type of resume ('AI Engineer' or 'Data Related')
        
        Returns:
            Status message
        """
        try:
            # Map resume type to file
            resume_files = {
                "AI Engineer": "ai_engineer_resume.pdf",
                "Data Related": "data_related_resume.pdf"
            }
            
            if resume_type not in resume_files:
                return f"❌ Invalid resume type: {resume_type}"
            
            resume_path = Path(RESUMES_DIR) / resume_files[resume_type]
            vector_store_path = Path(VECTOR_STORES_DIR) / resume_type.lower().replace(" ", "_")
            
            # Check if vector store exists
            if vector_store_path.exists():
                logger.info(f"Loading existing vector store for {resume_type}")
                self.generator.vector_store_manager.load_vector_store(str(vector_store_path))
                message = f"✅ Loaded existing vector store for {resume_type}"
            else:
                logger.info(f"Creating new vector store for {resume_type}")
                self.generator.vector_store_manager.load_and_index_resume(str(resume_path))
                self.generator.vector_store_manager.save_vector_store(str(vector_store_path))
                message = f"✅ Created and saved vector store for {resume_type}"
            
            # Load cover letter examples
            self.generator.load_cover_letter_examples()
            self.current_resume_type = resume_type
            
            logger.info(message)
            return message
            
        except Exception as e:
            error_msg = f"❌ Error indexing resume: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def generate_cover_letter(self, company_name: str, job_title: str, 
                            job_description: str, output_format: str) -> tuple:
        """
        Generate a cover letter.
        
        Args:
            company_name: Name of the company
            job_title: Job title/position
            job_description: Full job description
            output_format: Output format ('txt' or 'pdf')
        
        Returns:
            Tuple of (cover letter text, file path, status message)
        """
        try:
            # Validate inputs
            if not company_name or not job_title or not job_description:
                return "", None, "❌ Please fill in all fields"
            
            if self.current_resume_type is None:
                return "", None, "❌ Please index a resume first"
            
            # Generate cover letter
            logger.info(f"Generating cover letter for {company_name} - {job_title}")
            cover_letter = self.generator.generate_cover_letter(
                job_description=job_description,
                company_name=company_name,
                job_title=job_title
            )
            
            # Save cover letter
            file_path = self.generator.save_cover_letter(
                cover_letter=cover_letter,
                company_name=company_name,
                job_title=job_title,
                format=output_format
            )
            
            success_msg = f"✅ Cover letter generated and saved to: {file_path}"
            logger.info(success_msg)
            
            return cover_letter, file_path, success_msg
            
        except Exception as e:
            error_msg = f"❌ Error generating cover letter: {str(e)}"
            logger.error(error_msg)
            return "", None, error_msg
    
    def create_interface(self) -> gr.Blocks:
        """Create and return the Gradio interface."""
        
        with gr.Blocks(title="Cover Letter Generator") as interface:
            gr.Markdown("# 📝 Personalized Cover Letter Generator")
            gr.Markdown("Generate tailored cover letters using AI based on your resume and job descriptions.")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("## Step 1: Select Resume Type")
                    resume_type = gr.Radio(
                        choices=["AI Engineer", "Data Related"],
                        label="Resume Type",
                        value="Data Related"
                    )
                    index_btn = gr.Button("📁 Index Resume", variant="primary")
                    index_status = gr.Textbox(label="Indexing Status", interactive=False)
            
            gr.Markdown("---")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("## Step 2: Enter Job Details")
                    company_name = gr.Textbox(
                        label="Company Name",
                        placeholder="e.g., PT Example Company"
                    )
                    job_title = gr.Textbox(
                        label="Job Title",
                        placeholder="e.g., Senior Data Analyst"
                    )
                    job_description = gr.Textbox(
                        label="Job Description",
                        placeholder="Paste the full job description here...",
                        lines=10
                    )
                    
                    with gr.Row():
                        output_format = gr.Radio(
                            choices=["txt", "pdf"],
                            label="Output Format",
                            value="txt"
                        )
                        generate_btn = gr.Button("✨ Generate Cover Letter", variant="primary", scale=2)
            
            gr.Markdown("---")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("## Step 3: Review and Download")
                    generation_status = gr.Textbox(label="Generation Status", interactive=False)
                    cover_letter_output = gr.Textbox(
                        label="Generated Cover Letter",
                        lines=15,
                        interactive=False
                    )
                    file_output = gr.File(label="Download Cover Letter")
            
            # Event handlers
            index_btn.click(
                fn=self.index_resume,
                inputs=[resume_type],
                outputs=[index_status]
            )
            
            generate_btn.click(
                fn=self.generate_cover_letter,
                inputs=[company_name, job_title, job_description, output_format],
                outputs=[cover_letter_output, file_output, generation_status]
            )
            
            gr.Markdown("---")
        
        return interface
    
    def launch(self, **kwargs):
        """Launch the Gradio interface."""
        interface = self.create_interface()
        interface.launch(theme=gr.themes.Soft(), **kwargs)


def main():
    """Main entry point for the UI."""
    ui = CoverLetterUI()
    ui.launch(share=False, server_name="127.0.0.1", server_port=7860)


if __name__ == "__main__":
    main()
