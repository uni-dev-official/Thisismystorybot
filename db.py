import sqlite3

conn = sqlite3.connect("bot_database.db")
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    chat_id INTEGER UNIQUE,
    joined_date TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS stories (
    story_id INTEGER PRIMARY KEY,
    chat_id INTEGER,
    story TEXT,
    FOREIGN KEY (chat_id) REFERENCES users (chat_id)
)
''')

conn.commit()

# Function to add a user
def add_user(username, chat_id, joined_date):
    try:
        cursor.execute('''
        INSERT INTO users (username, chat_id, joined_date)
        VALUES (?, ?, ?)
        ''', (username, chat_id, joined_date))
        conn.commit()
    except sqlite3.IntegrityError:
        print('User already exists!')

# Function to fetch user data
def get_user(chat_id):
    cursor.execute('SELECT * FROM users WHERE chat_id = ?', (chat_id,))
    return cursor.fetchone()

# Function to count all users
def count_users():
    cursor.execute('SELECT COUNT(*) FROM users')
    return cursor.fetchone()[0]

# Function to add a story
def add_story(chat_id, story):
    cursor.execute("""
    INSERT INTO stories (chat_id, story)
    VALUES (?, ?)
    """, (chat_id, story))
    conn.commit()

# Function to fetch stories for a user
def get_stories(chat_id):
    cursor.execute('SELECT story FROM stories WHERE chat_id = ?', (chat_id,))
    return cursor.fetchall()

def fetch_all_stories():
    cursor = conn.cursor()
    cursor.execute("SELECT story_id, chat_id, story FROM stories")  # Using the actual column names
    rows = cursor.fetchall()
    return rows

stories = fetch_all_stories()
for story in stories:
    story_id = story[0]  # story_id
    chat_id = story[1]   # chat_id
    story_content = story[2]  # story content
    # process the story as needed

    print(story)

# Close the connection (optional, if needed at the end of your program)
def close_connection():
    conn.close()
