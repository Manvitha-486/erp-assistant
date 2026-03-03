from langchain_community.embeddings import HuggingFaceEmbeddings

def get_embeddings():
    """
    Returns the all-MiniLM-L6-v2 embeddings model for converting
    documents and queries into vector embeddings locally.
    """
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}
    
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
