import os
from typing import Optional

def configure_langsmith(api_key: Optional[str] = None, project: Optional[str] = None):
    """
    Dynamically configure LangSmith environment tracing.
    Maps any LANGSMITH_ environment variables to standard LANGCHAIN_ ones.
    """
    # 1. Map any LANGSMITH_ env vars to standard LANGCHAIN_ ones
    if os.environ.get("LANGSMITH_API_KEY") and not os.environ.get("LANGCHAIN_API_KEY"):
        os.environ["LANGCHAIN_API_KEY"] = os.environ["LANGSMITH_API_KEY"]
    if os.environ.get("LANGSMITH_TRACING") and not os.environ.get("LANGCHAIN_TRACING_V2"):
        if os.environ["LANGSMITH_TRACING"].lower() == "true":
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
    if os.environ.get("LANGSMITH_PROJECT") and not os.environ.get("LANGCHAIN_PROJECT"):
        os.environ["LANGCHAIN_PROJECT"] = os.environ["LANGSMITH_PROJECT"].replace('"', '').replace("'", "")
    if os.environ.get("LANGSMITH_ENDPOINT") and not os.environ.get("LANGCHAIN_ENDPOINT"):
        os.environ["LANGCHAIN_ENDPOINT"] = os.environ["LANGSMITH_ENDPOINT"]

    # 2. Dynamic override passed as argument
    if api_key:
        os.environ["LANGCHAIN_API_KEY"] = api_key
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        if project:
            os.environ["LANGCHAIN_PROJECT"] = project
            
    # 3. Final fallback: Ensure tracing is active if API key is present
    if os.environ.get("LANGCHAIN_API_KEY"):
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        if not os.environ.get("LANGCHAIN_PROJECT"):
            os.environ["LANGCHAIN_PROJECT"] = "DesiFinds"
