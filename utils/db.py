import os
import sqlite3
import json
from datetime import datetime
from config.settings import DB_PATH

def init_db():
    """
    Initializes the SQLite database tables if they do not exist.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table for execution runs (sessions)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            trace_id TEXT PRIMARY KEY,
            filename TEXT,
            timestamp TEXT,
            context TEXT
        )
    """)
    
    # Create table for Agent-to-Agent message logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS a2a_messages (
            message_id TEXT PRIMARY KEY,
            trace_id TEXT,
            from_agent TEXT,
            to_agent TEXT,
            task TEXT,
            payload TEXT,
            status TEXT,
            result TEXT,
            timestamp TEXT,
            latency_ms INTEGER
        )
    """)
    
    conn.commit()
    conn.close()

def log_message_to_db(msg):
    """
    Saves an AgentMessage to the SQLite database.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Standardize values for database entry
    payload_str = json.dumps(msg.payload)
    result_str = json.dumps(msg.result) if msg.result is not None else None
    ts_str = msg.timestamp.isoformat() if hasattr(msg.timestamp, 'isoformat') else str(msg.timestamp)
    
    cursor.execute("""
        INSERT OR REPLACE INTO a2a_messages 
        (message_id, trace_id, from_agent, to_agent, task, payload, status, result, timestamp, latency_ms)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        msg.message_id,
        msg.trace_id,
        msg.from_agent,
        msg.to_agent,
        msg.task,
        payload_str,
        msg.status,
        result_str,
        ts_str,
        msg.latency_ms
    ))
    
    conn.commit()
    conn.close()

def get_messages_for_trace(trace_id: str) -> list:
    """
    Retrieves all A2A messages associated with a trace_id, sorted by timestamp.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT message_id, trace_id, from_agent, to_agent, task, payload, status, result, timestamp, latency_ms
        FROM a2a_messages
        WHERE trace_id = ?
        ORDER BY timestamp ASC
    """, (trace_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    messages = []
    for r in rows:
        messages.append({
            "message_id": r[0],
            "trace_id": r[1],
            "from_agent": r[2],
            "to_agent": r[3],
            "task": r[4],
            "payload": json.loads(r[5]) if r[5] else {},
            "status": r[6],
            "result": json.loads(r[7]) if r[7] else {},
            "timestamp": r[8],
            "latency_ms": r[9]
        })
    return messages

def save_session_context(trace_id: str, filename: str, context: dict):
    """
    Saves or updates pipeline execution results context for a trace_id.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    context_str = json.dumps(context)
    ts_str = datetime.now().isoformat()
    
    cursor.execute("""
        INSERT OR REPLACE INTO sessions (trace_id, filename, timestamp, context)
        VALUES (?, ?, ?, ?)
    """, (trace_id, filename, ts_str, context_str))
    
    conn.commit()
    conn.close()

def get_all_sessions() -> list:
    """
    Retrieves metadata of all execution sessions.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT trace_id, filename, timestamp FROM sessions ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    
    sessions = []
    for r in rows:
        sessions.append({
            "trace_id": r[0],
            "filename": r[1],
            "timestamp": r[2]
        })
    return sessions

def get_session_context(trace_id: str) -> dict:
    """
    Retrieves full parsed results context for a trace_id.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT context FROM sessions WHERE trace_id = ?", (trace_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return json.loads(row[0])
    return {}
