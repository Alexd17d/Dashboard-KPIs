import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuración de estilos visuales profesionales
sns.set_theme(style="whitegrid")

# 1. CONEXIÓN AL REPOSITORIO (LEER ARCHIVO DE CONFIGURACIÓN)
# Definimos el nombre de las columnas tal cual la estructura de tu archivo C
columnas_vehiculos = ['usuario', 'placa', 'cedula', 'anio', 'tipo', 'avaluo', 'r1', 'r2', 'r3']

ruta_archivo = 'data/vehiculos.txt'

if not os.path.exists(ruta_archivo):
    print(f"[ERROR] No se encontro el archivo en '{ruta_archivo}'. Verifica que la carpeta 'data' exista.")
    exit()

# Carga de datos atómicos (TPS) usando Pandas
print("Cargando el repositorio transaccional...")
df = pd.read_csv(ruta_archivo, names=columnas_vehiculos, header=None)
print(f"[OK] Base de datos cargada con éxito. Total registros: {len(df):,}\n")

# Cálculos base obligatorios para los KPIs
df['matriculado'] = (df['r1'] == 1) | (df['r2'] == 1) | (df['r3'] == 1)
df['antiguedad'] = 2026 - df['anio']


# ============================================================
# PROCESAMIENTO KPI 1: PORCENTAJE DE VEHÍCULOS POR TIPO
# ============================================================
print("Procesando KPI 1: Porcentaje de vehiculos...")
conteo_tipos = df['tipo'].value_counts()

plt.figure(figsize=(6, 6))
plt.pie(conteo_tipos.values, labels=conteo_tipos.index, autopct='%1.1f%%', startangle=140, 
        colors=['#2c3e50', '#2980b9', '#f1c40f'], textprops={'fontweight': 'bold', 'size': 11})
plt.title('KPI 1: Porcentaje de Vehículos por Tipo\n(Composición del Parque Automotor)', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('data/kpi1_porcentaje_tipo.png') # Se guarda automáticamente en la carpeta data
plt.close()


# ============================================================
# PROCESAMIENTO KPI 2: RIESGO VEHICULAR POR ANTIGÜEDAD Y FALLAS
# ============================================================
print("Procesando KPI 2: Riesgo vehicular...")
# Lógica: Alto Riesgo = Más de 15 años y fallo en la primera revisión (r1 == 0)
def evaluar_riesgo(row):
    if row['antiguedad'] > 15 and row['r1'] == 0:
        return 'Alto Riesgo'
    elif row['antiguedad'] > 5 and row['r1'] == 0:
        return 'Riesgo Moderado'
    return 'Bajo Riesgo'

df['riesgo'] = df.apply(evaluar_riesgo, axis=1)
conteo_riesgo = df['riesgo'].value_counts().reindex(['Bajo Riesgo', 'Riesgo Moderado', 'Alto Riesgo'])

plt.figure(figsize=(7, 4.5))
sns.barplot(x=conteo_riesgo.index, y=conteo_riesgo.values, palette=['#2ecc71', '#f39c12', '#e74c3c'])
plt.title('KPI 2: Índice de Riesgo Vehicular Estructural\n(Antigüedad + Intentos Fallidos)', fontsize=12, fontweight='bold')
plt.ylabel('Cantidad de Unidades')
for i, v in enumerate(conteo_riesgo.values):
    plt.text(i, v + 500, f"{v:,}", ha='center', fontweight='bold')
plt.tight_layout()
plt.savefig('data/kpi2_riesgo_vehicular.png')
plt.close()


# ============================================================
# PROCESAMIENTO KPI 3: APROBACIONES POR TIPO DE VEHÍCULO
# ============================================================
print("Procesando KPI 3: Tasas de aprobacion...")
df_kpi3 = df.groupby(['tipo', 'matriculado']).size().unstack(fill_value=0)
df_kpi3.columns = ['No Aprobado (Moroso)', 'Aprobado (Matriculado)']

plt.figure(figsize=(8, 5))
df_kpi3.plot(kind='bar', stacked=False, color=['#e74c3c', '#2ecc71'], ax=plt.gca(), width=0.7)
plt.title('KPI 3: Tasa de Aprobación Final Segmentada por Tipo', fontsize=12, fontweight='bold')
plt.ylabel('Cantidad de Vehículos')
plt.xlabel('Tipo de Vehículo')
plt.xticks(rotation=0)
plt.legend(title='Estado Final')
plt.tight_layout()
plt.savefig('data/kpi3_aprobacion_tipo.png')
plt.close()

print("\n[PROCESO TERMINADO] Los 3 gráficos han sido generados y guardados en la carpeta 'data/'.")