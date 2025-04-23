#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
diagnostico_triple.py - Diagnostica por qué no se encuentran señales de triple coincidencia
"""

import os
import mysql.connector
import pandas as pd
from dotenv import load_dotenv
import json
import sys
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', '21blackjack'),
    'database': os.getenv('MYSQL_DATABASE', 'binance_lob')
}

def connect_db():
    """Conectar a la base de datos."""
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    print(f"Conectado a base de datos MySQL: {db_config['database']}")
    return conn, cursor

def analyze_components(symbol="BTCUSDT", timeframe="5m"):
    """Analizar cada componente para diagnóstico"""
    conn, cursor = connect_db()
    
    try:
        print(f"\n===== DIAGNÓSTICO PARA {symbol}-{timeframe} =====")
        
        # Verificar estructura de las tablas
        print("\nAnalizando estructura de las tablas...")
        
        # Verificar key_candles
        cursor.execute("SHOW COLUMNS FROM key_candles")
        key_candles_columns = [col['Field'] for col in cursor.fetchall()]
        print(f"Columnas en key_candles: {key_candles_columns}")
        
        # Verificar detect_accumulation_zone_results
        cursor.execute("SHOW COLUMNS FROM detect_accumulation_zone_results")
        zone_columns = [col['Field'] for col in cursor.fetchall()]
        print(f"Columnas en detect_accumulation_zone_results: {zone_columns}")
        
        # Verificar mini_trend_results
        mini_trend_table = "mini_trend_results"
        cursor.execute(f"SHOW TABLES LIKE '{mini_trend_table}'")
        if cursor.fetchone():
            cursor.execute(f"SHOW COLUMNS FROM {mini_trend_table}")
            trend_columns = [col['Field'] for col in cursor.fetchall()]
            print(f"Columnas en {mini_trend_table}: {trend_columns}")
        else:
            print(f"Tabla {mini_trend_table} no existe")
            
        # Adaptando consultas a la estructura real
        # Determinar si hay columnas de símbolo y timeframe
        has_symbol_key_candles = 'symbol' in key_candles_columns
        has_timeframe_key_candles = 'timeframe' in key_candles_columns
        
        # Verificar velas clave
        where_clause = []
        if has_symbol_key_candles:
            where_clause.append(f"symbol = '{symbol}'")
        if has_timeframe_key_candles:
            where_clause.append(f"timeframe = '{timeframe}'")
            
        if where_clause:
            where_sql = "WHERE " + " AND ".join(where_clause)
        else:
            where_sql = ""
            
        cursor.execute(f"SELECT COUNT(*) as total FROM key_candles {where_sql}")
        key_candles_count = cursor.fetchone()['total']
        print(f"\n1. Velas clave encontradas: {key_candles_count}")
        
        if key_candles_count == 0:
            print("   [ERROR] No hay velas clave detectadas. Revise los parámetros de detección.")
            return
            
        # 2. Verificar zonas de acumulación
        has_symbol_zone = 'symbol' in zone_columns
        has_timeframe_zone = 'timeframe' in zone_columns
        
        where_clause = []
        if has_symbol_zone:
            where_clause.append(f"symbol = '{symbol}'")
        if has_timeframe_zone:
            where_clause.append(f"timeframe = '{timeframe}'")
            
        if where_clause:
            where_sql = "WHERE " + " AND ".join(where_clause)
        else:
            where_sql = ""
            
        cursor.execute(f"SELECT COUNT(*) as total FROM detect_accumulation_zone_results {where_sql}")
        zone_count = cursor.fetchone()['total']
        print(f"2. Zonas de acumulación encontradas: {zone_count}")
        
        if zone_count == 0:
            print("   [ERROR] No hay zonas de acumulación detectadas. Revise los parámetros de detección.")
            return
        
        # 3. Verificar mini-tendencias
        mini_trend_table = "mini_trend_results"  # Table as in save_triple_signals.py
        cursor.execute(f"SHOW TABLES LIKE '{mini_trend_table}'")
        if cursor.fetchone():
            has_symbol_trend = 'symbol' in trend_columns
            has_timeframe_trend = 'timeframe' in trend_columns
            
            where_clause = []
            if has_symbol_trend:
                where_clause.append(f"symbol = '{symbol}'")
            if has_timeframe_trend:
                where_clause.append(f"timeframe = '{timeframe}'")
                
            if where_clause:
                where_sql = "WHERE " + " AND ".join(where_clause)
            else:
                where_sql = ""
                
            cursor.execute(f"SELECT COUNT(*) as total FROM {mini_trend_table} {where_sql}")
            trend_count = cursor.fetchone()['total']
            print(f"3. Mini-tendencias encontradas: {trend_count}")
            
            if trend_count == 0:
                print("   [ERROR] No hay mini-tendencias detectadas. Revise los parámetros de detección.")
                return
        else:
            print(f"3. [ERROR] Tabla de mini-tendencias '{mini_trend_table}' no existe.")
            return
            
        # 4. Análisis más detallado de coincidencias potenciales
        # Ver velas clave y sus índices
        fields = []
        for field in ['candle_index', 'datetime', 'is_key_candle', 'open', 'high', 'low', 'close', 'volume', 'body_percentage']:
            if field in key_candles_columns:
                fields.append(field)
                
        query = f"SELECT {', '.join(fields)} FROM key_candles {where_sql} ORDER BY candle_index"
        cursor.execute(query)
        key_candles = cursor.fetchall()
        
        # Verificar si tenemos índices de vela
        if 'candle_index' in key_candles_columns and key_candles:
            key_indices = [kc['candle_index'] for kc in key_candles]
            print(f"\n4. Análisis de coincidencias potenciales:")
            print(f"   Velas clave por índice: {key_indices}")
        else:
            print(f"\n4. No se pueden analizar coincidencias sin índices de vela.")
            return
        
        # Ver rangos de zonas
        zone_fields = []
        for field in ['id', 'start_idx', 'end_idx', 'quality_score']:
            if field in zone_columns:
                zone_fields.append(field)
                
        if not zone_fields:
            print("   [ERROR] Faltan campos críticos en tabla detect_accumulation_zone_results")
            return
            
        zone_query = f"SELECT {', '.join(zone_fields)} FROM detect_accumulation_zone_results {where_sql}"
        cursor.execute(zone_query)
        zones = cursor.fetchall()
        
        if 'start_idx' in zone_columns and 'end_idx' in zone_columns and 'quality_score' in zone_columns:
            zone_ranges = [(z['start_idx'], z['end_idx'], z['quality_score']) for z in zones]
            print(f"   Rangos de zonas (inicio-fin, calidad): {zone_ranges}")
        else:
            print("   [ERROR] Falta información de índices o calidad en zonas de acumulación")
        
        # Ver rangos de mini-tendencias
        trend_fields = []
        for field in ['id', 'start_idx', 'end_idx', 'direction', 'r_squared']:
            if field in trend_columns:
                trend_fields.append(field)
                
        if not trend_fields:
            print("   [ERROR] Faltan campos críticos en tabla mini_trend_results")
            return
            
        trend_query = f"SELECT {', '.join(trend_fields)} FROM {mini_trend_table} {where_sql}"
        cursor.execute(trend_query)
        trends = cursor.fetchall()
        
        if 'start_idx' in trend_columns and 'end_idx' in trend_columns and 'direction' in trend_columns and 'r_squared' in trend_columns:
            trend_ranges = [(t['start_idx'], t['end_idx'], t['direction'], t['r_squared']) for t in trends]
            print(f"   Rangos de mini-tendencias (inicio-fin, dirección, R²): {trend_ranges}")
        else:
            print("   [ERROR] Falta información de índices, dirección o R² en mini-tendencias")
        
        # Simulación de consulta de triple_signals pero con criterios más flexibles para diagnóstico
        tolerance = 5  # Tolerancia más amplia para diagnóstico
        
        print(f"\n5. Verificando posibles coincidencias con tolerancia ampliada ({tolerance} velas):")
        
        for kc in key_candles:
            idx = kc['candle_index']
            in_zone = False
            zone_info = None
            
            for z in zones:
                if idx >= z['start_idx'] - tolerance and idx <= z['end_idx'] + tolerance:
                    in_zone = True
                    zone_info = z
                    break
                    
            if not in_zone:
                continue
                
            in_trend = False
            trend_info = None
            
            for t in trends:
                if idx >= t['start_idx'] - tolerance and idx <= t['end_idx'] + tolerance:
                    in_trend = True
                    trend_info = t
                    break
                    
            if in_zone and in_trend:
                # Verficamos si tenemos datetime o usamos solo el índice
                datetime_str = f", Datetime: {kc['datetime']}" if 'datetime' in kc else ""
                print(f"   [POSIBLE COINCIDENCIA] Índice: {idx}{datetime_str}")
                
                # Solo mostrar información si está disponible
                if 'volume' in kc and 'body_percentage' in kc:
                    print(f"      Vela Clave: Volumen={kc['volume']:.2f}, Cuerpo={kc['body_percentage']:.2f}%")
                else:
                    print("      Vela Clave: [Información no disponible]")
                    
                if 'id' in zone_info and 'quality_score' in zone_info:
                    print(f"      Zona: ID={zone_info['id']}, Calidad={zone_info['quality_score']:.4f}")
                else:
                    print("      Zona: [Información no disponible]")
                    
                if 'id' in trend_info and 'direction' in trend_info and 'r_squared' in trend_info:
                    print(f"      Tendencia: ID={trend_info['id']}, Dirección={trend_info['direction']}, R²={trend_info['r_squared']:.4f}")
                else:
                    print("      Tendencia: [Información no disponible]")
                    
                print(f"      NOTA: Esta coincidencia requiere {tolerance} velas de tolerancia.")
                
        # 5. Verificar configuración de calidad mínima
        print("\n6. Verificación de requisitos de calidad mínima:")
        print(f"   Zonas de acumulación con calidad >= 0.5: ", end="")
        quality_where_clause = where_clause.copy() if has_symbol_zone or has_timeframe_zone else []
        quality_where_clause.append("quality_score >= 0.5")
        quality_where_sql = "WHERE " + " AND ".join(quality_where_clause) if quality_where_clause else ""
        cursor.execute(f"SELECT COUNT(*) as total FROM detect_accumulation_zone_results {quality_where_sql}")
        quality_zones = cursor.fetchone()['total']
        print(f"{quality_zones} de {zone_count}")
        
        print(f"   Mini-tendencias con R² >= 0.45: ", end="")
        quality_where_clause = where_clause.copy() if has_symbol_trend or has_timeframe_trend else []
        quality_where_clause.append("r_squared >= 0.45")
        quality_where_sql = "WHERE " + " AND ".join(quality_where_clause) if quality_where_clause else ""
        cursor.execute(f"SELECT COUNT(*) as total FROM {mini_trend_table} {quality_where_sql}")
        quality_trends = cursor.fetchone()['total']
        print(f"{quality_trends} de {trend_count}")
        
        print(f"   Velas clave con cuerpo >= 15%: ", end="")
        if 'body_percentage' in key_candles_columns:
            quality_where_clause = where_clause.copy() if has_symbol_key_candles or has_timeframe_key_candles else []
            quality_where_clause.append("body_percentage >= 15")
            quality_where_sql = "WHERE " + " AND ".join(quality_where_clause) if quality_where_clause else ""
            cursor.execute(f"SELECT COUNT(*) as total FROM key_candles {quality_where_sql}")
            quality_candles = cursor.fetchone()['total']
            print(f"{quality_candles} de {key_candles_count}")
        else:
            print("N/A (columna no disponible)")
        
        # 6. Recomendaciones
        print("\n7. Recomendaciones:")
        if quality_zones < zone_count * 0.3:
            print("   • Considere reducir el umbral de calidad para zonas de acumulación (actualmente 0.5)")
        if quality_trends < trend_count * 0.3:
            print("   • Considere reducir el umbral de R² para mini-tendencias (actualmente 0.45)")
        if quality_candles < key_candles_count * 0.3:
            print("   • Considere reducir el umbral de tamaño de cuerpo para velas clave")
        
        print("   • Aumente la tolerancia de proximidad entre componentes (actualmente 3 velas)")
        print("   • Verifique si los períodos de los datos coinciden entre detecciones")
        
    except Exception as e:
        print(f"Error realizando diagnóstico: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        cursor.close()
        conn.close()
        print("\nConexión cerrada.")

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Diagnosticar problemas en detección de triple coincidencia")
    parser.add_argument('--symbol', type=str, default='BTCUSDT', help='Símbolo (por defecto: BTCUSDT)')
    parser.add_argument('--timeframe', type=str, default='5m', help='Timeframe (por defecto: 5m)')
    
    args = parser.parse_args()
    
    analyze_components(args.symbol, args.timeframe)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error general: {e}")
        import traceback
        traceback.print_exc()
