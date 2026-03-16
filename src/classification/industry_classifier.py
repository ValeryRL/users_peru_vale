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

    def classify_batch(self, batch_repositories: list[dict]) -> list[dict]:
        """Classify a batch of repositories in a single LLM call for efficiency."""
        if not self.client:
            return [{
                "repo_id": r.get("id"),
                "repo_name": r.get("name"),
                "industry_code": "J",
                "industry_name": self.industries["J"],
                "confidence": "low",
                "reasoning": "OpenAI client missing"
            } for r in batch_repositories]

        batch_info = []
        for r in batch_repositories:
            topics = r.get("topics", [])
            topics_str = ", ".join(topics) if isinstance(topics, list) else str(topics)
            readme = r.get("readme", "")
            readme_snippet = readme[:1000] if readme else 'No README'
            
            batch_info.append({
                "id": r.get("id"),
                "name": r.get("name"),
                "description": r.get("description", "No description"),
                "language": r.get("language", "Not specified"),
                "topics": topics_str,
                "readme": readme_snippet
            })

        prompt = f"""Analyze the following {len(batch_repositories)} GitHub repositories and classify each into ONE industry category.
        
INDUSTRY CATEGORIES:
{json.dumps(self.industries, indent=2)}

REPOSITORIES TO CLASSIFY:
{json.dumps(batch_info, indent=2)}

INSTRUCTIONS:
1. For each repository, provide the industry_code, industry_name, confidence, and a brief reasoning.
2. Return a JSON structure with a "classifications" key containing a list of objects.
3. Every object must have these fields: "repo_id", "industry_code", "industry_name", "confidence", "reasoning".
4. Ensure the repo_id matches the input exactly.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert software project classifier. Your output must be a valid JSON object matching the requested schema."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            output = json.loads(response.choices[0].message.content)
            results = output.get("classifications", [])
            
            # Map back to ensure we return results for all repos in the batch
            # even if the LLM missed one (unlikely but possible)
            mapping = {str(res["repo_id"]): res for res in results if "repo_id" in res}
            
            final_results = []
            for r in batch_repositories:
                rid = str(r.get("id"))
                if rid in mapping:
                    res = mapping[rid]
                    final_results.append({
                        "repo_id": r.get("id"),
                        "repo_name": r.get("name"),
                        "industry_code": res.get("industry_code", "J"),
                        "industry_name": res.get("industry_name", "Information and communication"),
                        "confidence": res.get("confidence", "medium"),
                        "reasoning": res.get("reasoning", "Bulk classified")
                    })
                else:
                    # Fallback for missing items
                    final_results.append({
                        "repo_id": r.get("id"),
                        "repo_name": r.get("name"),
                        "industry_code": "J",
                        "industry_name": self.industries["J"],
                        "confidence": "low",
                        "reasoning": "Missing from bulk output"
                    })
            return final_results
            
        except Exception as e:
            logger.error(f"Bulk classification failed: {e}")
            return [{
                "repo_id": r.get("id"),
                "repo_name": r.get("name"),
                "industry_code": "J",
                "industry_name": self.industries["J"],
                "confidence": "low",
                "reasoning": f"Error in bulk: {e}"
            } for r in batch_repositories]

    def batch_classify(self, repositories: list[dict], batch_size: int = 10) -> list[dict]:
        """Classify multiple repositories efficiently using bulk calls."""
        results = []
        for i in range(0, len(repositories), batch_size):
            batch = repositories[i:i+batch_size]
            logger.info(f"Classifying batch of {len(batch)} repositories (starting at index {i})...")
            batch_results = self.classify_batch(batch)
            results.extend(batch_results)
        return results
