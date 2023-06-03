import os
import sqlite3

from chromadb.config import Settings
from chromadb.utils import embedding_functions
default_ef = embedding_functions.DefaultEmbeddingFunction()

import chromadb

import warnings

from utils import format_query_results

client = chromadb.Client(Settings(chroma_db_impl='duckdb+parquet',persist_directory="../.data"
))

def collection_to_query():
    # get all collections
    collections = client.list_collections()

    # if there's only one collection, use that one
    if len(collections) == 1:
        return collections[0].name
    
    # if there are no collections, return
    if len(collections) == 0:
        warnings.warn("No collections found. Please run src/embed_messages.py first.")
        return

    print("\nCollections:\n")
    for i, collection in enumerate(collections):
        print(f"{i}: {collection.name}")

    # Ask for which collection to use
    collection_index = int(input("Which collection would you like to query (enter the #)?\n"))
    collection = collections[collection_index]

    return collection.name

def get_num_messages_to_retrieve():
    # Ask for how many messages to retrieve
    num_messages = int(input("\nHow many results would you like to retrieve?\n"))

    # validate input
    while num_messages < 1 or num_messages > 1000:
        # Ask again if needed
        num_messages = int(input("\nPlease enter a number between 1 and 1000:\n"))

    return num_messages

def retrieval_type():
    # return boolean for whether to retrieve all messages or just ones where "only me" is true
    all_messages = input("\nRetrieve \n1. ALL messages or \n2. Only messages that YOU sent?\n")
    while all_messages not in ["1", "2"]:
        all_messages = input("\nPlease enter 1 or 2:\n")
    
    if all_messages == "1":
        return True
    return False

def main():
    # get collections
    collection_name = collection_to_query()
    collection = client.get_collection(collection_name, embedding_function=default_ef)
    num_messages = get_num_messages_to_retrieve()
    all_messages = retrieval_type()

    while True:
        query = input("\nEnter a query:\n")
        if query == "exit":
            break

        if all_messages:
            results = collection.query(
            query_texts=[query],
            n_results=num_messages,
            )
        else:
            # query only messages where "is_from_me" is true
            print('searching is_from_me: true')
            results = collection.query(
            query_texts=[query],
            n_results=num_messages,
            where={"is_from_me": True},
            )
        
        if len(results['ids'][0]) == 0:
            print("\nNo results found.\n")

        format_query_results(results)

if __name__ == "__main__":
    main()
