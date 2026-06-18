import pandas as pd
from typing import List, Dict, Any

class Deduplicator:
    """
    Deduplicates products using Pandas based on Brand + Name + Category.
    """
    @staticmethod
    def deduplicate(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not products:
            return []
            
        # Convert to Pandas DataFrame
        df = pd.DataFrame(products)
        
        # Create composite key for comparison (case-insensitive and whitespace stripped)
        df["dedup_key"] = (
            df["brand"].str.strip().str.lower() + "||" +
            df["name"].str.strip().str.lower() + "||" +
            df["category"].str.strip().str.lower()
        )
        
        # Sort so that records with valid ratings/reviewCounts or originalPrices are prioritized
        # We put non-null rating/reviewCount at the top
        df["has_rating"] = df["rating"].notnull()
        df["has_price"] = df["price"] > 0
        
        df = df.sort_values(by=["has_rating", "has_price"], ascending=[False, False])
        
        # Drop duplicates, keeping the first occurrence (which is the one with better metadata)
        df_clean = df.drop_duplicates(subset=["dedup_key"], keep="first")
        
        # Clean up temporary helper columns
        df_clean = df_clean.drop(columns=["dedup_key", "has_rating", "has_price"])
        
        # Convert back to list of dictionaries
        # Convert NaN values to None for JSON compliance
        df_clean = df_clean.where(pd.notnull(df_clean), None)
        
        return df_clean.to_dict(orient="records")
