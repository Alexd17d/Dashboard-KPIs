import os
import matplotlib.pyplot as plt
import seaborn as sns


# 1. DIRECCIONAMIENTO INTELIGENTE Y CONFIGURACIÓN DE RUTAS

# Detecta la ubicación exacta de este archivo .py para evitar errores de ruta
DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))

# Crear la carpeta 'data' para guardar los gráficos junto al script
CARPETA_SALIDA = os.path.join(DIRECTORIO_ACTUAL, "data")
if not os.path.exists(CARPETA_SALIDA):
    os.makedirs(CARPETA_SALIDA)

# Búsqueda automática del archivo transaccional 'vehiculos.txt'
# Intenta buscarlo tanto en la estructura local como en la carpeta compartida TPS
rutas_probables = [
    os.path.join(DIRECTORIO_ACTUAL, "TPS", "data", "vehiculos.txt"),
    os.path.join(DIRECTORIO_ACTUAL, "..", "TPS", "data", "vehiculos.txt"),
    os.path.join(DIRECTORIO_ACTUAL, "data", "vehiculos.txt"),
    "vehiculos.txt"
]

ruta_archivo = None
for ruta in rutas_probables:
    if os.path.exists(ruta):
        ruta_archivo = ruta
        break

if ruta_archivo is None:
    raise FileNotFoundError(
        " [ERROR CRÍTICO] No se encontró el archivo 'vehiculos.txt'.\n"
        "Por favor, asegúrate de que la carpeta 'TPS' o el archivo estén en el mismo directorio que este script."
    )

print(f"Base de datos detectada con éxito en: {ruta_archivo}")
print("Leyendo base de datos transaccional del TPS...")


# 2. INICIALIZACIÓN DE VARIABLES PARA LOS 8 KPIs

total_vehiculos = 0
sin_revision = 0
aprobado_2da = 0
aprobado_3ra = 0

conteo_livianos = 0
conteo_pesados = 0
conteo_motos = 0

recaudacion_real = 0.0
recaudacion_proyectada_total = 0.0

# Variables para el KPI 5 (Riesgo Mecánico)
reinspecciones_autos_viejos = 0  
reinspecciones_autos_nuevos = 0  

# Estructuras dinámicas para almacenar conteos y cálculos de soporte
antiguedad_por_tipo = {"pesado": 0.0, "liviano": 0.0, "moto": 0.0}
conteos_por_tipo = {"pesado": 0, "liviano": 0, "moto": 0}
avaluo_total_por_tipo = {"pesado": 0.0, "liviano": 0.0, "moto": 0.0}
matriculados_por_tipo = {"pesado": 0, "liviano": 0, "moto": 0}

# KPI 8: Control de carga por último dígito de placa
saturacion_placa = {i: 0 for i in range(10)}


# 3. EXTRACCIÓN Y PROCESAMIENTO DE DATOS (ETL)

with open(ruta_archivo, "r", encoding="utf-8") as archivo:
    for linea in archivo:
        linea = linea.strip()
        if not linea or len(linea.split(",")) < 9:
            continue
            
        datos = linea.split(",")
        try:
            placa = datos[1]
            anio = int(datos[3])
            tipo = datos[4]
            r1 = int(datos[6])
            r2 = int(datos[7])
            r3 = int(datos[8])
        except ValueError:
            continue

        total_vehiculos += 1
        es_matriculado = (r1 == 1 or r2 == 1 or r3 == 1)
        antiguedad_anios = 2026 - anio
        
        # LÓGICA DE REVISIONES (KPI 1 y KPI 2) 
        if not es_matriculado:
            sin_revision += 1
        elif r2 == 1:
            aprobado_2da += 1
        elif r3 == 1:
            aprobado_3ra += 1

        # LÓGICA DE CLASIFICACIÓN (KPI 3 y KPI 6) 
        if tipo == "liviano":
            conteo_livianos += 1
        elif tipo == "pesado":
            conteo_pesados += 1
        elif tipo == "moto":
            conteo_motos += 1

        if tipo in conteos_por_tipo:
            conteos_por_tipo[tipo] += 1
            antiguedad_por_tipo[tipo] += antiguedad_anios
            
        # LÓGICA FINANCIERA (KPI 4 y KPI 7) 
        tasa_base = 200.0 if tipo == "pesado" else 25.0
        valor_matricula = tasa_base + (antiguedad_anios * 5.0) + (0.0 if es_matriculado else 50.0)
        recaudacion_proyectada_total += valor_matricula
        
        if es_matriculado:
            recaudacion_real += valor_matricula
            matriculados_por_tipo[tipo] += 1
            avaluo_total_por_tipo[tipo] += valor_matricula

        # CRUCE DE RIESGO MECÁNICO (KPI 5) 
        if r2 == 1 or r3 == 1:
            if antiguedad_anios > 15:
                reinspecciones_autos_viejos += 1
            else:
                reinspecciones_autos_nuevos += 1

        # LÓGICA DE CALENDARIO DE PLACAS (KPI 8) 
        try:
            ultimo_digito = int(placa[-1])
            saturacion_placa[ultimo_digito] += 1
        except ValueError:
            continue

