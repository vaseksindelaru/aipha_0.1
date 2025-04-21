"""
save_detect_candles.py - Módulo para guardar resultados de la detección Shakeout en base de datos

Este módulo permite guardar los resultados de la detección de velas clave en una base de datos MySQL para su análisis posterior.
Ubicación: aipha/programs/stable/save_detect_candles.py
"""

import os
import sys
import mysql.connector
from mysql.connector import Error
import pandas as pd
import numpy as np
import json
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.abspath(os.path.join(os.path.dirname(__file__), '../../config/.env')), override=True)

import sys
import mysql.connector
from mysql.connector import Error
import pandas as pd
import numpy as np
import json
from datetime import datetime
import traceback

# Ajuste de path para importar desde el módulo padre
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from detect_candle import Detector

class DetectionResultSaver:
    """
    Clase para guardar resultados de la estrategia Shakeout en la base de datos binance_lob.
    Maneja la conexión y métodos para almacenar datos de velas clave y parámetros de detección.
    """
    def __init__(self, host=None, user=None, password=None, database=None):
        self.db_config = {
            'host': host or os.getenv('MYSQL_HOST', 'localhost'),
            'user': user or os.getenv('MYSQL_USER', 'root'),
            'password': password or os.getenv('MYSQL_PASSWORD', ''),
            'database': database or os.getenv('MYSQL_DATABASE', 'binance_lob')
        }
        print(f"Database configuration: host={self.db_config['host']}, user={self.db_config['user']}, database={self.db_config['database']}")
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
                print(f"Connected to MySQL database: {self.db_config['database']}")
                return True
        except Error as e:
            print(f"Error connecting to MySQL database: {e}")
            return False

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("Database connection closed.")

    def save_results(self, results, detection_params, table_name='shakeout_key_candles'):
        if not self.connection or not self.connection.is_connected():
            print("Not connected to database.")
            return False
        try:
            # Crea tabla si no existe
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                candle_index INT,
                open FLOAT,
                high FLOAT,
                low FLOAT,
                close FLOAT,
                volume FLOAT,
                volume_percentile FLOAT,
                body_percentage FLOAT,
                is_key_candle BOOLEAN,
                detection_params JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB;
            """
            self.cursor.execute(create_table_query)
            self.connection.commit()
            # Inserta resultados
            insert_query = f"""
            INSERT INTO {table_name} (
                candle_index, open, high, low, close, volume, volume_percentile, body_percentage, is_key_candle, detection_params
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            for res in results:
                params_json = json.dumps(detection_params)
                self.cursor.execute(insert_query, (
                    res['index'], res['open'], res['high'], res['low'], res['close'],
                    res['volume'], res['volume_percentile'], res['body_percentage'],
                    res['is_key_candle'], params_json
                ))
            self.connection.commit()
            print(f"Inserted {len(results)} key candles into {table_name}.")
            return True
        except Exception as e:
            print(f"Error saving results: {e}")
            traceback.print_exc()
            return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Save Shakeout detection results to DB (AIPHA version)")
    parser.add_argument('--csv', type=str, required=True, help='Path to CSV file')
    args = parser.parse_args()

    detector = Detector(args.csv)
    detector.set_detection_params(80, 30, 50)
    results = detector.process_csv()

    saver = DetectionResultSaver()
    if saver.connect():
        saver.save_results(results, detector.detection_params)
        saver.close()
