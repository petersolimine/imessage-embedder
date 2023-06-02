'''
Pull all messages and organize them by conversation
TODO: load into chroma
'''
import os
import sqlite3

from chromadb.config import Settings
from chromadb.utils import embedding_functions
# openai_ef = embedding_functions.OpenAIEmbeddingFunction(
#                 api_key="sk-",
#                 model_name="text-embedding-ada-002"
#             )
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
    except:
        collection = client.create_collection("messages")
    
    # Create list of IDs based on number of messages
    ids = list(range(1, len(messages) + 1))
    ids = [str(i) for i in ids]

    # Add the messages to the Chroma collection
    collection.upsert(
        documents=messages,
        ids=ids,
    )

    client.persist()

    return collection


def main():
    # Get the iMessages
    raw_messages = get_imessages()

    # Organize messages (tuple) into strings, ignoring None and empty strings
    messages = [message[3] for message in raw_messages if message[3] is not None and message[3].strip() != ""]

    # Initialize Chroma
    collection = initialize_chroma(messages)

    while True:
        query = input("Enter a query: ")
        if query == "exit":
            break
        
        results = collection.query(
            query_texts=[query],
            n_results=5,
        )
        print(results)

if __name__ == "__main__":
    main()


'''
TODO:
- Add metadata to messages
- while true for querying
'''