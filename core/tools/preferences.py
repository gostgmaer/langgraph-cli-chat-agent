from langchain.tools import tool

@tool
def save_preference(key: str, value: str) -> str:
    """
    Save a user preference (e.g., name, favorite color, language) to the agent's long-term memory.
    Call this whenever the user states a preference you should remember.
    
    Args:
        key: The category of the preference (e.g., 'name', 'language', 'diet').
        value: The value to remember for this preference.
    """
    return f"Preference '{key}' saved as '{value}'."
