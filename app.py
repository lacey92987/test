from flask import Flask
from flask import jsonify
from flask import request
from flask_cors import CORS
import psycopg2
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List

# Define database connection parameters
DB_PARAMS = {
    'user': 'lcdouglas',
    'password': 'N3/tle12',
    'host': 'lcdouglas.postgres.database.azure.com',
    'port': 5432,
    'database': 'database'
}

# Function to create a database connection
def create_connection():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        print("Connected to PostgreSQL database successfully")
        return conn
    except psycopg2.Error as e:

        print("Error connecting to PostgreSQL database:", e)
        return None  # Return None to indicate connection failure

# Call the create_connection function to establish a connection
conn = create_connection()

app = Flask(__name__) 
CORS(app)

@app.route('/compare_power', methods=['GET'])
def compare_power():
    hero_id1 = request.args.get('hero_id1')
    hero_id2 = request.args.get('hero_id2')

    if not hero_id1 or not hero_id2:
        return jsonify({"error": "Both hero_id1 and hero_id2 parameters are required"}), 400

    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT h1.hero_name AS hero_name1, SUM(p1.power_level) AS total_power1,
           h2.hero_name AS hero_name2, SUM(p2.power_level) AS total_power2
        FROM heroes AS h1
        JOIN heroes_powers AS hp1 ON h1.hero_id = hp1.hero_id
        JOIN powers AS p1 ON hp1.power_id = p1.power_id
        JOIN heroes AS h2 ON h2.hero_id = ?
        JOIN heroes_powers AS hp2 ON h2.hero_id = hp2.hero_id
        JOIN powers AS p2 ON hp2.power_id = p2.power_id
        WHERE h1.hero_id = ? AND h2.hero_id = ?
    """, (hero_id2, hero_id1, hero_id2))

    result = cursor.fetchone()
    conn.close()

    if result is None:
        return jsonify({"error": "One or both heroes not found"}), 404

    hero_name1, total_power1, hero_name2, total_power2 = result
    if total_power1 > total_power2:
        winner = hero_name1
    elif total_power1 < total_power2:
        winner = hero_name2
    else:
        winner = "Tie"

    response = {
        "hero_id1": hero_id1,
        "hero_name1": hero_name1,
        "total_power1": total_power1,
        "hero_id2": hero_id2,
        "hero_name2": hero_name2,
        "total_power2": total_power2,
        "winner": winner,
    }

    return jsonify(response)
    
###
# Main
###
if __name__ == '__main__':
    # This says: if this file is run directly, then run the Flask app
    app.run(debug=True, use_reloader=False, passthrough_errors=True)
