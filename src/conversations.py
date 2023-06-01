'''
Pull all messages and organize them by conversation
TODO: load into chroma
'''
import os
import sqlite3
from collections import defaultdict
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings


from chromadb.config import Settings
import chromadb
client = chromadb.Client(Settings(chroma_db_impl='duckdb+parquet',persist_directory=".conversations"
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

    # Organize messages into conversations
    conversations = defaultdict(list)
    for message in raw_messages:
        date, is_from_me, chat_identifier, text = message
        sender = "Me" if is_from_me else chat_identifier
        conversations[chat_identifier].append((date, sender, text))
    
    # Return the conversations
    return conversations.values()

def initialize_chroma(conversations):

    collection = client.create_collection("messages")

    # list from 1 to len(documents)
    ids = list(range(1, len(conversations) + 1))
    
    #convert ids to string 
    ids = [str(i) for i in ids]

    collection.add(
        documents=conversations,
        ids=ids
    )

    results = collection.query(
        query_texts=["uplifting message"],
        n_results=1,
    )

    # Persist the Chroma database
    client.persist()

    print(results)


def main():
    # Get the iMessages
    conversations = get_imessages()

    # Initialize Chroma
    initialize_chroma(conversations)


if __name__ == "__main__":
    main()
