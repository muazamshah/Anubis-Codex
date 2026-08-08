from typing import Any, Dict, List, Optional


class QueryService:
    """Query optimizer for Phase 3 chat system."""
    
    def __init__(self):
        self.abbreviations = {
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
            "func": "function",
            "var": "variable",
            "class": "class",
            "obj": "object",
            "prop": "property",
            "meth": "method",
            "init": "initialization",
        }
    
    def optimize_query(self, question: str) -> str:
        """
        Optimize user query for better retrieval.
        
        Examples:
        - "Explain auth" -> "Explain the authentication system"
        - "How does login work?" -> "How does the login system work?"
        """
        optimized = question.strip()
        
        # Expand abbreviations
        words = optimized.lower().split()
        for word, expansion in self.abbreviations.items():
            if word in words:
                optimized = optimized.replace(word, expansion)
        
        # Add context if question is too short
        if len(optimized.split()) <= 2:
            optimized = f"Explain {optimized} in the repository"
        
        return optimized
    
    def rewrite_ambiguous_question(self, question: str, chat_history: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Rewrite ambiguous questions based on chat history.
        
        Example:
        User: "Where is authentication implemented?"
        Assistant: "Authentication is in backend/auth.py"
        User: "Explain that function"
        Rewritten: "Explain the authentication function in backend/auth.py"
        """
        if not chat_history or len(chat_history) == 0:
            return question
        
        # Check for pronouns and references
        pronouns = ["that", "this", "it", "they", "them", "those"]
        question_lower = question.lower()
        
        for pronoun in pronouns:
            if question_lower.startswith(pronoun):
                # Get last assistant message
                last_assistant_msg = None
                for msg in reversed(chat_history):
                    if msg.get("role") == "assistant":
                        last_assistant_msg = msg.get("content", "")
                        break
                
                if last_assistant_msg:
                    # Extract file references from last message
                    import re
                    file_refs = re.findall(r'\[Source: ([^\]]+)\]', last_assistant_msg)
                    if file_refs:
                        # Replace pronoun with actual reference
                        question = question.replace(pronoun, f"the code in {file_refs[0]}")
        
        return question
    
    def expand_query(self, question: str) -> List[str]:
        """
        Generate multiple query variations for better retrieval.
        
        Returns list of query variations.
        """
        queries = [question]
        
        # Add expanded version
        optimized = self.optimize_query(question)
        if optimized != question:
            queries.append(optimized)
        
        # Add keyword extraction
        keywords = self._extract_keywords(question)
        if keywords:
            queries.append(" ".join(keywords))
        
        return queries
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text."""
        # Remove common words
        stop_words = {
            "a", "an", "the", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "can",
            "to", "of", "in", "for", "on", "with", "at", "by", "from",
            "as", "into", "through", "during", "before", "after",
            "above", "below", "between", "out", "off", "over", "under",
            "again", "further", "then", "once", "here", "there",
            "when", "where", "why", "how", "all", "each", "every",
            "both", "few", "more", "most", "other", "some", "such",
            "no", "nor", "not", "only", "own", "same", "so", "than",
            "too", "very", "just", "because", "but", "and", "or",
            "if", "while", "about", "up", "what", "which", "who",
            "whom", "this", "that", "these", "those", "i", "me",
            "my", "myself", "we", "our", "ours", "ourselves", "you",
            "your", "yours", "yourself", "yourselves", "he", "him",
            "his", "himself", "she", "her", "hers", "herself", "it",
            "its", "itself", "they", "them", "their", "theirs",
            "themselves", "explain", "tell", "show", "describe"
        }
        
        words = text.lower().split()
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords
    
    def validate_query(self, question: str) -> Dict[str, Any]:
        """
        Validate user query.
        
        Returns:
        - valid: Whether query is valid
        - optimized: Optimized version
        - warnings: List of warnings
        """
        warnings = []
        
        # Check if question is empty
        if not question or not question.strip():
            return {
                "valid": False,
                "optimized": "",
                "warnings": ["Question cannot be empty"]
            }
        
        # Check if question is too short
        if len(question.split()) < 2:
            warnings.append("Question is very short, may not retrieve relevant results")
        
        # Check if question is too long
        if len(question) > 500:
            warnings.append("Question is very long, consider shortening it")
        
        # Optimize
        optimized = self.optimize_query(question)
        
        return {
            "valid": True,
            "optimized": optimized,
            "warnings": warnings
        }