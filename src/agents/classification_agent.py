import json
import os
from openai import OpenAI
from loguru import logger
from src.extraction.github_client import GitHubClient
from src.extraction.repo_extractor import RepoExtractor

class ClassificationAgent:
    def __init__(self):
        opt_key = os.getenv("OPENAI_API_KEY")
        if not opt_key or opt_key == "your_openai_api_key_here":
            logger.warning("OPENAI_API_KEY not properly configured.")
            self.client = None
        else:
            self.client = OpenAI()
            
        github_client = GitHubClient()
        self.repo_extractor = RepoExtractor(github_client)
        
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_readme",
                    "description": "Fetch the README content of a repository if the description is not enough",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "owner": {"type": "string"},
                            "repo": {"type": "string"}
                        },
                        "required": ["owner", "repo"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_languages",
                    "description": "Get the programming languages used in a repository",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "owner": {"type": "string"},
                            "repo": {"type": "string"}
                        },
                        "required": ["owner", "repo"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "classify_industry",
                    "description": "Classify a repository into an industry category and finish execution.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "repo_name": {"type": "string"},
                            "industry_code": {"type": "string", "enum": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U"]},
                            "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                            "reasoning": {"type": "string"}
                        },
                        "required": ["repo_name", "industry_code", "confidence", "reasoning"]
                    }
                }
            }
        ]

    def _get_readme(self, owner: str, repo: str) -> str:
        logger.debug(f"[Tool Execution] Fetching README for {owner}/{repo}")
        return self.repo_extractor.get_repo_readme(owner, repo)

    def _get_languages(self, owner: str, repo: str) -> dict:
        logger.debug(f"[Tool Execution] Fetching languages for {owner}/{repo}")
        return self.repo_extractor.get_repo_languages(owner, repo)

    def run(self, repository: dict) -> dict:
        """Run the classification agent on a repository."""
        if not self.client:
            return {"error": "Missing OpenAI API key."}
            
        messages = [
            {
                "role": "system",
                "content": """You are an autonomous AI agent that classifies GitHub repositories into industry categories based on their purpose or the industry they serve.
Your task is to analyze a repository and determine which industry it serves.
You have access to tools to get more information if needed. If you are confident, simply call the classify_industry tool.

Industry codes: A (Agriculture), B (Mining), C (Manufacturing), D (Utilities),
E (Water), F (Construction), G (Trade), H (Transport), I (Hospitality),
J (Information/Tech), K (Finance), L (Real Estate), M (Professional Services),
N (Administrative), O (Public Admin), P (Education), Q (Health), R (Arts),
S (Other Services), T (Households), U (International Orgs)

Steps:
1. Review the basic repository information.
2. If unclear, fetch the README or languages for more context using the provided tools.
3. Make your final classification by calling the classify_industry tool. You MUST eventually call classify_industry to complete your task!"""
            },
            {
                "role": "user",
                "content": f"""Please classify this repository:
Name: {repository.get('name')}
Owner: {repository.get('owner')}
Description: {repository.get('description', 'No description')}
Primary Language: {repository.get('language', 'Unknown')}
Topics: {', '.join(repository.get('topics', [])) if repository.get('topics') else 'None'}
Stars: {repository.get('stargazers_count', 0)}
"""
            }
        ]
        
        while True:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini", # Standard faster model
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            
            if message.tool_calls:
                messages.append(message)
                
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    if function_name == "get_readme":
                        result = self._get_readme(arguments.get("owner", repository.get("owner")), arguments.get("repo", repository.get("name")))
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result[:5000] if result else "No README available"
                        })
                    elif function_name == "get_languages":
                        result = self._get_languages(arguments.get("owner", repository.get("owner")), arguments.get("repo", repository.get("name")))
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": str(result)
                        })
                    elif function_name == "classify_industry":
                        logger.info(f"Agent classified '{arguments.get('repo_name', repository.get('name'))}' as {arguments.get('industry_code')}")
                        return arguments
            else:
                logger.warning(f"Agent did not call a tool, content: {message.content}")
                break
                
        return {"error": "Agent did not produce classification"}
