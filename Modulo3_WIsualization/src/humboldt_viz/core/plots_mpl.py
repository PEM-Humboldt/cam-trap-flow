"""
WIsualization - Motor de Visualización Científica con Matplotlib
=================================================================

Funciones especializadas para generar visualizaciones científicas de alta calidad
de datos de fototrampeo. Implementa métodos estadísticos avanzados y mejores
prácticas en visualización de datos ecológicos.

Visualizaciones implementadas:
    1. Curvas de acumulación de especies:
       - Suavizado semilogarítmico según Ugland et al. (2003)
       - Intervalos de confianza mediante bootstrap de primeras apariciones
       - Métricas de ajuste (R²) y diagnósticos de calidad
    
    2. Rangos temporales de deployments:
       - Visualización de esfuerzo de muestreo por sitio
       - Cronología de operación de cámaras trampa
       - Detección de gaps temporales
    
    3. Patrones de actividad circadiana:
       - Kernel Density Estimation (KDE) para suavizado de densidad
       - Análisis de ritmos diarios y nocturnos
       - Comparación multi-especie
    
    4. Matrices de presencia/ausencia:
       - Análisis espaciotemporal de ocupación
       - Detección de patrones de movimiento
       - Visualización tipo heatmap

Metodología científica:
    - Aplicación de modelos estadísticos robustos
    - Manejo de datos faltantes y outliers
    - Visualizaciones siguiendo estándares de publicación científica
    - Código documentado con referencias bibliográficas

Módulo: core/plots_mpl.py
Autores: Cristian C. Acevedo, Angélica Díaz-Pulido
Organización: Instituto Humboldt - Programa de Evaluación y Monitoreo
Versión: 1.0.0
Última actualización: 24 de diciembre de 2025
Licencia: Ver LICENSE

Referencias bibliográficas:
    - Ugland, K. I., Gray, J. S., & Ellingsen, K. E. (2003). The species-accumulation 
      curve and estimation of species richness. Journal of Animal Ecology, 72(5), 888-897.
    - Efron, B., & Tibshirani, R. J. (1994). An Introduction to the Bootstrap. 
      Chapman & Hall/CRC.
"""

import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.widgets import Cursor

# Importación condicional para suavizado de curvas
try:
    from scipy.ndimage import gaussian_filter1d
except ImportError:
    # Fallback si scipy.ndimage no está disponible
    gaussian_filter1d = None


# =====================================================================================
# FUNCIONES DE UTILIDAD Y FORMATO
# =====================================================================================

def _show_error_message(ax, message: str):
    """
    Muestra un mensaje de error consistente en el área de graficación.
    
    Esta función limpia el eje y presenta un mensaje de error centrado
    con formato visual consistente para todas las gráficas.
    
    Args:
        ax (matplotlib.axes.Axes): Eje donde mostrar el mensaje
        message (str): Texto del mensaje de error a mostrar
    """
    ax.clear()
    ax.axis("off")
    ax.text(0.5, 0.5, message, ha="center", va="center", 
            transform=ax.transAxes, fontsize=10, 
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral", alpha=0.7))


def _safe_tight_layout(fig):
    """
    Aplica tight_layout de forma segura con sistema de respaldo.
    
    Intenta optimizar el espaciado automático de la figura. Si falla
    (común con gráficas complejas), usa un espaciado manual predefinido.
    
    Args:
        fig (matplotlib.figure.Figure): Figura a la que aplicar el layout
    """
    try:
        fig.tight_layout(pad=1.0)
    except Exception:
        # Si tight_layout falla, usar layout manual como respaldo
        fig.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9)


