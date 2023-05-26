'''
This script just pulls the 100 most recent messages from the Messages app on macOS.
Use it to make sure you have proper database connection.
'''
import sqlite3
import os

def get_imessages():
    # Define the path to the chat.db database
    db_path = os.path.expanduser('~/Library/Messages/chat.db')

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)

    # Create a cursor object
    cursor = conn.cursor()

    # SQLite query string to get the last 100 messages
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
            message.date 
        DESC 
        LIMIT 100
    """

    # Execute the query, fetch results, & return
    cursor.execute(query)

    messages = cursor.fetchall()

    conn.close()

    return messages


def print_messages(messages):
    for message in messages:
        date, is_from_me, chat_identifier, text = message
        sender = "Me" if is_from_me else chat_identifier
        print(f"[{date}] {sender}: {text}")


if __name__ == "__main__":
    messages = get_imessages()
    print_messages(messages)
