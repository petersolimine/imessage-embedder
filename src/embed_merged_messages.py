import os
import sqlite3
from collections import defaultdict
from chromadb.config import Settings
import chromadb

print(chromadb.__version__)

client = chromadb.Client(Settings(chroma_db_impl='duckdb+parquet',persist_directory=".data"))

db_path = os.path.expanduser('~/Library/Messages/chat.db')

def get_imessages():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

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
    cursor.execute(query)
    raw_messages = cursor.fetchall()
    conn.close()

    conversations = defaultdict(list)
    for message in raw_messages:
        date, is_from_me, chat_identifier, text = message
        sender = "Me" if is_from_me else chat_identifier
        conversations[chat_identifier].append((date, sender, text))
    
    return conversations

def initialize_chroma(conversations):
    try: 
        collection = client.get_collection("merged_messages")
    except:
        collection = client.create_collection("merged_messages")

    documents = []
    metadatas = []
    ids = []

    for i, (key, conversation) in enumerate(conversations.items(), start=1):
        document = ""
        num_merged_msgs = 0
        first_message_time = ""
        last_message_time = ""
        sender = ""
        prev_sender = None
        for date, sender, text in conversation:
            if sender != prev_sender:
                if document:
                    documents.append(document)
                    metadatas.append({
                        "number_of_merged_messages": num_merged_msgs,
                        "first_message_time": first_message_time,
                        "last_message_time": last_message_time,
                        "sender": prev_sender,
                    })
                    ids.append(str(i))
                    i += 1

                document = f"From: {sender}\n"
                num_merged_msgs = 0
                first_message_time = date
                prev_sender = sender
            
            document += f"Time: {date}\nMessage: {text}\n"
            num_merged_msgs += 1
            last_message_time = date

        if document:
            documents.append(document)
            metadatas.append({
                "number_of_merged_messages": num_merged_msgs,
                "first_message_time": first_message_time,
                "last_message_time": last_message_time,
                "sender": sender,
            })
            ids.append("m"+str(i))

    print("Total number of conversation threads: ", len(documents))
    collection.upsert(
        documents=documents,
        ids=ids,
        metadatas=metadatas
    )

    client.persist()
    return collection

def main():
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
