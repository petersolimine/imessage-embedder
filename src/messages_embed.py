'''
Pull all messages and organize them by conversation
TODO: load into chroma
'''
import os
import sqlite3

from chromadb.config import Settings
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

    print(raw_messages)

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
    collection.add(
        documents=messages,
        ids=ids,
    )
    
    print("added messages to collection")

    uplifting_messages = collection.query(
        query_texts=["uplifting message"],
        n_results=10,
    )

    print(uplifting_messages)

    hilarious_story = collection.query(
    query_texts=["hilarious story"],
    n_results=10,
    )

    print(hilarious_story)

    # Persist the Chroma database TODO: uncomment. Figure out how to load from persist_directory
    # client.persist()


def main():
    # Get the iMessages
    raw_messages = get_imessages()

    # Organize messages (tuple) into strings, ignoring None and empty strings
    messages = [message[3] for message in raw_messages if message[3] is not None and message[3].strip() != ""]

    # Initialize Chroma
    initialize_chroma(messages)

if __name__ == "__main__":
    main()


'''
TODO:

- Figure out how to persist properly
- Figure out how to load from persist_directory
- Add metadata to messages

'''