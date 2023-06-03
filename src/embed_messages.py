import os
import sqlite3

from chromadb.config import Settings
from chromadb.utils import embedding_functions

from utils import format_query_results

import chromadb
client = chromadb.Client(Settings(chroma_db_impl='duckdb+parquet',persist_directory=".data"
))

# Define the path to the chat.db database
db_path = os.path.expanduser('~/Library/Messages/chat.db')

def get_imessages():
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)

    # Create a cursor object
    cursor = conn.cursor()

    # SQLite query string to get all messages
    query = """
        SELECT 
            datetime(message.date/1000000000 + strftime("%s", "2001-01-01") ,"unixepoch","localtime") as date, 
            message.is_from_me, 
            chat.chat_identifier, 
            message.text
        FROM 
            message 
        LEFT JOIN 
            chat_message_join 
        ON 
            message.ROWID = chat_message_join.message_id 
        LEFT JOIN 
            chat 
        ON 
            chat.ROWID = chat_message_join.chat_id 
        ORDER BY 
            chat.chat_identifier, message.date ASC
    """

    # Execute the query
    cursor.execute(query)

    # Fetch all results
    raw_messages = cursor.fetchall()

    # Close the connection
    conn.close()

    return raw_messages

def initialize_chroma(messages):
    # try to get collection. If it doesn't exist, create it.
    try: 
        collection = client.get_collection("messages")
        print("collection already exists")
        return collection
    except:
        collection = client.create_collection("messages")

    # Convert raw_messages into documents with metadata fields
    documents = []
    metadatas = []
    ids = []
    id_counter = 1
    for msg in messages:
        if msg[3] is not None and msg[3].strip() != "":
            document = msg[3]
            metadata = {
                "date": msg[0], 
                "is_from_me": bool(msg[1]), 
                "chat_id": msg[2]
            }
            documents.append(document)
            metadatas.append(metadata)
            ids.append(str(id_counter))
            id_counter += 1
    
    # Add the messages to the Chroma collection
    collection.upsert(
        documents=documents,
        ids=ids,
        metadatas=metadatas
    )

    client.persist()
    print("collection persisted to disk")

    return collection


def main():
    # Get the iMessages
    raw_messages = get_imessages()
    print("Number of messages retrieved:", len(raw_messages))

    # Initialize Chroma
    collection = initialize_chroma(raw_messages)

    while True:
        query = input("Enter a query: ")
        if query == "exit":
            break
        
        results = collection.query(
        query_texts=[query],
        n_results=5,
        )
        format_query_results(results)

if __name__ == "__main__":
    main()