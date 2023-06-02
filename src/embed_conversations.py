import os
import sqlite3
from collections import defaultdict
from chromadb.config import Settings
import chromadb

print(chromadb.__version__) # should be 0.3.25 as of june 1st

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

    # Organize messages into conversations
    conversations = defaultdict(list)
    for message in raw_messages:
        date, is_from_me, chat_identifier, text = message
        sender = "Me" if is_from_me else chat_identifier
        conversations[chat_identifier].append((date, sender, text))
    
    # Return the conversations
    return conversations

def initialize_chroma(conversations):
    # Create a collection
    try: 
        collection = client.get_collection("conversations")
    except:
        collection = client.create_collection("conversations")

    documents = []
    metadatas = []
    ids = []

    for i, (key, conversation) in enumerate(conversations.items(), start=1):
        first_message_date = conversation[0][0]
        last_message_date = conversation[-1][0]
        
        document = f"Conversation Date: {first_message_date} - {last_message_date}\nConversation With: {key}\n————————————————\n"
        prev_sender = None
        for date, sender, text in conversation:
            if sender != prev_sender:
                document += f"\nFrom: {sender}\n"
                prev_sender = sender
            document += f"Time: {date}\nMessage: {text}\n"
        
        documents.append(document)
        metadatas.append({
            "conversation_with": key,
            "conversation_start": first_message_date,
            "conversation_end": last_message_date
        })
        ids.append(str(i))

    print("Total number of conversation threads: ", len(documents))
    collection.upsert(
        documents=documents,
        ids=ids,
        metadatas=metadatas
    )

    # Persist the Chroma database
    client.persist()

    return collection

def main():
    # Get the iMessages
    conversations = get_imessages()

    collection = initialize_chroma(conversations)


    while True:
        query = input("Enter a query: ")
        if query == "exit":
            break
        
        results = collection.query(
            query_texts=[query],
            n_results=1,
        )
        print(results)

if __name__ == "__main__":
    main()