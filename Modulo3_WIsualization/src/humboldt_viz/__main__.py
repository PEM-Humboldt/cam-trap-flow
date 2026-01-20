"""
WIsualization - Punto de Entrada Principal como Módulo
=======================================================

Script de entrada para ejecutar WIsualization como módulo de Python.
Permite lanzar la aplicación mediante el comando: python -m humboldt_viz

Uso:
    python -m humboldt_viz
    
    o desde cualquier directorio después de instalar:
    pip install .
    python -m humboldt_viz

Este archivo actúa como puente entre el intérprete de Python y la función
principal de la interfaz gráfica, permitiendo la ejecución del paquete como
módulo ejecutable estándar de Python.

Módulo: __main__.py
Autores: Cristian C. Acevedo, Angélica Díaz-Pulido
Organización: Instituto Humboldt
Versión: 1.0.0
Última actualización: 24 de diciembre de 2025
"""

from humboldt_viz.ui_main import main

if __name__ == "__main__":
    main()
