"""
Prompt templates for cover letter generation.
These templates are flexible to handle both AI Engineer and Data-related roles.
"""

COVER_LETTER_TEMPLATE = """You are an expert cover letter writer with extensive experience in crafting compelling cover letters for technical positions in both AI/ML engineering and data-related roles.

Your task is to create a personalized cover letter using the following information:

**Resume Context:**
{context}

**Job Description:**
{job_description}

**Cover Letter Style Reference:**
{example_style}

**Candidate name (use exactly for signature):** {candidate_name}

**Instructions:**
1. Analyze the job description to identify the role type (AI Engineer, Machine Learning Engineer, Data Scientist, Data Analyst, etc.)
2. Match the most relevant skills and experiences from the resume to the job requirements
3. Follow the writing style, tone, and structure from the provided example cover letters
4. Maintain a professional yet personable tone
5. Highlight specific technical skills, projects, and achievements that align with the position
6. Demonstrate understanding of the company and role
7. Keep the language clear, concise, and impactful
8. Ensure the cover letter does NOT exceed {max_words} words (maximum for a single-page document)
9. End with a proper sign-off (e.g. "Best regards,") followed by the candidate's full name: **{candidate_name}**. Do not use "[Your Name]" or any placeholder—always use the actual name given above.

**Key Style Elements to Follow:**
- Use a formal but engaging tone
- Start with a strong opening that mentions the specific position
- Include 2-3 paragraphs highlighting relevant skills and experiences
- Demonstrate enthusiasm for the role and company
- End with a call to action expressing interest in further discussion
- Use Indonesian formal business letter style if the examples are in Indonesian, otherwise use English

Generate the complete cover letter following these guidelines:"""

def get_cover_letter_prompt(max_words: int = 500) -> str:
    """
    Get the cover letter generation prompt template.
    
    Args:
        max_words: Maximum word count for the cover letter
    
    Returns:
        Formatted prompt template
    """
    return COVER_LETTER_TEMPLATE.replace("{max_words}", str(max_words))