# Cálculos globales de salida
matriculados_totales = aprobado_2da + aprobado_3ra
tasa_churn = (sin_revision / total_vehiculos) * 100 if total_vehiculos > 0 else 0
fuga_dinero = max(0.0, recaudacion_proyectada_total - recaudacion_real)
total_reinspecciones = aprobado_2da + aprobado_3ra
tipos_lista = list(antiguedad_por_tipo.keys())


# 4. IMPRESIÓN DEL DASHBOARD 

print("="*75)
print("   MIS DASHBOARD - RESUMEN DE SALUD DEL NEGOCIO  ")
print("="*75)
print(f"  REGISTROS TOTALES     :  {total_vehiculos:,} vehículos procesados")
print(f"  CLIENTES QUE SE VAN   :  {tasa_churn:.2f}% de abandono comercial")
print("-"*75)
print(f"   ÁREA              INDICADOR CRÍTICO                   VALOR")
print("  ───────────────────────────────────────────────────────────────────────────")
print(f"    DINERO REAL      Dinero que ya entró al banco       ${recaudacion_real:,.2f}")
print(f"    DINERO PERDIDO   Cuentas que no se cobraron         ${fuga_dinero:,.2f}")
print(f"    TRABAJO DOBLE    Citas repetidas por fallas         {total_reinspecciones:,} revisiones")
print(f"    EQUIPOS MOTOS    Cantidad total de motos revisadas  {conteo_motos:,} unidades")
print("  ───────────────────────────────────────────────────────────────────────────")
print("="*75)
print("Exportando catálogo visual...\n")


# 5. MOTOR GRÁFICO PREMIUM ESTILIZADO (MÁXIMA ELEGANCIA)

HEX_BG = '#121316'         
HEX_CARD = '#1a1b20'       
HEX_TEXT = '#ffffff'       
HEX_MUTED = '#8a8f98'      

PALETA_MUTED = sns.color_palette("muted")
PALETA_CYAN_PURP = sns.color_palette("cool", 3) 
COLOR_MINT = '#00b894'     
COLOR_CORAL = '#ff5e62'    

plt.style.use('dark_background')

def estilizar_tarjeta_ui(ax, titulo_kpi, subtitulo):
    """Limpia los marcos e implementa cabeceras estilo software web moderno"""
    ax.set_facecolor(HEX_CARD)
    fig = ax.get_figure()
    fig.patch.set_facecolor(HEX_BG)
    ax.text(0.02, 1.16, titulo_kpi, transform=ax.transAxes, fontsize=12, fontweight='bold', color=HEX_TEXT)
    ax.text(0.02, 1.08, subtitulo, transform=ax.transAxes, fontsize=8, color=HEX_MUTED)
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_visible(False)
    ax.tick_params(colors=HEX_MUTED, labelsize=9, length=0)
    ax.yaxis.grid(True, linestyle='--', alpha=0.06, color=HEX_TEXT)
    ax.set_axisbelow(True)
    ax.margins(y=0.15)



