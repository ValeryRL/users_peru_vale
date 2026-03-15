import json
import os
from openai import OpenAI
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

class IndustryClassifier:
    def __init__(self):
        opt_key = os.getenv("OPENAI_API_KEY")
        if not opt_key or opt_key == "your_openai_api_key_here":
            logger.warning("OPENAI_API_KEY not properly configured.")
            self.client = None
        else:
            self.client = OpenAI()
            
        self.industries = {
            "A": "Agriculture, forestry and fishing",
            "B": "Mining and quarrying",
            "C": "Manufacturing",
            "D": "Electricity, gas, steam supply",
            "E": "Water supply; sewerage",
            "F": "Construction",
            "G": "Wholesale and retail trade",
            "H": "Transportation and storage",
            "I": "Accommodation and food services",
            "J": "Information and communication",
            "K": "Financial and insurance activities",
            "L": "Real estate activities",
            "M": "Professional, scientific activities",
            "N": "Administrative and support activities",
            "O": "Public administration and defense",
            "P": "Education",
            "Q": "Human health and social work",
            "R": "Arts, entertainment and recreation",
            "S": "Other service activities",
            "T": "Activities of households",
            "U": "Extraterritorial organizations"
        }

    def classify_repository(self, name: str, description: str, readme: str, topics: list[str], language: str) -> dict:
        """Classify a repository into an industry category."""
        if not self.client:
            return {"industry_code": "J", "industry_name": self.industries["J"], "confidence": "low", "reasoning": "OpenAI client missing"}
            
        topics_str = ", ".join(topics) if topics else 'None'
        readme_snippet = readme[:2000] if readme else 'No README'
        
        prompt = f"""Analyze this GitHub repository and classify it into ONE of the following industry categories based on its potential application or the industry it serves.

REPOSITORY INFORMATION:
- Name: {name}
- Description: {description or 'No description'}
- Primary Language: {language or 'Not specified'}
- Topics: {topics_str}
- README (first 2000 chars): {readme_snippet}

INDUSTRY CATEGORIES:
{json.dumps(self.industries, indent=2)}

INSTRUCTIONS:
1. Analyze the repository's purpose, functionality, and potential use cases
2. Consider what industry would most benefit from or use this software
3. If it's a general-purpose tool (e.g., utility library), classify based on the most likely industry application
4. If truly generic (e.g., "hello world"), use "J" (Information and communication)

Respond in JSON format:
{{
  "industry_code": "X",
  "industry_name": "Full industry name",
  "confidence": "high|medium|low",
  "reasoning": "Brief explanation of why this classification was chosen"
}}
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini", # Used a faster model, can fallback to gpt-4-turbo-preview if asked
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert at classifying software projects by industry. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Classification failed for {name}: {e}")
            return {
                "industry_code": "J", 
                "industry_name": "Information and communication", 
                "confidence": "low", 
                "reasoning": f"Error during classification: {e}"
            }

    def batch_classify(self, repositories: list[dict], batch_size: int = 10) -> list[dict]:
        """Classify multiple repositories efficiently."""
        results = []
        for i in range(0, len(repositories), batch_size):
            batch = repositories[i:i+batch_size]
            for repo in batch:
                classification = self.classify_repository(
                    name=repo.get("name", ""),
                    description=repo.get("description", ""),
                    readme=repo.get("readme", ""),
                    topics=repo.get("topics", []),
                    language=repo.get("language", "")
                )
                results.append({
                    "repo_id": repo.get("id"),
                    "repo_name": repo.get("name"),
                    **classification
                })
                logger.info(f"Classified {repo.get('name')} as {classification.get('industry_name')}")
        return results
