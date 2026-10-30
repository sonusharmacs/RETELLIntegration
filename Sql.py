import sqlite3
import pandas as pd


def initialize_database():
    conn = sqlite3.connect('claims.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_number TEXT NOT NULL,
            empid TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            Amount REAL NOT NULL,
            Status TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def insert_claim(claim_number, empid, Amount, Status):
    conn = sqlite3.connect('claims.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO claims (claim_number, empid, Amount, Status)
        VALUES (?, ?, ?, ?)
    ''', (claim_number, empid, Amount, Status))
    conn.commit()
    conn.close()
    
def retrieve_claim(empid):
    conn = sqlite3.connect('claims.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM claims WHERE empid = ?
    ''', (empid,))
    claim = cursor.fetchone()
    conn.close()
    return claim    

def delete_claim(claim_number):
    conn = sqlite3.connect('claims.db')
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM claims WHERE claim_number = ?
    ''', (claim_number,))
    conn.commit()
    conn.close()
    
def delete_all_claims():
    conn = sqlite3.connect('claims.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM claims')
    conn.commit()
    conn.close()

def get_all_claims() -> pd.DataFrame:
    conn = sqlite3.connect('claims.db')
    df = pd.read_sql_query("SELECT * FROM claims", conn)
    conn.close()
    return df