import paho.mqtt.client as mqtt
import json
import sqlite3
import os

# --- Configuration ---
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "lab/rfid/access"
DB_FILE = "access_control.db"

# --- Database Setup ---
def init_db():
    """Creates the table if it does not exist."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS access_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    card_id TEXT NOT NULL,
                    reader_id TEXT,
                    timestamp TEXT NOT NULL
                )
            ''')
            conn.commit()
            print("Database initialized.")
    except sqlite3.Error as e:
        print(f"Database Error: {e}")

def save_to_db(data):
    """Inserts the payload data into the SQLite database."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO access_logs (card_id, reader_id, timestamp)
                VALUES (?, ?, ?)
            ''', (data.get('card_id'), data.get('reader_id'), data.get('timestamp')))
            conn.commit()
            print(f"Saved to DB: {data['card_id']} at {data['timestamp']}")
    except sqlite3.Error as e:
        print(f"Failed to write to DB: {e}")

# --- MQTT Callbacks ---
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to Broker. Subscribing to {MQTT_TOPIC}")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Connection failed with code {rc}")

def on_message(client, userdata, msg):
    try:
        # Decode the JSON payload
        payload_str = msg.payload.decode("utf-8")
        data = json.loads(payload_str)
        
        # Save to Database
        save_to_db(data)
        
    except json.JSONDecodeError:
        print("Received invalid JSON format")
    except Exception as e:
        print(f"Error processing message: {e}")

# --- Main Execution ---
if __name__ == "__main__":
    # Ensure DB exists before starting
    init_db()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    print("Logger Service Started...")
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        # loop_forever handles automatic reconnects
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nDisconnecting...")
        client.disconnect()
    except Exception as e:
        print(f"Fatal Error: {e}")
