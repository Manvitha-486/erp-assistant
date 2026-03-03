import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    """Returns the Gemini Flash LLM instance."""
    return ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        temperature=0.0
    )

def get_qa_prompt(context, question):
    """Returns the QA Prompt as a simple formatted string to prevent hallucination."""
    return f"""You are an ERP support assistant.

First, respond politely to any conversational greetings (e.g. "hi", "hello", "good morning") in a brief, friendly manner.

Then, answer the user's question using ONLY the provided documentation.

If the user asks a question and the answer is not found in the documentation,
respond with:
"The information is not available in the ERP documentation."

Context:
{context}

Question:
{question}
"""
