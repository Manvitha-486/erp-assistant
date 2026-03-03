from retriever import get_retriever
from llm_service import get_llm, get_qa_prompt

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def process_query(question: str, document_id: str = "general"):
    """Processes a user query through the RAG pipeline."""
    
    # Handle basic edge cases
    if not question or not question.strip():
        return {
            "answer": "Validation Error: Query cannot be empty.",
            "source": ""
        }
        
    if len(question) > 500:
        question = question[:500]  # Truncate very long queries

    retriever = get_retriever(document_id)
    if not retriever:
        return {
            "answer": f"The model '{document_id}' is not initialized or the file is missing.",
            "source": "System Error"
        }

    llm = get_llm()

    # Step 1: Retrieve documents first to get sources
    docs = retriever.invoke(question)
    
    # Extract the context sources
    sources = []
    if docs:
        for doc in docs:
            source = doc.metadata.get("source", "Unknown")
            source_file = source.split("/")[-1].split("\\")[-1]
            page = doc.metadata.get("page", "")
            if page:
                sources.append(f"{source_file} (Page {page})")
            else:
                sources.append(source_file)
            
    source_str = ", ".join(set(sources)) if sources else "No source found"

    # Step 2: Form the prompt manually as a basic string
    context_text = format_docs(docs)
    final_prompt = get_qa_prompt(context=context_text, question=question)

    # Step 3: Pass string to LLM directly and get the text content back
    llm_output = llm.invoke(final_prompt)
    answer = llm_output.content
    
    # Basic fallback if LLM answers that info is missing or low similarity
    if "not available" in answer.lower():
        answer = "The information is not available in this module."
    elif not sources:
        answer = "No relevant documentation found for this query in this module."
    
    return {
        "answer": answer,
        "source": source_str
    }
