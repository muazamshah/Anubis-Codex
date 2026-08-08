import ast
import os
import re
from typing import Any, Dict, List, Optional


class ASTParserService:
    """AST-based parser for extracting code structure."""
    
    def parse_file(self, file_path: str, language: str) -> Dict[str, Any]:
        """Parse a file and extract structural elements."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            return self._empty_parse_result()
        
        if language == 'python':
            return self._parse_python(content)
        elif language in ['javascript', 'typescript']:
            return self._parse_javascript(content, language)
        elif language == 'markdown':
            return self._parse_markdown(content)
        else:
            return self._parse_generic(content)
    
    def _empty_parse_result(self) -> Dict[str, Any]:
        return {
            "classes": [],
            "functions": [],
            "imports": [],
            "variables": [],
            "docstrings": [],
            "decorators": [],
        }
    
    def _parse_python(self, content: str) -> Dict[str, Any]:
        result = self._empty_parse_result()
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Extract classes
                if isinstance(node, ast.ClassDef):
                    result["classes"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "bases": [self._get_name(base) for base in node.bases],
                        "decorators": [self._get_decorator_name(d) for d in node.decorator_list],
                    })
                
                # Extract functions
                elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    result["functions"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "args": [arg.arg for arg in node.args.args],
                        "decorators": [self._get_decorator_name(d) for d in node.decorator_list],
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                    })
                
                # Extract imports
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        result["imports"].append({
                            "module": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno,
                        })
                
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    result["imports"].append({
                        "module": module,
                        "names": [alias.name for alias in node.names],
                        "line": node.lineno,
                    })
                
                # Extract variables (module-level assignments)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            result["variables"].append({
                                "name": target.id,
                                "line": node.lineno,
                            })
            
            # Extract docstrings
            if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant):
                result["docstrings"].append(tree.body[0].value.value)
            
        except SyntaxError:
            pass
        
        return result
    
    def _parse_javascript(self, content: str, language: str) -> Dict[str, Any]:
        result = self._empty_parse_result()
        
        # Extract classes
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{'
        for match in re.finditer(class_pattern, content):
            result["classes"].append({
                "name": match.group(1),
                "line": content[:match.start()].count('\n') + 1,
                "bases": [match.group(2)] if match.group(2) else [],
            })
        
        # Extract functions
        func_patterns = [
            r'function\s+(\w+)\s*\(([^)]*)\)',
            r'const\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)\s*=>',
            r'(\w+)\s*:\s*(?:async\s+)?function\s*\(([^)]*)\)',
        ]
        for pattern in func_patterns:
            for match in re.finditer(pattern, content):
                result["functions"].append({
                    "name": match.group(1),
                    "line": content[:match.start()].count('\n') + 1,
                })
        
        # Extract imports
        import_patterns = [
            r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]',
            r'require\([\'"]([^\'"]+)[\'"]\)',
        ]
        for pattern in import_patterns:
            for match in re.finditer(pattern, content):
                result["imports"].append({
                    "module": match.group(1),
                    "line": content[:match.start()].count('\n') + 1,
                })
        
        return result
    
    def _parse_markdown(self, content: str) -> Dict[str, Any]:
        result = self._empty_parse_result()
        
        # Extract headings
        for match in re.finditer(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE):
            result["classes"].append({
                "name": match.group(2),
                "line": content[:match.start()].count('\n') + 1,
                "level": len(match.group(1)),
            })
        
        # Extract code blocks
        for match in re.finditer(r'```(\w+)?\n(.*?)```', content, re.DOTALL):
            result["functions"].append({
                "name": f"code_block_{match.group(1) or 'text'}",
                "line": content[:match.start()].count('\n') + 1,
                "language": match.group(1),
            })
        
        return result
    
    def _parse_generic(self, content: str) -> Dict[str, Any]:
        result = self._empty_parse_result()
        
        # Try to extract basic patterns
        for match in re.finditer(r'(?:class|struct|interface)\s+(\w+)', content):
            result["classes"].append({
                "name": match.group(1),
                "line": content[:match.start()].count('\n') + 1,
            })
        
        for match in re.finditer(r'(?:def|function|void|int|string)\s+(\w+)\s*\(', content):
            result["functions"].append({
                "name": match.group(1),
                "line": content[:match.start()].count('\n') + 1,
            })
        
        return result
    
    def _get_name(self, node) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return ""
    
    def _get_decorator_name(self, node) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return ""