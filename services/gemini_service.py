from google import genai
import config

class GeminiService:
    def __init__(self):
        if not config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set")
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        self.model_id = 'gemini-3-flash-preview'

    def summarize_repo(self, repo_details):
        """Summarize repository details using Gemini."""
        prompt = f"""
        Please provide a concise summary of the following GitHub repository based on its details and README:
        
        Repository: {repo_details['name']}
        Description: {repo_details['description']}
        Primary Language: {repo_details['language']}
        
        README Content:
        {repo_details['readme'][:2000]}  # Limiting readme for prompt size
        
        Summary:
        """
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )
        return response.text

    def analyze_quality(self, commits):
        """Analyze code quality based on commit messages and metadata."""
        if not commits:
            return "No activity to analyze."
            
        commit_summary = "\n".join([f"Repo: {c['repo']} | Msg: {c['message']}" for c in commits])
        prompt = f"""
        Analyze the following commit activity from the past 7 days and provide a high-level assessment of the code quality and development focus.
        
        Commit Data:
        {commit_summary}
        
        Please provide:
        1. **Code Quality Assessment**: Based on the clarity and descriptiveness of commit messages.
        2. **Development Focus**: What has the user been primarily working on?
        3. **Suggestions**: One or two tips for improvement.
        
        Keep it professional and encouraging.
        """
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )
        return response.text
