from langchain_google_genai import ChatGoogleGenerativeAI
from . import config

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro", google_api_key=config.GOOGLE_API_KEY, temperature=0.0)
