
# MIS: Dashboard Gerencial y Visualización de KPIs 📊🚗

Este repositorio contiene la capa del **Sistema de Información Gerencial (MIS)** del proyecto de Matriculación Vehicular. Su objetivo principal es consumir los datos atómicos y transaccionales generados por el **TPS (Transaction Processing System)** desarrollado en C, consolidarlos en un repositorio común y transformarlos en reportes estructurados (KPIs) para el apoyo a la toma de decisiones estratégicas.

---

##  Enlace Arquitectónico (TPS vs. MIS)

De acuerdo con el enfoque de sistemas:
* **TPS (Desarrollado en C):** Se encarga del monitoreo, recolección y almacenamiento diario de las operaciones básicas (alta de usuarios, registro de vehículos y bitácora de revisiones técnicas) en tiempo real y a nivel atómico.
* **MIS (Desarrollado en Python):** Extrae la información desde el repositorio transaccional del TPS (`vehiculos.txt` y `usuarios.txt`), procesa matemáticamente los datos en fracciones de segundo y los sintetiza en indicadores clave de rendimiento (KPIs) orientados a mandos medios y gerenciales, mitigando el principio *GIGO (Garbage In, Garbage Out)* mediante validaciones de integridad.

---

##  Indicadores Clave de Rendimiento (KPIs) Implementados

El sistema transforma **Datos Crudos (Data Items)** en **Información Contextualizada (Information)** para generar **Conocimiento Aplicado (Knowledge)** en tres ejes estratégicos:

| KPI | Dimensión | Lógica Gerencial (Knowledge) |
| :--- | :--- | :--- |
| **1. Índice de Morosidad Vehicular** | Control de Procesos / Financiero | Si la evasión anual supera el 25%, la gerencia ejecutará campañas automáticas de notificación por correo y coordinará operativos viales coactivos. |
| **2. Eficiencia en Citas de Revisión** | Optimización Operativa | Si la mayoría de los usuarios aprueba la revisión técnica vehicular recién en su 3ra cita (`0,0,1`), la gerencia auditará los manuales técnicos para eliminar cuellos de botella artificiales. |
| **3. Carga por Tipo de Vehículo** | Planificación Urbana | Si el volumen de transporte pesado incrementa de forma sostenida, la alcaldía reestructurará los presupuestos de mantenimiento asfáltico y restringirá los horarios de circulación urbana. |

---

##  Conexión en Tiempo Real (Desacoplamiento)

Para cumplir con el requerimiento de desacoplamiento arquitectónico, este MIS se aloja en un repositorio Git independiente del TPS. La lectura de datos en "tiempo real" se genera de forma local mediante **rutas relativas** entre ambos directorios en el entorno de desarrollo:



## Requisitos e Instalación

### Prerrequisitos

Es necesario contar con Python 3 instalado en el sistema. Puedes instalar las librerías analíticas necesarias ejecutando el siguiente comando en tu terminal:

```bash
pip install pandas matplotlib seaborn

```

### Ejecución del Reporte Gerencial

Para procesar las más de 90,000 transacciones simuladas del parque automotor y desplegar el cuadro de mando visual, ejecuta:

```bash
python reporte_mis.py

```

*Nota: La consulta y renderizado de gráficos tarda menos de 0.3 segundos gracias al motor optimizado de vectores indexados de Pandas, cumpliendo con el atributo de valor de **Oportunidad (Timeliness)**.*

```

