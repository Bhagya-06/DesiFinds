from langgraph.graph import StateGraph, START, END
from backend.ai.state import DiscoveryState
from backend.ai.nodes import (
    deconstructor_node,
    retriever_node,
    reviewer_node,
    curator_node,
    formatter_node
)

def build_workflow_graph() -> StateGraph:
    # Initialize state graph with our State TypedDict
    workflow = StateGraph(DiscoveryState)
    
    # Register all nodes
    workflow.add_node("deconstructor", deconstructor_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("reviewer", reviewer_node)
    workflow.add_node("curator", curator_node)
    workflow.add_node("formatter", formatter_node)
    
    # Define execution graph flow
    workflow.add_edge(START, "deconstructor")
    workflow.add_edge("deconstructor", "retriever")
    workflow.add_edge("retriever", "reviewer")
    workflow.add_edge("reviewer", "curator")
    workflow.add_edge("curator", "formatter")
    workflow.add_edge("formatter", END)
    
    return workflow.compile()

# Compile the graph
compiled_graph = build_workflow_graph()

def run_product_discovery(query: str, api_key: str = None) -> dict:
    """
    Run the compiled discovery graph for a given user query.
    """
    initial_state = {
        "query": query,
        "api_key": api_key,
        "category": "",
        "features": [],
        "materials": [],
        "aesthetic_style": "",
        "price_range": "",
        "original_brand": "",
        "matches": [],
        "reviews_analysis": {},
        "curation": {},
        "workflow_steps": [],
        "formatted_output": {}
    }
    
    result = compiled_graph.invoke(initial_state)
    return result["formatted_output"]