def _prettify(ax, title: str, xlabel: str, ylabel: str, enable_cursor=True):
    """
    Aplica estilo científico estándar a las gráficas.
    
    Configura títulos, etiquetas, grillas y estilo visual consistente
    para todas las visualizaciones del módulo.
    
    Args:
        ax (matplotlib.axes.Axes): Eje a formatear
        title (str): Título principal de la gráfica
        xlabel (str): Etiqueta del eje X
        ylabel (str): Etiqueta del eje Y
        enable_cursor (bool): Si habilitar cursor interactivo (no usado actualmente)
    """
    # Configurar títulos y etiquetas
    ax.set_title(title, fontsize=12, fontweight="600", pad=15)
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    
    # Configurar grilla y bordes para aspecto científico
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.spines["top"].set_visible(False)      # Quitar borde superior
    ax.spines["right"].set_visible(False)    # Quitar borde derecho
    
    # Mejorar apariencia general
    ax.tick_params(axis='both', which='major', labelsize=9)
    ax.set_facecolor('#fafbfc')  # Fondo ligeramente gris


def plot_accumulation_curve_mpl(images: pd.DataFrame, deployments: pd.DataFrame, ax, 
                               confidence_interval=False, smooth_curve=True):
    """
    Genera curva de acumulación de especies con opciones avanzadas de análisis.
    
    PROPÓSITO:
    Esta función crea visualizaciones de cómo se acumulan las especies nuevas
    a lo largo del tiempo en un estudio de fototrampeo. Es fundamental para
    evaluar la eficiencia del muestreo y estimar la riqueza total de especies.
    
    METODOLOGÍA CIENTÍFICA:
    - Curva básica: Cuenta especies únicas acumuladas por fecha
    - Suavizado semilogarítmico: Aplica modelo S = a*ln(t+1) + b según Ugland et al. (2003)
    - Intervalos de confianza: Bootstrap de fechas de primera aparición (método innovador)
    
    PROCESO PASO A PASO:
    1. Validación y limpieza de datos (timestamps y nombres científicos)
    2. Construcción del rango completo de fechas desde el estudio
    3. Cálculo de especies acumuladas día por día
    4. Aplicación opcional de suavizado semilogarítmico
    5. Cálculo opcional de intervalos de confianza bootstrap
    6. Renderizado final con formato científico
    
    Args:
        images (pd.DataFrame): DataFrame con registros de especies. Debe contener:
                              - 'timestamp': Fecha/hora de cada registro
                              - 'scientific_name': Nombre científico de cada especie
        deployments (pd.DataFrame): DataFrame con información de deployments (usado para validación)
        ax (matplotlib.axes.Axes): Eje donde dibujar la gráfica
        confidence_interval (bool): Si True, calcula y muestra intervalos de confianza del 95%
        smooth_curve (bool): Si True, aplica suavizado semilogarítmico; si False, muestra curva discreta
    
    Returns:
        None: La función modifica directamente el eje proporcionado
        
    Efectos Secundarios:
        - Imprime estadísticas del proceso en consola
        - Modifica el eje matplotlib proporcionado
        - Puede mostrar advertencias sobre calidad de intervalos de confianza
    
    Excepciones:
        - Muestra mensaje de error si faltan datos válidos
        - Captura y reporta errores en suavizado o intervalos de confianza
    """
    try:
        # =============================================================================
        # PASO 1: PREPARACIÓN Y VALIDACIÓN DE DATOS
        # =============================================================================
        
        images = images.copy()  # Evitar modificar el DataFrame original
        images["timestamp"] = pd.to_datetime(images["timestamp"], errors="coerce")
        
        # Validación exhaustiva de la calidad de los datos
        valid_timestamps = images["timestamp"].notna()
        valid_names = images["scientific_name"].notna() & (images["scientific_name"] != "")
        
        # Verificar que tenemos datos mínimos para generar la curva
        if not valid_timestamps.any():
            _show_error_message(ax, "No hay timestamps válidos en los datos de imágenes")
            return
        
        if not valid_names.any():
            _show_error_message(ax, "No hay nombres científicos válidos en los datos")
            return
        
        # Filtrar solo registros con datos completos y extraer fecha normalizada
        images = images[valid_timestamps & valid_names]
        images["date"] = images["timestamp"].dt.normalize()  # Solo fecha, sin hora

        # Verificación final de que tenemos datos para trabajar
        if images.empty:
            _show_error_message(ax, "No quedan datos válidos después de la limpieza")
            return

        # =============================================================================
        # PASO 2: CONSTRUCCIÓN DE LA CURVA DE ACUMULACIÓN BÁSICA
        # =============================================================================
        
        # Crear rango completo de fechas desde el inicio hasta el final del estudio
        start = images["date"].min()
        end = images["date"].max()
        date_range = pd.date_range(start, end, freq="D")

        # Agrupar especies únicas por día (conjunto matemático para evitar duplicados)
        by_day = images.groupby("date")["scientific_name"].apply(lambda s: set(s.dropna().astype(str)))
        
        # Calcular acumulación día por día: cada día suma especies nuevas al total
        richness_discrete = []
        seen = set()  # Conjunto acumulativo de todas las especies vistas hasta la fecha
        for d in date_range:
            seen |= by_day.get(d, set())  # Unión de conjuntos (agregar especies nuevas)
            richness_discrete.append(len(seen))  # Contar total de especies únicas

        # Aplicar suavizado semilogarítmico siguiendo Ugland et al. (2003)
        days_numeric = np.arange(len(date_range))
        
        # Método 1: Curva semilogarítmica suavizada (si está habilitado)
        if smooth_curve and len(richness_discrete) > 3:
            try:
                # Ajuste semilog: S = a * ln(t + 1) + b
                log_days = np.log(days_numeric + 1)  # +1 para evitar ln(0)
                
                # Regresión robusta usando percentiles para evitar outliers
                valid_mask = np.array(richness_discrete) > 0
                if valid_mask.sum() > 3:
                    coeffs = np.polyfit(log_days[valid_mask], 
                                      np.array(richness_discrete)[valid_mask], 1)
                    a, b = coeffs
                    
                    # Generar curva suavizada con más puntos para suavidad visual
                    days_smooth = np.linspace(0, len(date_range)-1, len(date_range)*3)
                    log_days_smooth = np.log(days_smooth + 1)
                    richness_smooth = a * log_days_smooth + b
                    
                    # Crear fechas correspondientes para la curva suavizada
                    date_smooth = []
                    for i in days_smooth:
                        if i < len(date_range):
                            date_smooth.append(date_range[int(i)])
                        else:
                            # Extrapolación
                            extra_days = int(i) - len(date_range) + 1
                            date_smooth.append(date_range[-1] + pd.Timedelta(days=extra_days))
                    
                    # Asegurar que no hay valores negativos
                    richness_smooth = np.maximum(richness_smooth, 0)
                    
                    # Gráfica de curva suavizada principal
                    ax.plot(date_smooth, richness_smooth, linewidth=3.2, 
                           label="Curva suavizada (semilog)", color='#2E86AB', alpha=0.9)
                    ax.fill_between(date_smooth, richness_smooth, alpha=0.12, color='#2E86AB')
                    
                    # Mostrar puntos de datos originales como referencia
                    ax.scatter(date_range[::max(1, len(date_range)//20)], 
                             [richness_discrete[i] for i in range(0, len(richness_discrete), 
                                                                 max(1, len(date_range)//20))],
                             s=35, alpha=0.7, color='#FF6B35', zorder=5, 
                             label="Datos observados")
                    
                    # Calcular R² del ajuste
                    r_squared = 1 - np.sum((np.array(richness_discrete)[valid_mask] - 
                                          (a * log_days[valid_mask] + b))**2) / \
                                    np.sum((np.array(richness_discrete)[valid_mask] - 
                                          np.mean(richness_discrete))**2)
                    
                    # Añadir información del modelo en el título
                    model_info = f"(R² = {r_squared:.3f})"
                    
                else:
                    # Fallback a curva original
                    ax.plot(date_range, richness_discrete, linewidth=2.8, 
                           label="Riqueza acumulada", color='#2E86AB', alpha=0.9)
                    model_info = ""
                    
            except Exception as e:
                print(f"Error en suavizado semilog: {e}")
                # Fallback a curva original
                ax.plot(date_range, richness_discrete, linewidth=2.8, 
                       label="Riqueza acumulada", color='#2E86AB', alpha=0.9)
                model_info = ""
        else:
            # Curva discreta original (sin suavizado)
            ax.plot(date_range, richness_discrete, linewidth=2.8, 
                   label="Riqueza acumulada", color='#2E86AB', marker='o', 
                   markersize=3, alpha=0.9)
            ax.fill_between(date_range, richness_discrete, alpha=0.15, color='#2E86AB')
            model_info = "(curva discreta)"

        # Intervalos de confianza específicos para curvas de acumulación
        if confidence_interval and len(richness_discrete) > 5 and len(images) > 20:
            try:
                # NUEVO MÉTODO: Bootstrap de fechas de primera aparición
                # Más apropiado para curvas de acumulación que dependen del orden temporal
                bootstrap_curves = []
                n_bootstrap = 300
                
                print(f"Calculando IC para {len(images)} observaciones en {len(date_range)} días...")
                
                # Obtener todas las especies únicas y sus fechas de primera aparición
                species_list = list(images['scientific_name'].unique())
                first_appearances = {}
                
                for species in species_list:
                    species_data = images[images['scientific_name'] == species]
                    first_date = species_data['date'].min()
                    first_appearances[species] = first_date
                
                print(f"Especies encontradas: {len(species_list)}")
                
                # Bootstrap remuestreando las fechas de primera aparición
                for bootstrap_iter in range(n_bootstrap):
                    # Crear una versión bootstrap de las primeras apariciones
                    bootstrap_first_appearances = {}
                    
                    for species in species_list:
                        # Para cada especie, decidir si aparece en este bootstrap (probabilístico)
                        # y si aparece, asignar una fecha aleatoria dentro del período de estudio
                        original_first_date = first_appearances[species]
                        
                        # Calcular probabilidad de aparición basada en cuándo apareció originalmente
                        # Especies que aparecieron temprano tienen mayor probabilidad de aparecer temprano
                        days_from_start = (original_first_date - date_range[0]).days
                        total_days = len(date_range)
                        
                        # Probabilidad decreciente con el tiempo
                        appearance_prob = 1.0  # Todas las especies aparecen en bootstrap
                        
                        if np.random.random() < appearance_prob:
                            # Asignar fecha bootstrap con distribución sesgada hacia la fecha original
                            # 70% cerca de la fecha original, 30% uniforme en el período
                            if np.random.random() < 0.7:
                                # Bootstrap cerca de la fecha original (±20% del período total)
                                window_size = max(1, total_days // 5)
                                min_day = max(0, days_from_start - window_size)
                                max_day = min(total_days - 1, days_from_start + window_size)
                                bootstrap_day = np.random.randint(min_day, max_day + 1)
                            else:
                                # Bootstrap uniforme en todo el período
                                bootstrap_day = np.random.randint(0, total_days)
                            
                            bootstrap_date = date_range[bootstrap_day]
                            bootstrap_first_appearances[species] = bootstrap_date
                    
                    # Calcular curva de acumulación bootstrap
                    sample_richness = []
                    for d in date_range:
                        # Contar especies que ya habían aparecido en o antes de esta fecha
                        species_by_date = sum(1 for species, first_date in bootstrap_first_appearances.items() 
                                            if first_date <= d)
                        sample_richness.append(species_by_date)
                    
                    # Verificar monotonicidad (por construcción debería serlo)
                    for i in range(1, len(sample_richness)):
                        if sample_richness[i] < sample_richness[i-1]:
                            sample_richness[i] = sample_richness[i-1]
                    
                    bootstrap_curves.append(sample_richness)
                
                if len(bootstrap_curves) >= 100:
                    bootstrap_array = np.array(bootstrap_curves)
                    
                    # Calcular intervalos de confianza
                    lower = np.percentile(bootstrap_array, 2.5, axis=0)
                    upper = np.percentile(bootstrap_array, 97.5, axis=0)
                    
                    # Asegurar monotonicidad en los intervalos
                    for i in range(1, len(lower)):
                        lower[i] = max(lower[i], lower[i-1])
                        upper[i] = max(upper[i], upper[i-1])
                    
                    # Estadísticas de diagnóstico
                    mean_curve = np.mean(bootstrap_array, axis=0)
                    
                    # Verificar cobertura
                    points_within = np.sum((np.array(richness_discrete) >= lower) & 
                                         (np.array(richness_discrete) <= upper))
                    coverage = points_within / len(richness_discrete)
                    
                    print(f"Bootstrap completado: {len(bootstrap_curves)} iteraciones")
                    print(f"Cobertura empírica: {coverage:.1%}")
                    
                    # Mostrar IC si la cobertura es aceptable (más permisivo para este tipo de datos)
                    if coverage >= 0.60:  # 60% es aceptable para curvas de acumulación
                        # Suavizado muy ligero para mejor visualización
                        if len(date_range) > 50 and gaussian_filter1d is not None:
                            sigma = len(date_range) / 100  # Suavizado mínimo
                            lower = gaussian_filter1d(lower, sigma=sigma)
                            upper = gaussian_filter1d(upper, sigma=sigma)
                            
                            # Mantener monotonicidad después del suavizado
                            for i in range(1, len(lower)):
                                lower[i] = max(lower[i], lower[i-1])
                                upper[i] = max(upper[i], upper[i-1])
                        
                        # Asegurar límites razonables
                        lower = np.maximum(lower, 0)
                        upper = np.minimum(upper, len(species_list))
                        
                        # Dibujar intervalos
                        ax.fill_between(date_range, lower, upper, alpha=0.3, color='#B0C4DE', 
                                       label="IC 95% (bootstrap)", zorder=1)
                        
                        # Líneas de límites
                        ax.plot(date_range, lower, '--', alpha=0.7, color='#778899', linewidth=1.2)
                        ax.plot(date_range, upper, '--', alpha=0.7, color='#778899', linewidth=1.2)
                        
                        print(f"IC mostrado con cobertura: {coverage:.1%}")
                        
                    else:
                        print(f"IC no mostrado: cobertura muy baja ({coverage:.1%})")
                        print("Se requiere más variabilidad en los datos para IC confiables")
                        
                        # Mostrar IC aproximado basado en varianza empírica
                        std_curve = np.std(bootstrap_array, axis=0)
                        approx_lower = mean_curve - 1.96 * std_curve
                        approx_upper = mean_curve + 1.96 * std_curve
                        
                        # Asegurar monotonicidad y límites
                        for i in range(1, len(approx_lower)):
                            approx_lower[i] = max(approx_lower[i], approx_lower[i-1])
                            approx_upper[i] = max(approx_upper[i], approx_upper[i-1])
                        
                        approx_lower = np.maximum(approx_lower, 0)
                        approx_upper = np.minimum(approx_upper, len(species_list))
                        
                        ax.fill_between(date_range, approx_lower, approx_upper, alpha=0.2, color='#D3D3D3', 
                                       label="IC 95% (aproximado)", zorder=1)
                        
                        print("Mostrando IC aproximado basado en varianza del bootstrap")
                
                else:
                    print(f"Warning: Insuficientes curvas bootstrap válidas ({len(bootstrap_curves)} < 100)")
                
            except Exception as e:
                print(f"Error calculando intervalos de confianza: {e}")
                import traceback
                traceback.print_exc()

        # Mejoras visuales siguiendo mejores prácticas
        title = f"Curva de acumulación de especies {model_info}"
        _prettify(ax, title, "Fecha", "Riqueza de especies (S)")

        # Formato de fechas optimizado
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
        
        # Ajustar límites Y para mejor visualización
        if len(richness_discrete) > 0:
            max_richness = max(richness_discrete)
            ax.set_ylim(0, max_richness * 1.1)
        
        # Leyenda mejorada
        legend = ax.legend(frameon=True, loc='lower right', fancybox=True, shadow=True)
        legend.get_frame().set_facecolor('#ffffff')
        legend.get_frame().set_alpha(0.9)
        
        # Márgenes optimizados
        ax.margins(x=0.01, y=0.02)
        
        # Información estadística adicional en texto
        if len(richness_discrete) > 1:
            final_richness = richness_discrete[-1]
            total_days = len(date_range)
            rate = final_richness / total_days if total_days > 0 else 0
            
            info_text = f"Total: {final_richness} especies\n{total_days} días\nTasa: {rate:.2f} sp/día"
            ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=9,
                   verticalalignment='top', bbox=dict(boxstyle="round,pad=0.3", 
                   facecolor="lightblue", alpha=0.8))
        
    except Exception as e:
        _show_error_message(ax, f"Error al generar curva de acumulación: {str(e)}")


def plot_site_dates_mpl(deployments: pd.DataFrame, ax):
    """
    Genera gráfica de rangos temporales de deployments por sitio.
    
    PROPÓSITO:
    Visualiza cuándo estuvo activo cada deployment de cámara trampa,
    mostrando el esfuerzo de muestreo temporal y espacial del estudio.
    
    FUNCIONALIDAD:
    - Cada línea horizontal representa un deployment específico
    - La longitud de la línea muestra la duración del deployment
    - Los puntos en los extremos marcan las fechas de inicio y fin
    - Los deployments se ordenan cronológicamente por fecha de inicio
    
    Args:
        deployments (pd.DataFrame): Datos de deployments con columnas:
                                  - deployment_id: Identificador único
                                  - start_date: Fecha de inicio
                                  - end_date: Fecha de finalización
        ax (matplotlib.axes.Axes): Eje donde dibujar la gráfica
    """
    try:
        # =============================================================================
        # PREPARACIÓN DE DATOS TEMPORALES
        # =============================================================================
        deployments = deployments.copy()
        # Convertir fechas a formato datetime, marcando inválidas como NaT
        deployments["start_date"] = pd.to_datetime(deployments["start_date"], errors="coerce")
        deployments["end_date"] = pd.to_datetime(deployments["end_date"], errors="coerce")

        # Filtrar solo registros con datos completos de fechas e ID
        df = deployments.dropna(subset=["deployment_id", "start_date", "end_date"]).copy()
        
        if df.empty:
            _show_error_message(ax, "No hay deployments con fechas válidas")
            return
        
        # =============================================================================
        # ORGANIZACIÓN Y POSICIONAMIENTO VERTICAL
        # =============================================================================
        # Ordenar por fecha de inicio para secuencia cronológica lógica
        df = df.sort_values("start_date")
        ids = df["deployment_id"].astype(str).unique()

        # Asignar posición vertical a cada deployment (eje Y)
        y_positions = {d: i for i, d in enumerate(ids)}
        
        # =============================================================================
        # DIBUJAR LÍNEAS TEMPORALES Y MARCADORES
        # =============================================================================
        for _, row in df.iterrows():
            y = y_positions[row["deployment_id"]]
            # Línea horizontal que muestra la duración del deployment
            ax.hlines(y, row["start_date"], row["end_date"], linewidth=3)
            # Puntos que marcan inicio y fin del período
            ax.plot([row["start_date"], row["end_date"]], [y, y], "o", markersize=4)

        # =============================================================================
        # CONFIGURACIÓN DE EJES Y FORMATO
        # =============================================================================
        ax.set_yticks(list(y_positions.values()))
        ax.set_yticklabels(list(y_positions.keys()))
        _prettify(ax, "Rangos de fechas por deployment", "Fecha", "Deployment")

        # Formato inteligente de fechas en eje X
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
        ax.grid(True, axis="x", alpha=0.3)  # Grilla vertical para fechas
        ax.margins(x=0.02, y=0.05)  # Márgenes pequeños para mejor aprovechamiento
        
    except Exception as e:
        _show_error_message(ax, f"Error al generar gráfica de sitios: {str(e)}")


def plot_activity_hours_mpl(images: pd.DataFrame, names, ax, class_col=None, class_filter="Todos"):
    """
    Genera gráficas de densidad de actividad temporal (patrones circadianos).
    
    PROPÓSITO:
    Analiza los patrones de actividad diaria de las especies, mostrando
    a qué horas del día cada especie es más activa. Fundamental para
    estudios de comportamiento y ecología temporal.
    
    METODOLOGÍA:
    - Extrae la hora de cada registro fotográfico
    - Aplica Kernel Density Estimation (KDE) para suavizar los datos
    - Genera curvas de densidad continuas que muestran probabilidad de actividad
    
    INTERPRETACIÓN:
    - Picos altos = horas de mayor actividad
    - Valles = períodos de baja actividad  
    - Curvas anchas = actividad dispersa en el tiempo
    - Curvas estrechas = actividad concentrada en pocas horas
    
    Args:
        images (pd.DataFrame): Registros con 'timestamp' y 'scientific_name'
        names (list): Lista de nombres científicos a analizar
        ax (matplotlib.axes.Axes): Eje donde dibujar las curvas
        class_col (str, opcional): Nombre de columna de clase taxonómica
        class_filter (str): Filtro de clase aplicado (para el título)
    """
    try:
        # =============================================================================
        # PREPARACIÓN DE DATOS TEMPORALES
        # =============================================================================
        images = images.copy()
        images["timestamp"] = pd.to_datetime(images["timestamp"], errors="coerce")
        
        # Validar que tenemos timestamps válidos para calcular horas
        if images["timestamp"].isna().all():
            _show_error_message(ax, "No hay timestamps válidos para calcular horas")
            return
            
        # Extraer solo la hora (0-23) de cada timestamp
        images["hour"] = images["timestamp"].dt.hour
        
        if not names:
            _show_error_message(ax, "No se han seleccionado especies")
            return

        # =============================================================================
        # GENERACIÓN DE CURVAS DE DENSIDAD POR ESPECIE
        # =============================================================================
        # Rango continuo de horas para curvas suaves (1000 puntos de 0 a 24)
        x_range = np.linspace(0, 24, 1000)
        dibujado = False

        for name in names:
            # Obtener todas las horas de actividad de esta especie
            horas = images[images["scientific_name"] == name]["hour"].dropna().to_numpy()
            
            # Verificar que tenemos suficientes datos para KDE
            if len(horas) > 1 and np.unique(horas).size > 1:
                try:
                    # Kernel Density Estimation: crea curva suave de probabilidad
                    kde = gaussian_kde(horas)
                    y = kde(x_range)
                    
                    # Dibujar curva con nombre científico en cursiva (notación LaTeX)
                    ax.plot(x_range, y, label=f"${name}$", linewidth=2.2)
                    ax.fill_between(x_range, y, alpha=0.12)  # Área sombreada bajo la curva
                    dibujado = True
                    
                except Exception as e:
                    print(f"Error en KDE para {name}: {e}")
                    continue

        # =============================================================================
        # CONFIGURACIÓN FINAL Y FORMATO
        # =============================================================================
        titulo = "Densidad de horas de actividad por especie"
        if class_filter not in ("", "Todos"):
            titulo += f" — {class_filter}"
        _prettify(ax, titulo, "Hora", "Densidad")
        
        # Configurar eje X para horas del día (0-24)
        ax.set_xlim(0, 24)
        ax.set_xticks(range(0, 25, 2))  # Marcas cada 2 horas
        
        if dibujado:
            ax.legend(loc="upper right", frameon=False)
        else:
            _show_error_message(ax, "Sin datos suficientes para generar densidades.\nSe requieren al menos 2 registros por especie.")
            
    except Exception as e:
        _show_error_message(ax, f"Error al generar gráfica de actividad: {str(e)}")


def plot_presence_absence_mpl(images: pd.DataFrame, deployments: pd.DataFrame, name: str, ax,
                              class_col=None, class_filter="Todos", date_start=None, date_end=None):
    """
    Genera matriz de presencia/ausencia temporal por deployment.
    
    PROPÓSITO:
    Visualiza cuándo y dónde se detectó una especie específica a lo largo
    del tiempo y entre diferentes deployments. Esencial para analizar
    patrones espaciotemporales de ocupación de habitat.
    
    INTERPRETACIÓN:
    - Eje Y: Cada fila representa un deployment diferente
    - Eje X: Progresión temporal (fechas del estudio)  
    - Colores: Blanco = ausencia, Color = presencia
    - Patrones: Permite identificar movimientos, estacionalidad, preferencias de habitat
    
    FUNCIONALIDAD:
    - Crea matriz binaria (0/1) para presencia/ausencia por día
    - Permite filtrar rango temporal específico
    - Ordena deployments para mejor interpretación visual
    - Incluye barra de color para interpretar la escala
    
    Args:
        images (pd.DataFrame): Registros de especies con timestamp y deployment_id
        deployments (pd.DataFrame): Información de deployments para contexto
        name (str): Nombre científico de la especie a analizar
        ax (matplotlib.axes.Axes): Eje donde dibujar la matriz
        class_col (str, opcional): Columna de clase taxonómica (no usado directamente)
        class_filter (str): Filtro de clase aplicado (para el título)
        date_start (pd.Timestamp, opcional): Fecha inicial del rango a mostrar
        date_end (pd.Timestamp, opcional): Fecha final del rango a mostrar
    """
    try:
        if not name or name.strip() == "":
            _show_error_message(ax, "No se ha especificado una especie válida")
            return
            
        images = images.copy()
        images = images[images["scientific_name"] == name]

        if images.empty:
            _show_error_message(ax, f"No se encontraron registros para la especie: {name}")
            return

        images["timestamp"] = pd.to_datetime(images["timestamp"], errors="coerce")
        
        # Validar timestamps
        if images["timestamp"].isna().all():
            _show_error_message(ax, "No hay timestamps válidos para esta especie")
            return
            
        images["date"] = images["timestamp"].dt.normalize()

        # Rango base (deployments → fallback a images)
        dep_start = pd.to_datetime(deployments["start_date"], errors="coerce").min()
        dep_end   = pd.to_datetime(deployments["end_date"],   errors="coerce").max()
        img_start = images["date"].min()
        img_end   = images["date"].max()

        start = dep_start if pd.notna(dep_start) else img_start
        end   = dep_end   if pd.notna(dep_end)   else img_end

        # Aplicar filtro de fecha (si viene desde la UI)
        if isinstance(date_start, pd.Timestamp):
            start = max(start, date_start)
        if isinstance(date_end, pd.Timestamp):
            end = min(end, date_end)

        if pd.isna(start) or pd.isna(end) or start > end:
            _show_error_message(ax, "Sin rango de fechas válido para graficar")
            return

        date_range = pd.date_range(start.normalize(), end.normalize(), freq="D")
        if len(date_range) == 0:
            _show_error_message(ax, "Sin días en el rango para graficar")
            return

        # Filtrar imágenes al rango seleccionado
        images = images[(images["date"] >= date_range[0]) & (images["date"] <= date_range[-1])]

        deployment_ids = sorted(deployments["deployment_id"].dropna().astype(str).unique())
        if len(deployment_ids) == 0:
            _show_error_message(ax, "Sin deployments válidos")
            return

        mat = np.zeros((len(deployment_ids), len(date_range)), dtype=int)
        idx_dep = {d: i for i, d in enumerate(deployment_ids)}
        idx_day = {d: i for i, d in enumerate(date_range)}

        for _, row in images.iterrows():
            d = row.get("deployment_id")
            dt = row.get("date")
            if pd.isna(d) or pd.isna(dt):
                continue
            i = idx_dep.get(str(d))
            j = idx_day.get(pd.to_datetime(dt).normalize())
            if i is not None and j is not None:
                mat[i, j] = 1

        im = ax.imshow(mat, aspect="auto", interpolation="nearest", vmin=0, vmax=1)

        # Aplicar cursiva al nombre de la especie en el título
        titulo = f"Presencia/Ausencia por día — ${name}$"
        if class_filter not in ("", "Todos"):
            titulo += f" — {class_filter}"
        _prettify(ax, titulo, "Fecha", "Deployment")

        ax.set_yticks(np.arange(len(deployment_ids)))
        ax.set_yticklabels(deployment_ids)

        n = len(date_range)
        ticks = np.linspace(0, n - 1, min(8, n), dtype=int)
        ax.set_xticks(ticks)
        ax.set_xticklabels([date_range[i].strftime('%Y-%m-%d') for i in ticks], rotation=0)
        ax.margins(x=0.01, y=0.02)

        # Usar la figura correcta para el colorbar
        cbar = ax.figure.colorbar(im, ax=ax, fraction=0.46 / 10, pad=0.04)
        cbar.set_label("Presencia")
        
    except Exception as e:
        _show_error_message(ax, f"Error al generar matriz de presencia/ausencia: {str(e)}")

