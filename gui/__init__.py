"""
GUI Package Initialization
"""

# Only import if the module exists and is valid
try:
    from .chat_window import ChatWindow
    __all__ = ['ChatWindow']
except ImportError as e:
    import warnings
    warnings.warn(f"Could not import ChatWindow: {e}")
    ChatWindow = Nonegit remote add origin https://github.com/aachaman52/GameDevAI.git
