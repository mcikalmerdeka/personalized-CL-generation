import os
from pathlib import Path
import gradio as gr
from dotenv import load_dotenv

from src.config.logging_config import setup_logger
from src.config.settings import RESUMES_DIR, VECTOR_STORES_DIR, CANDIDATE_NAME
from src.core.generator import CoverLetterGenerator
from src.core.chatbot import EmployerQAChatbot

# Load environment variables
load_dotenv()

logger = setup_logger(__name__)


class ApplyCopilotUI:
    """Gradio UI for ApplyCopilot - Cover Letter Generation and Employer Q&A."""
    
    def __init__(self):
        """Initialize the UI and components."""
        self.generator = CoverLetterGenerator()
        self.chatbot = EmployerQAChatbot(self.generator.vector_store_manager)
        
        # Shared state
        self.current_resume_type = None
        self.job_details = {
            "company_name": "",
            "job_title": "",
            "job_description": ""
        }
        
        logger.info("Initialized ApplyCopilotUI")
    
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
    
    def update_job_details(self, company_name: str, job_title: str, job_description: str) -> str:
        """
        Update shared job details for both features.
        
        Args:
            company_name: Name of the company
            job_title: Job title/position
            job_description: Full job description
        
        Returns:
            Status message
        """
        try:
            self.job_details["company_name"] = company_name
            self.job_details["job_title"] = job_title
            self.job_details["job_description"] = job_description
            
            # Update chatbot with job context if available
            if company_name or job_title:
                job_context = f"Position: {job_title} at {company_name}" if job_title and company_name else f"Position: {job_title or company_name}"
                self.chatbot.set_job_context(job_context, job_description)
            
            logger.info(f"Updated job details: {job_title} at {company_name}")
            return f"✅ Job details updated: {job_title} at {company_name}"
            
        except Exception as e:
            error_msg = f"❌ Error updating job details: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def generate_cover_letter(self, output_format: str) -> tuple:
        """
        Generate a cover letter using shared job details.
        
        Args:
            output_format: Output format ('txt' or 'pdf')
        
        Returns:
            Tuple of (cover letter text, file path, status message)
        """
        try:
            # Validate inputs
            if not self.job_details["company_name"] or not self.job_details["job_title"] or not self.job_details["job_description"]:
                return "", None, "❌ Please fill in all job details in the Setup section"
            
            if self.current_resume_type is None:
                return "", None, "❌ Please index a resume first in the Setup section"
            
            # Generate cover letter
            logger.info(f"Generating cover letter for {self.job_details['company_name']} - {self.job_details['job_title']}")
            cover_letter = self.generator.generate_cover_letter(
                job_description=self.job_details["job_description"],
                company_name=self.job_details["company_name"],
                job_title=self.job_details["job_title"]
            )
            
            # Save cover letter
            file_path = self.generator.save_cover_letter(
                cover_letter=cover_letter,
                company_name=self.job_details["company_name"],
                job_title=self.job_details["job_title"],
                format=output_format
            )
            
            success_msg = f"✅ Cover letter generated and saved to: {file_path}"
            logger.info(success_msg)
            
            return cover_letter, file_path, success_msg
            
        except Exception as e:
            error_msg = f"❌ Error generating cover letter: {str(e)}"
            logger.error(error_msg)
            return "", None, error_msg
    
    def create_setup_section(self) -> gr.Row:
        """Create the shared Setup section with Resume selection and Job Details."""
        with gr.Row() as setup_row:
            with gr.Column(scale=1):
                gr.Markdown("### 📋 Step 1: Select Resume Type")
                resume_type = gr.Radio(
                    choices=["AI Engineer", "Data Related"],
                    label="Resume Type",
                    value="Data Related"
                )
                index_btn = gr.Button("📁 Index Resume", variant="primary")
                index_status = gr.Textbox(
                    label="Resume Status",
                    value="No resume indexed yet. Please select and index a resume.",
                    interactive=False
                )
            
            with gr.Column(scale=2):
                gr.Markdown("### 🎯 Step 2: Enter Job Details (Shared for Both Features)")
                gr.Markdown("*These details will be used for both Cover Letter generation and Employer Q&A*")
                
                with gr.Row():
                    company_name = gr.Textbox(
                        label="Company Name",
                        placeholder="e.g., PT Example Company",
                        scale=1
                    )
                    job_title = gr.Textbox(
                        label="Job Title",
                        placeholder="e.g., Senior Data Analyst",
                        scale=1
                    )
                
                job_description = gr.Textbox(
                    label="Job Description",
                    placeholder="Paste the full job description here...",
                    lines=5
                )
                
                update_job_btn = gr.Button("💾 Save Job Details", variant="secondary")
                job_status = gr.Textbox(
                    label="Job Details Status",
                    value="No job details saved yet.",
                    interactive=False
                )
        
        # Event handlers for setup section
        index_btn.click(
            fn=self.index_resume,
            inputs=[resume_type],
            outputs=[index_status]
        )
        
        update_job_btn.click(
            fn=self.update_job_details,
            inputs=[company_name, job_title, job_description],
            outputs=[job_status]
        )
        
        return setup_row
    
    def create_cover_letter_tab(self) -> gr.Tab:
        """Create the Cover Letter Generation tab."""
        with gr.Tab("📝 Cover Letter Generator", id="cover_letter") as tab:
            gr.Markdown("## Generate tailored cover letters using AI based on your resume and job details.")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### ⚙️ Generation Settings")
                    output_format = gr.Radio(
                        choices=["txt", "pdf"],
                        label="Output Format",
                        value="txt"
                    )
                    generate_btn = gr.Button("✨ Generate Cover Letter", variant="primary")
            
            gr.Markdown("---")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 📄 Generated Cover Letter")
                    generation_status = gr.Textbox(label="Generation Status", interactive=False)
                    cover_letter_output = gr.Textbox(
                        label="Generated Cover Letter",
                        lines=15,
                        interactive=False
                    )
                    file_output = gr.File(label="Download Cover Letter")
            
            # Event handlers
            generate_btn.click(
                fn=self.generate_cover_letter,
                inputs=[output_format],
                outputs=[cover_letter_output, file_output, generation_status]
            )
        
        return tab
    
    def create_employer_qa_tab(self) -> gr.Tab:
        """Create the Employer Q&A Chatbot tab."""
        with gr.Tab("💬 Employer Q&A Assistant", id="employer_qa") as tab:
            gr.Markdown(f"## Chat with employers on behalf of {CANDIDATE_NAME}")
            gr.Markdown(
                "Answer questions from recruiters and hiring managers based on your indexed resume and job details. "
                "The AI assistant will provide professional responses using your background information."
            )
            
            # Show current context
            with gr.Row():
                with gr.Column(scale=1):
                    qa_context_status = gr.Textbox(
                        label="Current Context",
                        value="No context loaded. Please complete Step 1 and 2 in the Setup section above.",
                        interactive=False
                    )
            
            gr.Markdown("---")
            
            # Chat Interface
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 💬 Chat with Employers")
                    
                    chatbot = gr.Chatbot(
                        label="Conversation",
                        height=500,
                        placeholder="Start a conversation with potential employers..."
                    )
                    
                    with gr.Row():
                        msg_input = gr.Textbox(
                            label="Your Message",
                            placeholder="Type employer's question here or ask a practice question...",
                            scale=7,
                            show_label=False
                        )
                        submit_btn = gr.Button("Send", variant="primary", scale=1)
                    
                    with gr.Row():
                        clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary")
                        save_btn = gr.Button("💾 Save Conversation", variant="secondary")
            
            # Chat status
            chat_status = gr.Textbox(label="Chat Status", interactive=False, visible=False)
            
            # Chat examples
            gr.Markdown("### 💡 Example Questions You Might Receive")
            gr.Examples(
                examples=[
                    "Can you tell me about your experience with machine learning?",
                    "What projects have you worked on related to data analysis?",
                    "Are you familiar with Python and its data science libraries?",
                    "What is your experience with cloud platforms like AWS or GCP?",
                    "Can you describe a challenging technical problem you've solved?",
                    "What is your educational background?",
                    "Are you comfortable working in a team environment?",
                    "What are your salary expectations?",
                    "When would you be available to start?",
                ],
                inputs=[msg_input],
                label="Click any example to use it"
            )
            
            # Event handlers
            def respond(message, history):
                if not message.strip():
                    return "", history
                
                if self.current_resume_type is None:
                    history.append({"role": "assistant", "content": "❌ Please load a resume first by completing Step 1 in the Setup section."})
                    return "", history
                
                try:
                    response = self.chatbot.chat(message, history)
                    history.append({"role": "user", "content": message})
                    history.append({"role": "assistant", "content": response})
                    return "", history
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    history.append({"role": "user", "content": message})
                    history.append({"role": "assistant", "content": error_msg})
                    return "", history
            
            def clear_chat():
                self.chatbot.clear_history()
                return []
            
            def update_qa_context():
                """Update the context status display."""
                if self.current_resume_type is None:
                    return "❌ No resume indexed. Please complete Step 1 in the Setup section."
                
                context_info = f"✅ Resume: {self.current_resume_type}"
                if self.job_details.get("job_title"):
                    context_info += f" | Job: {self.job_details['job_title']}"
                if self.job_details.get("company_name"):
                    context_info += f" at {self.job_details['company_name']}"
                
                return context_info
            
            # Update context status when tab is opened
            tab.select(
                fn=update_qa_context,
                outputs=[qa_context_status]
            )
            
            submit_btn.click(
                fn=respond,
                inputs=[msg_input, chatbot],
                outputs=[msg_input, chatbot]
            )
            
            msg_input.submit(
                fn=respond,
                inputs=[msg_input, chatbot],
                outputs=[msg_input, chatbot]
            )
            
            clear_btn.click(
                fn=clear_chat,
                outputs=[chatbot]
            )
        
        return tab
    
    def create_interface(self) -> gr.Blocks:
        """Create and return the Gradio interface with shared setup and tabs."""
        
        with gr.Blocks(title="ApplyCopilot - Your AI Job Application Assistant") as interface:
            gr.Markdown("# 🤖 ApplyCopilot")
            gr.Markdown(
                "**Your intelligent job application assistant.** "
                "Generate personalized cover letters and answer employer questions based on your resume."
            )
            
            # Setup Section (Shared across all features)
            with gr.Column():
                gr.Markdown("## 🔧 Setup")
                gr.Markdown("*Complete these steps first. Your selections will be shared across all features.*")
                self.create_setup_section()
            
            gr.Markdown("---")
            
            # Feature Tabs
            gr.Markdown("## 🚀 Features")
            with gr.Tabs():
                self.create_cover_letter_tab()
                self.create_employer_qa_tab()
            
            gr.Markdown("---")
            gr.Markdown(
                f"*Powered by AI • Built for {CANDIDATE_NAME}*"
            )
        
        return interface
    
    def launch(self, **kwargs):
        """Launch the Gradio interface."""
        interface = self.create_interface()
        interface.launch(theme=gr.themes.Soft(), **kwargs)


def main():
    """Main entry point for the UI."""
    ui = ApplyCopilotUI()
    ui.launch(share=False, server_name="127.0.0.1", server_port=7860)


if __name__ == "__main__":
    main()
