import logging
import sqlite3
from sqlite3 import Error

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO, filename = 'bot.log', encoding = 'UTF-8', datefmt = '%Y-%m-%d %H:%M:%S')

def create_connection():
    """Create a database connection to the SQLite database"""
    try:
        conn = sqlite3.connect('bot_settings.db')
        return conn
    except Error as e:
        logging.error(f"Error connecting to database: {e}")
        return None

def init_database():
    """Create the settings table if it doesn't exist"""
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS chat_settings
                (chat_id INTEGER PRIMARY KEY,
                 notes_folder TEXT NOT NULL)
            ''')
            # Migration: add all_as_tasks column if it does not exist
            try:
                c.execute('ALTER TABLE chat_settings ADD COLUMN all_as_tasks INTEGER NOT NULL DEFAULT 0')
            except Error:
                # Column likely exists already
                pass
            conn.commit()
        except Error as e:
            logging.error(f"Error creating table: {e}")
        finally:
            conn.close()

def set_notes_folder(chat_id, folder_path) -> str:
    # Save to database without overwriting other fields
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute('UPDATE chat_settings SET notes_folder = ? WHERE chat_id = ?', (folder_path, chat_id))
            if c.rowcount == 0:
                c.execute('INSERT INTO chat_settings (chat_id, notes_folder) VALUES (?, ?)', (chat_id, folder_path))
            conn.commit()
            result = f"Notes folder for {chat_id} set to: {folder_path}"
            logging.info(result)
        except Error as e:
            result = f"Error saving settings for for {chat_id}: {e}"
            logging.error(result)
        finally:
            conn.close()
            return result

def get_notes_folder(chat_id) -> str:
    conn = create_connection()
    folder_path = ""
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute('SELECT notes_folder FROM chat_settings WHERE chat_id = ?', 
                    (chat_id,))
            row = c.fetchone()
            if row:
                folder_path = row[0]
        except Error as e:
            logging.error(f"Database error: {e}")
        finally:
            conn.close()
    return folder_path

def set_all_as_tasks(chat_id: int, enabled: bool) -> str:
    """Turn on/off forced task mode for a chat (stores as 0/1)."""
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute('UPDATE chat_settings SET all_as_tasks = ? WHERE chat_id = ?', (1 if enabled else 0, chat_id))
            if c.rowcount == 0:
                c.execute('INSERT INTO chat_settings (chat_id, notes_folder, all_as_tasks) VALUES (?, ?, ?)', (chat_id, "", 1 if enabled else 0))
            conn.commit()
            result = f"All posts as tasks for {chat_id}: {'ON' if enabled else 'OFF'}"
            logging.info(result)
        except Error as e:
            result = f"Error saving all_as_tasks for {chat_id}: {e}"
            logging.error(result)
        finally:
            conn.close()
            return result

def get_all_as_tasks(chat_id: int) -> bool:
    """Read forced task flag for a chat."""
    conn = create_connection()
    enabled = False
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute('SELECT all_as_tasks FROM chat_settings WHERE chat_id = ?', (chat_id,))
            row = c.fetchone()
            if row is not None:
                enabled = bool(row[0])
        except Error as e:
            logging.error(f"Database error: {e}")
        finally:
            conn.close()
    return enabled

init_database()