# KPI 1: Control de Matriculación Anual
fig, ax = plt.subplots(figsize=(6, 3.8))
plt.subplots_adjust(top=0.78)
barras = ax.bar(['Clientes Activos', 'Inactivos (Churn)'], [matriculados_totales, sin_revision], color=[COLOR_MINT, COLOR_CORAL], width=0.38)
for bar in barras:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (total_vehiculos*0.01), f"{int(bar.get_height()):,}", ha='center', va='bottom', fontsize=9, fontweight='bold', color=HEX_TEXT)
estilizar_tarjeta_ui(ax, "KPI 1 | CONTROL DE CUENTAS OPERATIVAS", "Identifica usuarios activos frente a fugas comerciales a cantones vecinos.")
plt.savefig(os.path.join(CARPETA_SALIDA, 'kpi1.png'), bbox_inches='tight', facecolor=HEX_BG)
plt.close()

# KPI 2: Curva de Eficiencia de Citas
fig, ax = plt.subplots(figsize=(6, 3.8))
plt.subplots_adjust(top=0.78)
ax.plot(['1ra Instancia', '2da Instancia', '3ra Instancia'], [0, aprobado_2da, aprobado_3ra], marker='o', color=PALETA_MUTED[4], linewidth=2.2, markersize=5)
ax.fill_between(['1ra Instancia', '2da Instancia', '3ra Instancia'], [0, aprobado_2da, aprobado_3ra], color=PALETA_MUTED[4], alpha=0.10)
estilizar_tarjeta_ui(ax, "KPI 2 | RE-INSPECCIÓN Y COSTO EN PLANTA", "Monitorea el desgaste técnico de rodillos y sensores por reingresos repetitivos.")
plt.savefig(os.path.join(CARPETA_SALIDA, 'kpi2.png'), bbox_inches='tight', facecolor=HEX_BG)
plt.close()

# KPI 3: Distribución del Parque Automotor
fig, ax = plt.subplots(figsize=(6, 4.2))
plt.subplots_adjust(top=0.78, right=0.65) 
wedges, texts, autotexts = ax.pie([conteo_livianos, conteo_motos, conteo_pesados], labels=None, autopct='%1.1f%%', startangle=150, colors=PALETA_CYAN_PURP, pctdistance=0.60, wedgeprops=dict(width=0.18, edgecolor=HEX_CARD, linewidth=4))
for autotext in autotexts:
    autotext.set_fontsize(9)
    autotext.set_weight('bold')
fig.patch.set_facecolor(HEX_BG)
ax.set_facecolor(HEX_CARD)
ax.text(0.02, 1.12, "KPI 3 | DISTRIBUCIÓN DE PARQUE PARA CAPEX", transform=ax.transAxes, fontsize=12, fontweight='bold', color=HEX_TEXT)
ax.legend(wedges, ['Livianos', 'Motos', 'Pesados'], title="Categorías", loc="center left", bbox_to_anchor=(1.05, 0.5), facecolor=HEX_CARD, edgecolor='none', labelcolor=HEX_TEXT)
ax.text(0, 0, f'TOTAL\n\n{total_vehiculos:,}\n\nAutos', ha='center', va='center', fontsize=9, fontweight='bold', color=HEX_MUTED)
plt.savefig(os.path.join(CARPETA_SALIDA, 'kpi3.png'), bbox_inches='tight', facecolor=HEX_BG)
plt.close()

# KPI 4: Balance Financiero de Caja
fig, ax = plt.subplots(figsize=(6, 3.8))
plt.subplots_adjust(top=0.78)
barras = ax.bar(['Caja Efectiva', 'Cartera Vencida'], [recaudacion_real, fuga_dinero], color=[COLOR_MINT, COLOR_CORAL], width=0.38)
for bar in barras:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (recaudacion_proyectada_total*0.01), f"${bar.get_height():,.2f}", ha='center', va='bottom', fontweight='bold', color=HEX_TEXT, fontsize=8.5)
estilizar_tarjeta_ui(ax, "KPI 4 | BALANCE FINANCIERO DE CAJA", "Cuantifica el capital neto recaudado contra la fuga latente por cuentas por cobrar.")
ax.get_yaxis().set_visible(True) 
plt.savefig(os.path.join(CARPETA_SALIDA, 'kpi4.png'), bbox_inches='tight', facecolor=HEX_BG)
plt.close()

