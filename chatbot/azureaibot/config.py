import os

class DefaultConfig:
    """ Bot Configuration """
    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    
    # Azure AI Language Service Configuration
    AZURE_LANGUAGE_ENDPOINT = os.environ.get("AZURE_LANGUAGE_ENDPOINT")
    AZURE_LANGUAGE_KEY = os.environ.get("AZURE_LANGUAGE_KEY")
