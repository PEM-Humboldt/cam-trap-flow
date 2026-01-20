# -*- coding: utf-8 -*-
"""
WI2CamtrapDP - Validación
==========================

Funciones para validar Data Packages con Frictionless Framework.

Proporciona validación automática de archivos datapackage.json y sus
recursos asociados (CSVs) según el estándar Camtrap-DP v1.0.2.

Módulo: validator.py
Autor: Cristian C. Acevedo
Organización: Instituto Humboldt - Red OTUS
Última actualización: 23 de diciembre de 2025
"""

from typing import Tuple, Any


def validate_datapackage(datapackage_path: str) -> Tuple[bool, Any]:
    """
    Valida un Data Package Camtrap-DP con Frictionless Framework.
    
    Verifica la conformidad del datapackage.json y sus recursos (CSVs)
    con el estándar Camtrap-DP, incluyendo:
        - Estructura del datapackage.json
        - Esquemas de tablas (deployments, media, observations)
        - Tipos de datos y valores de campos
        - Restricciones y reglas de validación
        - Integridad referencial entre tablas
    
    Args:
        datapackage_path: Ruta al archivo datapackage.json a validar
    
    Returns:
        Tuple[bool, Any]: Tupla con:
            - bool: True si el datapackage es válido, False en caso contrario
            - Any: Objeto Report de Frictionless con detalles de validación,
                   o string con mensaje de error si Frictionless no está disponible
    
    Example:
        >>> valid, report = validate_datapackage("output/datapackage.json")
        >>> if valid:
        ...     print("✓ Datapackage válido")
        ... else:
        ...     print(f"✗ Errores: {report}")
        
    Note:
        - Requiere Frictionless Framework: pip install frictionless
        - Si Frictionless no está instalado, retorna (False, error_msg)
          sin interrumpir el flujo de procesamiento
        - La validación puede tomar varios segundos para datasets grandes
        
    Raises:
        No lanza excepciones. Los errores se retornan como (False, error_msg).
    """
    try:
        from frictionless import validate
        report = validate(datapackage_path)
        return bool(report.valid), report
    except Exception as e:
        # Si Frictionless no está disponible o hay error, no bloquear
        return False, str(e)
