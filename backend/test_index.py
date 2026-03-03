from retriever import get_retriever

retriever = get_retriever("general")
if retriever:
    print("SUCCESS")
    docs = retriever.invoke("hi")
    print(docs)
else:
    print("FAILED")
