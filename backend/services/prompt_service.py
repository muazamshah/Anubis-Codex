from typing import Any, Dict, List, Optional


class PromptService:
    """Prompt engine for Phase 3 chat system."""
    
    SYSTEM_PROMPT = """You are ANUBIS CODEX, an expert software engineer and repository intelligence assistant.

Your responsibilities:
- Answer questions using ONLY the provided repository information
- Never hallucinate or invent functions, files, or code
- Never provide information not found in the repository context
- Always provide file references with line numbers when possible
- Answer as an experienced software engineer with deep technical knowledge
- If information is unavailable, clearly state: "I could not find enough information inside the repository."

Response guidelines:
- Be concise and technical
- Include specific file paths and line numbers
- Explain code functionality when asked
- Identify potential issues or bugs when relevant
- Provide context-aware answers based on repository structure
"""

    def build_prompt(self, 
                     question: str, 
                     context: str,
                     chat_history: Optional[List[Dict[str, Any]]] = None,
                     repository_info: Optional[Dict[str, Any]] = None) -> str:
        """
        Build the complete prompt for the LLM.
        
        Structure:
        1. System prompt
        2. Repository information
        3. Chat history (if any)
        4. Retrieved context
        5. User question
        """
        prompt_parts = []
        
        # 1. System prompt
        prompt_parts.append(self.SYSTEM_PROMPT)
        prompt_parts.append("\n" + "="*80 + "\n")
        
        # 2. Repository information
        if repository_info:
            prompt_parts.append("REPOSITORY INFORMATION:\n")
            if repository_info.get("name"):
                prompt_parts.append(f"Repository: {repository_info['name']}\n")
            if repository_info.get("description"):
                prompt_parts.append(f"Description: {repository_info['description']}\n")
            if repository_info.get("languages"):
                prompt_parts.append(f"Languages: {', '.join(repository_info['languages'])}\n")
            if repository_info.get("topics"):
                prompt_parts.append(f"Topics: {', '.join(repository_info['topics'])}\n")
            prompt_parts.append("\n" + "="*80 + "\n")
        
        # 3. Chat history
        if chat_history and len(chat_history) > 0:
            prompt_parts.append("CONVERSATION HISTORY:\n")
            for msg in chat_history[-10:]:  # Last 10 messages
                role = msg.get("role", "user")
                content = msg.get("content", "")
                prompt_parts.append(f"{role.upper()}: {content}\n")
            prompt_parts.append("\n" + "="*80 + "\n")
        
        # 4. Retrieved context
        if context and context != "No relevant information found.":
            prompt_parts.append("RETRIEVED CODE CONTEXT:\n")
            prompt_parts.append(context)
            prompt_parts.append("\n" + "="*80 + "\n")
        
        # 5. User question
        prompt_parts.append("USER QUESTION:\n")
        prompt_parts.append(question)
        prompt_parts.append("\n\n")
        prompt_parts.append("ANSWER:\n")
        
        return "".join(prompt_parts)
    
    def build_simple_prompt(self, question: str, context: str) -> str:
        """Build a simple prompt without history."""
        return self.build_prompt(question, context)
    
    def optimize_query(self, question: str) -> str:
        """
        Optimize user query for better retrieval.
        
        Examples:
        - "Explain auth" -> "Explain the authentication system"
        - "How does login work?" -> "How does the login system work?"
        """
        # Abbreviation expansions
        expansions = {
            "auth": "authentication",
            "config": "configuration",
            "db": "database",
            "repo": "repository",
            "util": "utility",
            "impl": "implementation",
            "mgr": "manager",
            "svc": "service",
            "ctrl": "controller",
            "hdlr": "handler",
        }
        
        optimized = question
        words = question.lower().split()
        
        for word, expansion in expansions.items():
            if word in words:
                optimized = optimized.replace(word, expansion)
        
        return optimized
    
    def build_citation_prompt(self, question: str, context: str, sources: List[Dict[str, Any]]) -> str:
        """Build prompt with explicit citation instructions."""
        base_prompt = self.build_prompt(question, context)
        
        citation_instruction = """
IMPORTANT: When answering, always cite your sources using this format:
[Source: filename.py, lines X-Y]

Example:
Authentication is handled in the auth.py file using JWT tokens [Source: backend/auth.py, lines 45-60].
"""
        
        return base_prompt + citation_instruction
    
    def get_system_prompt(self) -> str:
        """Get the system prompt."""
        return self.SYSTEM_PROMPT