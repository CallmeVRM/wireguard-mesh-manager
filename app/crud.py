import sqlite3
from pathlib import Path
import os

# Path to the database file, with a default value
DB_FILE = os.environ.get("DB_FILE", "/data/wireguard.db")
Path(DB_FILE).parent.mkdir(parents=True, exist_ok=True)

# Function to establish a SQLite connection
def get_conn():
    """
    Creates and returns a connection to the SQLite database.
    Configures row_factory to return query results as dictionaries.
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# Function to initialize the database
def init_db():
    """
    Initializes the SQLite database by creating the 'nodes' and 'users' tables if they don't exist.
    """
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS nodes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        public_ip TEXT,
        vpn_ip TEXT,
        port INTEGER,
        mtu INTEGER,
        private_key TEXT,
        public_key TEXT
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        vpn_ip TEXT,
        mtu INTEGER,
        private_key TEXT,
        public_key TEXT
    )""")
    conn.commit()
    conn.close()


# -------- Nodes ----------
# Function to list all nodes
def list_nodes():
    conn = get_conn()
    rows = conn.execute("""
        SELECT id,name,public_ip,vpn_ip,port,mtu,private_key,public_key
        FROM nodes ORDER BY id ASC
    """).fetchall()
    conn.close()
    return rows

# Function to create a new node
def create_node(name, public_ip, port, mtu, vpn_ip):
    """
    Adds a new node to the 'nodes' table.
    Arguments:
        name : Unique name of the node.
        public_ip : Public IP address of the node.
        port : Port used by the node.
        mtu : Maximum Transmission Unit (MTU) of the node.
        vpn_ip : VPN IP address of the node.
    """
    conn = get_conn()
    conn.execute("""
        INSERT INTO nodes(name, public_ip, port, mtu, vpn_ip)
        VALUES (?, ?, ?, ?, ?)
    """, (name, public_ip, port, mtu, vpn_ip))
    conn.commit(); conn.close()

# Function to update the public IP of a node
def update_node_public_ip(node_id, new_ip):
    """
    Updates the public IP address of an existing node.
    Arguments:
        node_id : ID of the node to update.
        new_ip : New public IP address.
    """
    conn = get_conn()
    conn.execute("UPDATE nodes SET public_ip=? WHERE id=?", (new_ip, node_id))
    conn.commit(); conn.close()

# Function to update the VPN IP of a node
def update_node_vpn_ip(node_id, new_vpn_ip):
    """
    Updates the VPN IP address of an existing node.
    Arguments:
        node_id : ID of the node to update.
        new_vpn_ip : New VPN IP address.
    """
    conn = get_conn()
    conn.execute("UPDATE nodes SET vpn_ip=? WHERE id=?", (new_vpn_ip, node_id))
    conn.commit(); conn.close()

# -------- Users ----------
# Function to list all users
def list_users():
    conn = get_conn()
    rows = conn.execute("""
        SELECT id,name,vpn_ip,mtu,private_key,public_key
        FROM users ORDER BY id ASC
    """).fetchall()
    conn.close()
    return rows

# Function to create a new user
def create_user(name, mtu, vpn_ip):
    """
    Adds a new user to the 'users' table.
    Arguments:
        name : Unique name of the user.
        mtu : Maximum Transmission Unit (MTU) of the user.
        vpn_ip : VPN IP address of the user.
    """
    conn = get_conn()
    conn.execute("""
        INSERT INTO users(name, mtu, vpn_ip)
        VALUES(?, ?, ?)
    """, (name, mtu, vpn_ip))
    conn.commit(); conn.close()

# Function to update the VPN IP of a user
def update_user_vpn_ip(user_id, new_vpn_ip):
    """
    Updates the VPN IP address of an existing user.
    Arguments:
        user_id : ID of the user to update.
        new_vpn_ip : New VPN IP address.
    """
    conn = get_conn()
    conn.execute("UPDATE users SET vpn_ip=? WHERE id=?", (new_vpn_ip, user_id))
    conn.commit(); conn.close()


# -------- Delete Node ----------
# Function to delete a node

def delete_node(node_id: int):
    """
    Deletes a node from the 'nodes' table based on its ID.
    Arguments:
        node_id : ID of the node to delete.
    """
    conn = get_conn()
    conn.execute("DELETE FROM nodes WHERE id=?", (node_id,))
    conn.commit()
    conn.close()

# -------- Delete User ----------
# Function to delete a user
 
def delete_user(user_id: int):
    """
    Deletes a user from the 'users' table based on its ID.
    Arguments:
        user_id : ID of the user to delete.
    """
    conn = get_conn()
    conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