# KPI 5: Tasa de Rechazo Crítico por Antigüedad
fig, ax = plt.subplots(figsize=(6, 3.8))
plt.subplots_adjust(top=0.78)
barras = ax.bar(['Viejos (>15 años)', 'Nuevos (<=15 años)'], [reinspecciones_autos_viejos, reinspecciones_autos_nuevos], color=[COLOR_CORAL, PALETA_CYAN_PURP[0]], width=0.38)
for bar in barras:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, f"{int(bar.get_height()):,}", ha='center', va='bottom', fontweight='bold', color=HEX_TEXT, fontsize=9)
estilizar_tarjeta_ui(ax, "KPI 5 | ÍNDICE DE RIESGO E INDEMNIZACIONES", "Mide vehículos propensos a rupturas mecánicas críticas dentro de nuestros patios de revisión.")
plt.savefig(os.path.join(CARPETA_SALIDA, 'kpi5.png'), bbox_inches='tight', facecolor=HEX_BG)
plt.close()

# KPI 6: Antigüedad Promedio del Parque Automotor
fig, ax = plt.subplots(figsize=(6, 3.8))
plt.subplots_adjust(top=0.78)
promedios_edad = [antiguedad_por_tipo[t] / conteos_por_tipo[t] if conteos_por_tipo[t] > 0 else 0 for t in tipos_lista]
barras = ax.bar([t.capitalize() for t in tipos_lista], promedios_edad, color=sns.color_palette("Greys_r", 3), width=0.38)
for bar in barras:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2, f"{bar.get_height():.1f} años", ha='center', va='bottom', fontweight='bold', color=HEX_TEXT, fontsize=9)
estilizar_tarjeta_ui(ax, "KPI 6 | OBSOLESCENCIA PARA ESTRATEGIA PREMIUM", "Segmentación de edad promedio del parque para empaquetamiento de servicios adicionales.")
plt.savefig(os.path.join(CARPETA_SALIDA, 'kpi6.png'), bbox_inches='tight', facecolor=HEX_BG)
plt.close()

# KPI 7: Ticket Promedio de Recaudación
fig, ax = plt.subplots(figsize=(6, 3.8))
plt.subplots_adjust(top=0.78)
tickets = [avaluo_total_por_tipo[t] / matriculados_por_tipo[t] if matriculados_por_tipo[t] > 0 else 0 for t in tipos_lista]
barras = ax.bar([t.capitalize() for t in tipos_lista], tickets, color=PALETA_CYAN_PURP, width=0.38)
for bar in barras:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, f"${bar.get_height():.2f}", ha='center', va='bottom', fontweight='bold', color=HEX_TEXT, fontsize=9)
estilizar_tarjeta_ui(ax, "KPI 7 | AUDITORÍA DE TICKET PROMEDIO COBRADO", "Monitorea la rentabilidad neta individual que deja cada tipo de servicio en el software.")
plt.savefig(os.path.join(CARPETA_SALIDA, 'kpi7.png'), bbox_inches='tight', facecolor=HEX_BG)
plt.close()

# KPI 8: Tasa de Saturación por Dígito de Placa
fig, ax = plt.subplots(figsize=(7, 3.8))
plt.subplots_adjust(top=0.78)
ax.bar([f"D {k}" for k in saturacion_placa.keys()], saturacion_placa.values(), color=sns.color_palette("Blues_d", 10), width=0.55)
estilizar_tarjeta_ui(ax, "KPI 8 | ESTRÉS DE INFRAESTRUCTURA DE RED", "Predicción de carga y tráfico de servidores según el calendario impositivo de placas.")
plt.savefig(os.path.join(CARPETA_SALIDA, 'kpi8.png'), bbox_inches='tight', facecolor=HEX_BG)
plt.close()

print(f"Los 8 KPIs avanzados han sido exportados correctamente en la ruta: {CARPETA_SALIDA}")