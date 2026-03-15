import os
import sys
import pandas as pd
from loguru import logger
from tqdm import tqdm

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.classification.industry_classifier import IndustryClassifier
from src.agents.classification_agent import ClassificationAgent

def classify_data():
    repos_path = "data/processed/repositories.csv"
    
    if not os.path.exists(repos_path):
        logger.error(f"Cannot find {repos_path}. Please run extract_data.py first.")
        return
        
    logger.info("Loading repositories...")
    repos_df = pd.read_csv(repos_path)
    
    # Fill NaN values for cleaner dictionaries
    repos_df = repos_df.fillna("")
    repositories = repos_df.to_dict(orient="records")
    
    # Check if OPENAI_API_KEY is properly set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        logger.warning("No valid OPENAI_API_KEY found.")
        logger.warning("Will classify all repositories as 'J' (Information and communication) by default.")
    
    classifier = IndustryClassifier()
    # We could also use the ClassificationAgent for more advanced evaluation on difficult repos, 
    # but the IndustryClassifier is much faster for a large batch of 1000 repos.
    # The assignment states "Use AI agents for automated data processing tasks", so we have both available.
    # Let's use the IndustryClassifier for the bulk, and if any fail we could use the agent,
    # or just use the IndustryClassifier as it does zero-shot over the whole batch.
    
    logger.info(f"Classifying {len(repositories)} repositories...")
    classifications = []
    
    # Classify in batches
    batch_size = 10
    for i in tqdm(range(0, len(repositories), batch_size), desc="Classification Batches"):
        batch = repositories[i:i+batch_size]
        try:
            results = classifier.batch_classify(batch, batch_size=batch_size)
            classifications.extend(results)
        except Exception as e:
            logger.error(f"Error classifying batch {i}: {e}")
            # Add fallback classifications for the batch
            for repo in batch:
                classifications.append({
                    "repo_id": repo.get("id"),
                    "repo_name": repo.get("name"),
                    "industry_code": "J",
                    "industry_name": "Information and communication",
                    "confidence": "low",
                    "reasoning": "Fallback due to error"
                })
                
    # Save classifications
    logger.info("Saving classifications to CSV...")
    os.makedirs("data/processed", exist_ok=True)
    classifications_df = pd.DataFrame(classifications)
    classifications_df.to_csv("data/processed/classifications.csv", index=False)
    logger.info("Classification complete!")

if __name__ == "__main__":
    classify_data()
