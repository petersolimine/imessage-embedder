

import chromadb
client = chromadb.Client()

# Create collection. get_collection, get_or_create_collection, delete_collection also available!
collection = client.create_collection("all-my-documents")

# Add docs to the collection. Can also update and delete. Row-based API coming soon!
collection.add(
    documents=["butterfly", "color"],
    metadatas=[{"source": "notion"}, {"from": "google-docs"}],
    ids=["doc1", "doc2"],
)

# Query/search 2 most similar results. You can also .get by id
results = collection.query(
    query_texts=["rainbow"],
    n_results=1,
)

print(results)