from typing import List
from openai import OpenAI

def get_openai_embeddings(texts: List[str], api_key: str) -> List[List[float]]:
    """
    Generate embeddings for a list of texts using the text-embedding-3-small model.
    """
    if not api_key:
        raise ValueError("OpenAI API key is required to generate embeddings.")
    
    client = OpenAI(api_key=api_key)
    # Ensure inputs are clean and non-empty
    cleaned_texts = [t.replace("\n", " ").strip() for t in texts if t.strip()]
    if not cleaned_texts:
        return []
        
    response = client.embeddings.create(
        input=cleaned_texts,
        model="text-embedding-3-small"
    )
    return [data.embedding for data in response.data]
