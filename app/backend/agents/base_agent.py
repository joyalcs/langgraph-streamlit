from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

# Using gpt-4o-mini as it's a valid, efficient OpenAI model
# If you want to use Groq instead, uncomment the line below:
# llm_model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.3)

llm_model = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, max_retries=5, request_timeout=60)