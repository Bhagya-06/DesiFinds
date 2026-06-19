from typing import TypedDict, List, Dict, Any, Optional

class DiscoveryState(TypedDict):
    # Inputs
    query: str
    api_key: Optional[str]
    
    # Product Deconstructor Output
    category: str
    features: List[str]
    materials: List[str]
    aesthetic_style: str
    price_range: str
    original_brand: str
    
    # RAG Retriever Output
    matches: List[Dict[str, Any]]
    
    # Review Analyzer Output
    reviews_analysis: Dict[str, Dict[str, Any]] # product_id -> {pros: List[str], cons: List[str], summary: str}
    
    # Quality Curator Output
    curation: Dict[str, Dict[str, Any]] # product_id -> {match_score: int, match_reason: str, craftsmanship: str, value_prop: str}
    
    # Formatter Output
    formatted_output: Dict[str, Any]
    
    # Execution tracing logs for UI
    workflow_steps: List[Dict[str, Any]] # list of {name: str, status: str, output: str}
    
    # Scope classification flag
    out_of_scope: Optional[bool]
