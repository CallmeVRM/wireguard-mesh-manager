# app/db.py
import sqlite3
import os

# Path to the SQLite database file, with a default value
DB_PATH = os.environ.get("WG_DB", "./data/wireguard.db")

def get_conn():
    """
    Establishes and returns a connection to the SQLite database.
    Ensures the directory for the database file exists.
    Arguments:
        None
    Returns:
        conn : SQLite connection object
    """
    # create data dir if missing
    d = os.path.dirname(DB_PATH)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30)
    return conn

def init_db():
    """
    Initializes the SQLite database by creating the 'nodes' and 'users' tables if they don't exist.
    Arguments:
        None
    Returns:
        None
    """
    
    conn = get_conn()
    c = conn.cursor()
    
    # Create the 'nodes' table to store information about network nodes
    c.execute("""
    CREATE TABLE IF NOT EXISTS nodes (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT UNIQUE,
      public_ip TEXT,
      vpn_ip TEXT,
      port INTEGER,
      mtu INTEGER DEFAULT 1420,
      private_key TEXT,
      public_key TEXT
    )
    """)
    # Create the 'users' table to store information about users
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT UNIQUE,
      vpn_ip TEXT,
      mtu INTEGER DEFAULT 1420,
      private_key TEXT,
      public_key TEXT
    )
    """)
    
    # Commit changes and close the connection
    conn.commit()
    conn.close()
