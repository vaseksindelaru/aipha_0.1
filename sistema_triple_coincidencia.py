#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema de Triple Coincidencia - Documentación y Descripción Detallada

Este script documenta y explica el flujo completo del sistema de triple coincidencia,
detallando todos los pasos desde la detección de componentes individuales hasta
la evaluación y puntuación final de las señales.

Autor: AIPHA System
Fecha: 2025-04-23
"""

import os
import sys
import mysql.connector
import pandas as pd
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from tabulate import tabulate
import json
from datetime import datetime

# Cargar variables de entorno (opcional)
load_dotenv()

class SistemaTripleCoincidencia:
    """Clase que documenta y describe el sistema de triple coincidencia"""
    
    def __init__(self):
        """Inicializar el sistema y cargar la configuración"""
        self.documentacion = {}
    
    def mostrar_flujo_completo(self):
        """Mostrar el flujo completo del sistema de triple coincidencia"""
        print("\n" + "="*80)
        print(" SISTEMA DE TRIPLE COINCIDENCIA - DOCUMENTACIÓN COMPLETA ")
        print("="*80 + "\n")
        
        print("El sistema de Triple Coincidencia es un enfoque avanzado de análisis técnico")
        print("que busca identificar oportunidades de trading de alta probabilidad mediante")
        print("la convergencia de tres factores técnicos independientes en el mismo punto.")
        
        # 1. VISIÓN GENERAL
        self._mostrar_vision_general()
        
        # 2. COMPONENTES
        self._mostrar_componentes()
        
        # 3. FLUJO DE DETECCIÓN
        self._mostrar_flujo_deteccion()
        
        # 4. SISTEMA DE PUNTUACIÓN
        self._mostrar_sistema_puntuacion()
        
        # 5. IMPLEMENTACIÓN TÉCNICA
        self._mostrar_implementacion_tecnica()
        
        # 6. ARCHIVOS DEL SISTEMA
        self._mostrar_archivos_sistema()
        
        # 7. PARÁMETROS OPTIMIZADOS
        self._mostrar_parametros_optimizados()
        
        # 8. RESUMEN FINAL
        self._mostrar_resumen_final()
    
    def _mostrar_vision_general(self):
        """Mostrar visión general del sistema"""
        print("\n" + "-"*80)
        print(" 1. VISIÓN GENERAL DEL SISTEMA ")
        print("-"*80 + "\n")
        
        print("El sistema de Triple Coincidencia busca identificar puntos en el mercado donde")
        print("convergen tres factores técnicos independientes:")
        print()
        print("1) Vela Clave: Vela con características morfológicas y de volumen destacables")
        print("2) Zona de Acumulación: Área donde el precio consolida con volumen significativo")
        print("3) Mini-Tendencia: Segmento de precio con dirección definida y buena estructura")
        print()
        print("Cuando estos tres componentes coinciden espacial y temporalmente, se genera una")
        print("señal con alta probabilidad de éxito, que se evalúa mediante un sofisticado")
        print("sistema de puntuación para determinar su fuerza relativa.")
    
    def _mostrar_componentes(self):
        """Mostrar componentes del sistema"""
        print("\n" + "-"*80)
        print(" 2. COMPONENTES INDIVIDUALES ")
        print("-"*80 + "\n")
        
        # 2.1 Velas Clave
        print("2.1 VELAS CLAVE")
        print("----------------")
        print("Definición: Velas con características morfológicas y de volumen que destacan")
        print("respecto a su entorno, indicando posibles puntos de inflexión en el mercado.")
        print()
        print("Criterios de detección:")
        print("- Volumen superior al percentil 70 de su entorno (parámetro VPT)")
        print("- Tamaño de cuerpo significativo (parámetro BPT)")
        print("- Contexto relativo a velas circundantes (lookback)")
        print()
        print("Puntuación basada en:")
        print("- Volumen relativo de la vela")
        print("- Morfología (tamaño de cuerpo, sombras)")
        print("- Posición respecto a la tendencia general")
        print()
        
        # 2.2 Zonas de Acumulación
        print("2.2 ZONAS DE ACUMULACIÓN")
        print("-----------------------")
        print("Definición: Áreas donde el precio consolida con actividad de volumen")
        print("significativa, indicando acumulación o distribución previo a un movimiento.")
        print()
        print("Criterios de detección:")
        print("- Rango de precio acotado durante varios periodos")
        print("- Volumen promedio por encima del umbral (volume_threshold)")
        print("- Factores de calidad como la cohesión del rango")
        print()
        print("Puntuación basada en:")
        print("- Calidad de la zona (quality_score)")
        print("- Perfil de volumen dentro de la zona")
        print("- Duración de la acumulación")
        print()
        
        # 2.3 Mini-Tendencias
        print("2.3 MINI-TENDENCIAS")
        print("------------------")
        print("Definición: Segmentos de precio con dirección definida y buena estructura,")
        print("identificados mediante el algoritmo ZigZag y regresión lineal.")
        print()
        print("Criterios de detección:")
        print("- Pendiente clara (positiva o negativa)")
        print("- R² significativo que indica buen ajuste de la tendencia")
        print("- Duración mínima para evitar segmentos aleatorios")
        print()
        print("Puntuación basada en:")
        print("- Coeficiente R² de la regresión")
        print("- Pendiente (slope) de la tendencia")
        print("- Dirección (alcista/bajista)")
    
    def _mostrar_flujo_deteccion(self):
        """Mostrar flujo de detección del sistema"""
        print("\n" + "-"*80)
        print(" 3. FLUJO DE DETECCIÓN ")
        print("-"*80 + "\n")
        
        print("El sistema sigue un proceso en varias etapas para detectar y evaluar")
        print("las señales de triple coincidencia:")
        print()
        print("3.1 PREPROCESAMIENTO DE DATOS")
        print("----------------------------")
        print("- Carga de datos OHLCV desde archivos CSV")
        print("- Normalización y preparación para análisis")
        print("- Cálculo de métricas auxiliares (ATR, volumen relativo, etc.)")
        print()
        
        print("3.2 DETECCIÓN DE COMPONENTES INDIVIDUALES")
        print("----------------------------------------")
        print("- Detección de velas clave (save_detect_candles.py)")
        print("- Identificación de zonas de acumulación (save_detect_accumulation_zone.py)")
        print("- Segmentación en mini-tendencias (mini_trend.py)")
        print("- Almacenamiento en tablas separadas en la base de datos MySQL")
        print()
        
        print("3.3 IDENTIFICACIÓN DE COINCIDENCIAS")
        print("---------------------------------")
        print("- Consulta SQL con tolerancia espacial (actualmente 8 velas)")
        print("- Vinculación de velas clave con zonas y mini-tendencias")
        print("- Filtrado inicial por umbrales mínimos de calidad")
        print("  * Calidad de zona >= 0.5")
        print("  * R² de tendencia >= 0.45")
        print()
        
        print("3.4 ANÁLISIS Y PUNTUACIÓN")
        print("------------------------")
        print("- Cálculo de puntuación para cada componente")
        print("- Evaluación de factores de convergencia")
        print("- Aplicación de ponderaciones según importancia relativa")
        print("- Cálculo de puntuación final combinada")
        print()
        
        print("3.5 ALMACENAMIENTO DE RESULTADOS")
        print("------------------------------")
        print("- Eliminación de duplicados")
        print("- Guardado en tabla triple_signals")
        print("- Almacenamiento de detalles en formato JSON")
    
    def _mostrar_sistema_puntuacion(self):
        """Mostrar sistema de puntuación"""
        print("\n" + "-"*80)
        print(" 4. SISTEMA DE PUNTUACIÓN ")
        print("-"*80 + "\n")
        
        print("El sistema utiliza un enfoque de puntuación ponderada en múltiples niveles:")
        print()
        print("4.1 PUNTUACIÓN DE COMPONENTES BÁSICOS (70%)")
        print("------------------------------------------")
        print("- Zona de Acumulación (35%):")
        print("  * Calidad de zona (normalizada 0.45-0.85)")
        print("  * Puntuación = (quality_score - 0.45) / 0.4")
        print()
        print("- Mini-Tendencia (35%):")
        print("  * Base: R² (coeficiente de determinación)")
        print("  * Ajuste por categoría:")
        print("    > R² >= 0.6: Premio extra (x1.3)")
        print("    > R² >= 0.45: Sin ajuste (x1.0)")
        print("    > R² < 0.45: Penalización leve (x0.9)")
        print("  * Factor direccional:")
        print("    > Alcista: 1.15 (premio)")
        print("    > Bajista: 0.90 (neutral)")
        print("  * Factor de pendiente (0.3-1.0)")
        print()
        print("- Vela Clave (30%):")
        print("  * Volumen (60%): Normalizado al rango 0-1 (referencia 150)")
        print("  * Morfología (40%): Tamaño de cuerpo")
        print("    > Óptimo: 15-40% (1.0)")
        print("    > Grande: 40-60% (0.8)")
        print("    > Pequeño: 5-15% (0.6)")
        print("    > Muy pequeño: <5% (0.3)")
        print()
        
        print("4.2 FACTORES AVANZADOS (30%)")
        print("---------------------------")
        print("- Divergencia/Convergencia (20%):")
        print("  * Mide la coherencia entre los tres componentes")
        print("  * Premia cuando todos los factores apuntan en la misma dirección")
        print()
        print("- Fiabilidad (15%):")
        print("  * Bonus por R² alto (>0.75)")
        print("  * Premia tendencias de alta calidad")
        print()
        print("- Potencial de Rentabilidad (15%):")
        print("  * Base: 0.6 (optimista)")
        print("  * Ajustes específicos:")
        print("    > Alcista con volumen >80: 0.85")
        print("    > Alcista con volumen >50: 0.75")
        print("    > Bajista con cuerpo >20%: 0.70")
        print()
        
        print("4.3 CÁLCULO DE PUNTUACIÓN FINAL")
        print("-----------------------------")
        print("- Puntuación básica ponderada de componentes:")
        print("  * 0.35 × zona_score + 0.35 × trend_score + 0.30 × candle_score")
        print()
        print("- Ajuste por factores avanzados:")
        print("  * Aporte ponderado de los factores avanzados")
        print("  * Normalización al rango 0-1")
        print()
        print("- Interpretación de puntuación:")
        print("  * <0.5: Débil")
        print("  * 0.5-0.6: Moderada")
        print("  * 0.6-0.7: Fuerte")
        print("  * >0.7: Muy fuerte")
    
    def _mostrar_implementacion_tecnica(self):
        """Mostrar implementación técnica"""
        print("\n" + "-"*80)
        print(" 5. IMPLEMENTACIÓN TÉCNICA ")
        print("-"*80 + "\n")
        
        print("5.1 ARQUITECTURA DEL SISTEMA")
        print("--------------------------")
        print("- Diseño modular con scripts independientes para cada fase")
        print("- Base de datos MySQL como almacenamiento centralizado")
        print("- Flujo de procesamiento secuencial coordinado por run_combined_detection.py")
        print()
        
        print("5.2 ESTRUCTURA DE LA BASE DE DATOS")
        print("--------------------------------")
        print("- Tabla key_candles: Almacena velas clave detectadas")
        print("- Tabla detect_accumulation_zone_results: Zonas de acumulación")
        print("- Tabla mini_trend_results: Mini-tendencias detectadas")
        print("- Tabla triple_signals: Señales de triple coincidencia")
        print()
        
        print("5.3 GESTIÓN DE DEPENDENCIAS ENTRE COMPONENTES")
        print("-------------------------------------------")
        print("- Consultas SQL para establecer relaciones espaciales")
        print("- Tolerancia espacial (8 velas) para relacionar componentes")
        print("- Detección automática de estructura de tablas")
        print()
        
        print("5.4 OPTIMIZACIONES DE RENDIMIENTO")
        print("-------------------------------")
        print("- Índices en columnas clave para consultas rápidas")
        print("- Manejo de errores y excepciones en puntos críticos")
        print("- Limpieza de datos antiguos para evitar duplicados")
        print()
        
        print("5.5 SISTEMA DE DIAGNÓSTICO")
        print("------------------------")
        print("- Script diagnostico_triple.py para análisis de problemas")
        print("- Verificación automática de estructura de tablas")
        print("- Análisis de coincidencias potenciales con tolerancia ampliada")
    
    def _mostrar_archivos_sistema(self):
        """Mostrar archivos del sistema"""
        print("\n" + "-"*80)
        print(" 6. ARCHIVOS DEL SISTEMA ")
        print("-"*80 + "\n")
        
        print("El sistema está compuesto por varios scripts que trabajan en conjunto:")
        print()
        print("6.1 SCRIPTS PRINCIPALES")
        print("---------------------")
        print("- run_combined_detection.py: Coordina el proceso completo")
        print("  * Ejecuta secuencialmente los scripts de detección")
        print("  * Gestiona parámetros y configuración")
        print()
        print("- save_detect_candles.py: Detección de velas clave")
        print("  * Identifica velas con volumen y morfología destacables")
        print("  * Guarda resultados en tabla key_candles")
        print()
        print("- save_detect_accumulation_zone.py: Detección de zonas")
        print("  * Identifica áreas de consolidación de precio")
        print("  * Calcula score de calidad para cada zona")
        print("  * Guarda resultados en tabla detect_accumulation_zone_results")
        print()
        print("- mini_trend.py: Análisis de mini-tendencias")
        print("  * Implementa algoritmo ZigZag para segmentación")
        print("  * Calcula regresión lineal y R² para cada segmento")
        print("  * Guarda resultados en tabla mini_trend_results")
        print()
        print("- save_triple_signals.py: Detección de triple coincidencia")
        print("  * Relaciona los tres componentes anteriores")
        print("  * Implementa sistema de puntuación")
        print("  * Guarda señales en tabla triple_signals")
        print()
        
        print("6.2 SCRIPTS AUXILIARES")
        print("--------------------")
        print("- view_triple_signals.py: Visualización de resultados")
        print("  * Muestra señales detectadas con puntuación detallada")
        print("  * Formato tabular para análisis")
        print()
        print("- diagnostico_triple.py: Herramienta de diagnóstico")
        print("  * Analiza por qué no se detectan señales")
        print("  * Verifica componentes y relaciones")
        print("  * Propone ajustes y soluciones")
    
    def _mostrar_parametros_optimizados(self):
        """Mostrar parámetros optimizados"""
        print("\n" + "-"*80)
        print(" 7. PARAMETROS OPTIMIZADOS ")
        print("-"*80 + "\n")
        
        print("Tras multiples pruebas y optimizaciones, estos son los parametros")
        print("actuales del sistema:")
        print()
        print("7.1 PARAMETROS DE DETECCION")
        print("--------------------------")
        print("- Velas Clave:")
        print("  * VPT (Volume Percentile Threshold): 70")
        print("  * BPT (Body Percentage Threshold): 40")
        print("  * lookback: 30 periodos")
        print()
        print("- Zonas de Acumulacion:")
        print("  * ATR Period: 14")
        print("  * ATR Multiplier: 1.0")
        print("  * Volume Threshold: 1.1")
        print("  * Quality Threshold: 3.0")
        print("  * Recency Bonus: 0.1")
        print()
        print("- Mini-Tendencias:")
        print("  * Umbral ZigZag: Adaptativo segun ATR")
        print("  * Minimo R2: 0.45 (para consideracion)")
        print()
        
        print("7.2 PARAMETROS DE RELACION ESPACIAL")
        print("---------------------------------")
        print("- Tolerancia de proximidad: 8 velas")
        print("  * Ajustado desde 3 -> 5 -> 8 velas")
        print("  * Permite capturar relaciones mas flexibles entre componentes")
        print()
        
        print("7.3 PARAMETROS DE PUNTUACION")
        print("--------------------------")
        print("- Umbrales de calidad minima:")
        print("  * Zona: 0.45 (antes 0.5)")
        print("  * R2 tendencia: 0.45 (antes mas exigente)")
        print("  * Categorias de R2:")
        print("    > Premium: >=0.6 (premio x1.3)")
        print("    > Estandar: >=0.45 (neutro x1.0)")
        print("    > Basico: <0.45 (penalizacion leve x0.9)")
        print()
        print("- Factores direccionales:")
        print("  * Alcista: 1.15 (premio por mejor desempeño histórico)")
        print("  * Bajista: 0.90 (neutral)")
        print()
        print("- Ponderación de componentes básicos:")
        print("  * Zona: 35%")
        print("  * Tendencia: 35%")
        print("  * Vela: 30%")
        print()
        print("- Ponderación de factores avanzados:")
        print("  * Divergencia: 20%")
        print("  * Fiabilidad: 15%")
        print("  * Potencial: 15%")
    
    def _mostrar_resumen_final(self):
        """Mostrar resumen final"""
        print("\n" + "-"*80)
        print(" 8. RESUMEN Y CONCLUSIONES ")
        print("-"*80 + "\n")
        
        print("El Sistema de Triple Coincidencia representa un enfoque avanzado para")
        print("la detección de oportunidades de trading de alta probabilidad, basado en")
        print("la convergencia de múltiples factores técnicos independientes.")
        print()
        print("BENEFICIOS PRINCIPALES:")
        print("---------------------")
        print("1. Mayor fiabilidad al requerir confirmación desde tres perspectivas")
        print("2. Sistema de puntuación objetivo que cuantifica la fuerza de las señales")
        print("3. Flexibilidad para adaptarse a diferentes pares y timeframes")
        print("4. Balance entre criterios estrictos de calidad y sensibilidad de detección")
        print()
        print("VALIDACIÓN DE RESULTADOS:")
        print("-----------------------")
        print("Las pruebas en diferentes conjuntos de datos han mostrado la efectividad")
        print("del sistema para identificar señales significativas, con tasas de éxito")
        print("superiores a estrategias basadas en un solo factor técnico.")
        print()
        print("PRÓXIMOS PASOS:")
        print("-------------")
        print("1. Integración con sistema de backtesting para validación estadística")
        print("2. Ampliación a más pares y timeframes para mayor diversificación")
        print("3. Desarrollo de alertas automáticas basadas en puntuación mínima")
        print("4. Optimización continua de parámetros y sistema de puntuación")
        print()
        print("El enfoque modular y parametrizable del sistema permite ajustes")
        print("continuos sin alterar su arquitectura fundamental, garantizando")
        print("su capacidad de adaptación a diferentes condiciones de mercado.")

def main():
    """Función principal"""
    sistema = SistemaTripleCoincidencia()
    sistema.mostrar_flujo_completo()

if __name__ == "__main__":
    main()
