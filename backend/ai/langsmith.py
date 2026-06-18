import os
from typing import Optional

def configure_langsmith(api_key: Optional[str] = None, project: Optional[str] = None):
    """
    Dynamically configure LangSmith environment tracing.
    """
    if api_key:
        os.environ["LANGCHAIN_API_KEY"] = api_key
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = project if project else "DesiFinds"
    elif os.environ.get("LANGCHAIN_API_KEY"):
        # If API key is already set in system environment
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        if not os.environ.get("LANGCHAIN_PROJECT"):
            os.environ["LANGCHAIN_PROJECT"] = "DesiFinds"
