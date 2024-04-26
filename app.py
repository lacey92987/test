from flask import Flask
from flask import jsonify
from flask import request
from flask_cors import CORS
import psycopg2 
import logging
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
@dataclass
class Power:
    """Class to represent a power."""
    power_name: str
    power_level: int = 0
    power_type: str = None
    power_id: int = None
    
    def to_dictionary(self):
        """Returns a dictionary representation of the power"""
        return asdict(self)
@dataclass
class Hero:
    """Class to represent a hero."""
    hero_name: str
    gender: str = None
    eye_color: str = None
    species: str = None
    hair_color: str = None
    height: float = None
    weight: float = None
    publisher: str = None
    skin_color: str = None
    alignment: str = None
    hero_id: int = None
    powers: List[Power] = field(default_factory=list)
    
    def to_dictionary(self, include_powers=False):
        """Returns a dictionary representation of the hero"""
        hero_dict = asdict(self)
        if not include_powers:
            hero_dict.pop('powers')
        else:
            hero_dict['powers'] = [power.to_dictionary() for power in self.powers]
        return hero_dict   

@app.route('/heroes', methods=['GET'])
def get_heroes():
    print("Success")
    limit = request.args.get('limit', 10)

    heroes = select_all_heroes(limit)
    return jsonify([hero.to_dictionary() for hero in heroes])

def select_all_heroes(limit):
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    cur.execute('SELECT * FROM heroes LIMIT %s', (limit,))
    results = cur.fetchall()
    heroes = []
    for result in results:
        hero = Hero(result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8], result[9], result[10], result[0])
        heroes.append(hero)
    return heroes
###
# Main
###
if __name__ == '__main__':
    # This says: if this file is run directly, then run the Flask app
    app.run(debug=True, use_reloader=False, passthrough_errors=True)
