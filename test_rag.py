from backend.rag import answer_query

response = answer_query("What causes fever?")
print("Answer:", response["answer"])
print("Sources:", response["sources"])
