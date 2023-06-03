def format_query_results(results):
    for i in range(len(results['ids'][0])):
        print("\n-------------------------------------------------")
        print(f"Result {i+1}:")
        print("ID:", results['ids'][0][i])
        print("Document:\n", results['documents'][0][i])
        print("Metadata:\n", results['metadatas'][0][i])
        print("Distance:", results['distances'][0][i])
        print("-------------------------------------------------\n")