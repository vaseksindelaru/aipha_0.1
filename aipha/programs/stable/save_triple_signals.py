#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
save_triple_signals.py - Guarda señales de triple coincidencia en una tabla dedicada.

Este script identifica y almacena en una tabla todas las señales que cumplen con las tres condiciones:
1. Son velas clave (según criterios de volumen y tamaño de cuerpo)
2. Están dentro de zonas de acumulación
3. Forman parte de mini-tendencias identificables

Estas señales de "triple verificación" tienen mayor probabilidad de éxito.
"""

import os
import sys
import argparse
import logging
import mysql.connector
from mysql.connector import errors
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("aipha/logs/triple_signals.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

class TripleSignalSaver:
    """Clase para identificar y guardar señales de triple coincidencia."""
    
    def __init__(self):
        """Inicializa la conexión a la base de datos y configuraciones."""
        self.host = os.getenv('MYSQL_HOST', 'localhost')
        self.user = os.getenv('MYSQL_USER', 'root')
        self.password = os.getenv('MYSQL_PASSWORD', '21blackjack')
        self.database = os.getenv('MYSQL_DATABASE', 'binance_lob')
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Establece conexión con la base de datos MySQL."""
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.conn.cursor(dictionary=True)
            logger.info(f"Conectado a base de datos MySQL: {self.database}")
            return True
        except Exception as e:
            logger.error(f"Error conectando a la base de datos: {e}")
            return False
    
    def close(self):
        """Cierra la conexión a la base de datos."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            logger.info("Conexión a la base de datos cerrada")
    
    def create_triple_signals_table(self):
        """Elimina y vuelve a crear la tabla triple_signals con todas las columnas necesarias."""
        try:
            # Primero verificamos si la tabla existe
            self.cursor.execute("SHOW TABLES LIKE 'triple_signals'")
            table_exists = self.cursor.fetchone() is not None
            
            # Si existe, la eliminamos para poder recrearla con todas las columnas
            if table_exists:
                logger.info("Tabla triple_signals existente, eliminándola para recrear")
                self.cursor.execute("DROP TABLE triple_signals")
                self.conn.commit()
            
            # Creamos la tabla con la estructura completa
            create_table_query = """
            CREATE TABLE triple_signals (
                id INT AUTO_INCREMENT PRIMARY KEY,
                symbol VARCHAR(20) NOT NULL,
                timeframe VARCHAR(10) NOT NULL,
                candle_index INT NOT NULL,
                datetime DATETIME,
                open FLOAT,
                high FLOAT,
                low FLOAT,
                close FLOAT,
                volume FLOAT,
                body_percentage FLOAT,
                zone_id INT,
                zone_quality_score FLOAT,
                zone_start_datetime DATETIME,
                zone_end_datetime DATETIME,
                mini_trend_id INT,
                trend_direction VARCHAR(10),
                trend_slope FLOAT,
                trend_r_squared FLOAT,
                trend_start_datetime DATETIME,
                trend_end_datetime DATETIME,
                signal_strength FLOAT,
                combined_score FLOAT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_signal (symbol, timeframe, candle_index)
            )
            """
            self.cursor.execute(create_table_query)
            self.conn.commit()
            logger.info("Tabla triple_signals creada correctamente con todas las columnas")
            return True
        except Exception as e:
            logger.error(f"Error creando tabla triple_signals: {e}")
            return False
    
    def find_triple_signals(self, symbol, timeframe):
        """
        Encuentra señales que coinciden en los tres criterios:
        1. Velas clave
        2. Dentro de zonas de acumulación
        3. Parte de mini-tendencias
        """
        try:
            # Verificar tabla de mini-tendencias
            mini_trend_table = 'mini_trend_results'  # Sabemos que esta tabla existe
            logger.info(f"Usando tabla de mini-tendencias: {mini_trend_table}")
            
            # Verificar si la tabla key_candles tiene mini_trend_id
            self.cursor.execute("DESCRIBE key_candles")
            columns = self.cursor.fetchall()
            column_names = [col['Field'] for col in columns]
            
            has_mini_trend_id = 'mini_trend_id' in column_names
            has_in_accumulation_zone = 'in_accumulation_zone' in column_names
            
            # Si no existen las columnas necesarias, debemos modificar la consulta
            # y posiblemente salir si no podemos establecer las relaciones
            if not has_mini_trend_id or not has_in_accumulation_zone:
                logger.warning(f"La tabla key_candles no tiene las columnas requeridas: mini_trend_id={has_mini_trend_id}, in_accumulation_zone={has_in_accumulation_zone}")
                
                # Primero detectemos si podemos establecer una relación entre velas clave y zonas
                if not has_in_accumulation_zone:
                    logger.info("Intentando determinar relación entre velas clave y zonas de acumulación")
                    # Una alternativa es usar los rangos de índices para determinar si la vela está en una zona
                    
                # Si no podemos relacionar velas con mini-tendencias, consideremos usar índices
                if not has_mini_trend_id:
                    logger.info("Intentando determinar relación entre velas clave y mini-tendencias por índices")
                    # Podemos relacionar velas y mini-tendencias por rango de índices
            
            # Construyamos una consulta adaptada a la estructura real
            query = f"""
            SELECT 
                kc.id as key_candle_id,
                '{symbol}' as symbol,
                '{timeframe}' as timeframe,
                kc.candle_index,
                kc.open,
                kc.high,
                kc.low,
                kc.close,
                kc.volume,
                kc.body_percentage,
                daz.id as zone_id,
                daz.quality_score as zone_quality_score,
                daz.datetime_start as zone_start_datetime,
                daz.datetime_end as zone_end_datetime,
                mt.id as trend_id,
                mt.direction as trend_direction,
                mt.slope as trend_slope,
                mt.r_squared as trend_r_squared,
                mt.start_time as trend_start_datetime,
                mt.end_time as trend_end_datetime
            FROM key_candles kc
            JOIN detect_accumulation_zone_results daz ON 
                daz.symbol = '{symbol}' AND
                daz.timeframe = '{timeframe}' AND
                kc.candle_index >= daz.start_idx AND
                kc.candle_index <= daz.end_idx
            JOIN {mini_trend_table} mt ON 
                kc.candle_index >= mt.start_idx AND
                kc.candle_index <= mt.end_idx
            WHERE 
                kc.is_key_candle = TRUE
            ORDER BY kc.candle_index
            """
            
            logger.info("Ejecutando consulta para encontrar señales de triple coincidencia")
            
            # Ejecutar la consulta sin parámetros ya que los incluimos directamente
            self.cursor.execute(query)
            signals = self.cursor.fetchall()
            logger.info(f"Encontradas {len(signals)} señales de triple coincidencia para {symbol}-{timeframe}")
            return signals
        except Exception as e:
            logger.error(f"Error buscando señales de triple coincidencia: {e}")
            return []
    
    def calculate_signal_strength(self, signal):
        """
        Calcula una puntuación de fuerza para cada señal basada en:
        - Calidad de la zona de acumulación
        - Fuerza de la mini-tendencia (r-cuadrado)
        - Volumen y tamaño de cuerpo de la vela clave
        
        Devuelve un valor entre 0 y 1, donde valores más altos indican señales más fuertes.
        """
        try:
            # Pesos de cada componente (ajustables)
            zone_weight = 0.35
            trend_weight = 0.35
            candle_weight = 0.30
            
            # Normalizar calidad de zona (típicamente entre 0 y 1)
            zone_quality = min(signal['zone_quality_score'], 1.0)
            
            # Normalizar r-cuadrado (ya está entre 0 y 1)
            trend_quality = signal['trend_r_squared']
            
            # Normalizar métricas de vela
            volume_norm = min(signal['volume'] / 100, 1.0)  # Ajustar según escala de volumen
            body_norm = signal['body_percentage'] / 100  # Convertir a decimal
            candle_quality = 0.6 * volume_norm + 0.4 * body_norm
            
            # Calcular puntuación combinada ponderada
            signal_strength = (
                zone_weight * zone_quality +
                trend_weight * trend_quality +
                candle_weight * candle_quality
            )
            
            return round(signal_strength, 4)
        except Exception as e:
            logger.warning(f"Error calculando fuerza de señal: {e}")
            return 0.5  # Valor por defecto
    
    def calculate_combined_score(self, signal):
        """
        Calcula una puntuación combinada incluyendo factores adicionales como:
        - La dirección de la tendencia
        - La pendiente de la tendencia
        
        Esta puntuación puede usarse para clasificar las señales.
        """
        try:
            base_strength = self.calculate_signal_strength(signal)
            
            # Ajuste por dirección de tendencia (por ejemplo, bonus para tendencias alcistas)
            # Este ajuste puede personalizarse según la estrategia
            direction_factor = 1.1 if signal['trend_direction'] == 'alcista' else 0.9
            
            # Ajuste por pendiente (normalizada)
            slope_abs = abs(signal['trend_slope'])
            slope_factor = min(slope_abs / 100, 1.0) * 0.2 + 0.9  # Entre 0.9 y 1.1
            
            combined_score = base_strength * direction_factor * slope_factor
            
            return round(min(combined_score, 1.0), 4)  # Limitar a máximo 1.0
        except Exception as e:
            logger.warning(f"Error calculando puntuación combinada: {e}")
            return base_strength
    
    def save_signals(self, symbol, timeframe):
        """Guarda las señales de triple coincidencia en la tabla."""
        if not self.connect():
            return False
        
        try:
            # Crear tabla si no existe
            if not self.create_triple_signals_table():
                return False
            
            # Encontrar señales
            signals = self.find_triple_signals(symbol, timeframe)
            if not signals:
                logger.info(f"No se encontraron señales de triple coincidencia para {symbol}-{timeframe}")
                return True
            
            # Asegurarnos que no hay registros previos que puedan causar duplicados
            # Primero, eliminamos cualquier registro con el mismo symbol/timeframe
            delete_query = "DELETE FROM triple_signals WHERE symbol = %s AND timeframe = %s"
            self.cursor.execute(delete_query, (symbol, timeframe))
            self.conn.commit()
            
            # Para mayor seguridad, también podemos eliminar registros específicos por índice
            if signals:
                candle_indices = [signal['candle_index'] for signal in signals]
                placeholder = ', '.join(['%s'] * len(candle_indices))
                delete_specific_query = f"DELETE FROM triple_signals WHERE symbol = %s AND timeframe = %s AND candle_index IN ({placeholder})"
                params = [symbol, timeframe] + candle_indices
                self.cursor.execute(delete_specific_query, params)
                self.conn.commit()
                logger.info(f"Eliminados registros específicos para candle_index: {candle_indices}")
            
            # Insertar nuevas señales
            insert_count = 0
            insert_query = """
            INSERT INTO triple_signals (
                symbol, timeframe, candle_index, datetime, open, high, low, close, 
                volume, body_percentage, zone_id, zone_quality_score, 
                zone_start_datetime, zone_end_datetime, mini_trend_id, 
                trend_direction, trend_slope, trend_r_squared, 
                trend_start_datetime, trend_end_datetime, signal_strength, combined_score
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """
            
            for signal in signals:
                # Calcular puntuaciones
                signal_strength = self.calculate_signal_strength(signal)
                combined_score = self.calculate_combined_score(signal)
                
                # Preparar datos para inserción
                # Calcular datetime para la vela a partir de la zona y su índice
                # Primero usamos datos de zona, que son más específicos del símbolo/timeframe
                zone_start = signal.get('zone_start_datetime')
                zone_end = signal.get('zone_end_datetime')
                zone_start_idx = None
                zone_end_idx = None
                
                # Buscar los índices de inicio/fin de la zona
                self.cursor.execute(f"SELECT start_idx, end_idx FROM detect_accumulation_zone_results WHERE id = {signal['zone_id']}")
                zone_info = self.cursor.fetchone()
                if zone_info:
                    zone_start_idx = zone_info['start_idx']
                    zone_end_idx = zone_info['end_idx']
                
                # Calcular datetime aproximado para la vela
                candle_datetime = None
                if zone_start and zone_end and zone_start_idx is not None and zone_end_idx is not None:
                    # Calcular posición relativa de esta vela en la zona
                    if isinstance(zone_start, str):
                        zone_start = datetime.strptime(zone_start, '%Y-%m-%d %H:%M:%S')
                    if isinstance(zone_end, str):
                        zone_end = datetime.strptime(zone_end, '%Y-%m-%d %H:%M:%S')
                    
                    zone_duration = (zone_end - zone_start).total_seconds()
                    zone_bars = zone_end_idx - zone_start_idx + 1
                    bar_duration = zone_duration / zone_bars if zone_bars > 0 else 0
                    
                    # Posición relativa de la vela en la zona
                    bar_offset = signal['candle_index'] - zone_start_idx
                    if bar_offset >= 0 and bar_duration > 0:
                        offset_seconds = bar_offset * bar_duration
                        candle_datetime = zone_start + timedelta(seconds=offset_seconds)
                    else:
                        candle_datetime = zone_start
                else:
                    # Si no podemos calcular, usamos inicio de zona o tiempo actual como fallback
                    candle_datetime = zone_start or datetime.now()
                
                # Formateamos para inserción
                if isinstance(candle_datetime, datetime):
                    candle_datetime = candle_datetime.strftime('%Y-%m-%d %H:%M:%S')
                
                # Preparar parámetros para la consulta
                params = (
                    signal['symbol'],
                    signal['timeframe'],
                    signal['candle_index'],
                    candle_datetime,
                    signal['open'],
                    signal['high'],
                    signal['low'],
                    signal['close'],
                    signal['volume'],
                    signal['body_percentage'],
                    signal['zone_id'],
                    signal['zone_quality_score'],
                    signal['zone_start_datetime'],
                    signal['zone_end_datetime'],
                    signal['trend_id'],
                    signal['trend_direction'],
                    signal['trend_slope'],
                    signal['trend_r_squared'],
                    signal['trend_start_datetime'],
                    signal['trend_end_datetime'],
                    signal_strength,
                    combined_score
                )
                
                try:
                    self.cursor.execute(insert_query, params)
                    insert_count += 1
                except mysql.connector.errors.IntegrityError as e:
                    # Manejo específico para error de duplicado
                    if "Duplicate entry" in str(e):
                        logger.warning(f"Se omitió una señal duplicada en candle_index={signal['candle_index']}")
                    else:
                        # Re-lanzar otros errores de integridad
                        raise
            
            self.conn.commit()
            logger.info(f"Guardadas {insert_count} señales de triple coincidencia en la tabla")
            return True
            
        except Exception as e:
            logger.error(f"Error guardando señales de triple coincidencia: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            self.close()


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description='Guardar señales de triple coincidencia en una tabla')
    parser.add_argument('--symbol', type=str, default='BTCUSDT', help='Símbolo (por defecto: BTCUSDT)')
    parser.add_argument('--timeframe', type=str, default='5m', help='Timeframe (por defecto: 5m)')
    args = parser.parse_args()
    
    logger.info(f"Iniciando guardado de señales de triple coincidencia para {args.symbol}-{args.timeframe}")
    
    saver = TripleSignalSaver()
    if saver.save_signals(args.symbol, args.timeframe):
        logger.info("Proceso completado exitosamente")
        return 0
    else:
        logger.error("Error en el proceso de guardado de señales")
        return 1


if __name__ == "__main__":
    sys.exit(main())
