# 📊 Dashboard Interactivo: Calidad del Aire en la Comunidad de Madrid

### 🔗 [👉 HAZ CLIC AQUÍ PARA INTERACTUAR CON EL DASHBOARD EN VIVO 👈](https://app.powerbi.com/view?r=eyJrIjoiZWNlNjZlMDQtM2MxOS00YTFhLTliZmUtNmY4M2ExZDM4MjQyIiwidCI6Ijc5ZmFkMTk4LTcxMzYtNDZhMC1iNzJkLTgyODFmOTk1ZTdmOSJ9)

## 🎯 Propósito del Proyecto
Este proyecto transforma **datos abiertos** públicos en una herramienta interactiva de Business Intelligence. El objetivo es analizar de forma visual la evolución de la contaminación y la calidad del aire en la Comunidad de Madrid, permitiendo identificar patrones temporales y zonas de riesgo ambiental.

## 🛠️ Tecnologías y Habilidades Utilizadas
* **Ingeniería de Datos (Python - Pandas):** Limpieza de datos masivos, manejo de registros no validos, **combinación de consultas** de tablas con distintos atributos, agrupación de datos para pasar de datos horarios a diarios (promedios) de calidad del aire y relacionarlos con los datos metereológicos diarios. **Unpivot** mediante librería Pandas de tablas de datos para obtener distintos datos diarios de cada nivel de contaminante y parámetro metereológico.
* **Modelado de Datos (Power BI):** Creación de un **modelo en estrella** (*Star Schema*) eficiente para conectar estaciones de medición con reportes de contaminación, relacionando distintas **dimensiones** de tiempo, lugar, códigos de estaciones y magnitudes medidas.
* **Análisis Estadístico (DAX):** Creación de **métricas personalizadas** para calcular promedios móviles y alertas de superación de límites legales de gases, y asignar **formato** (color) a distintos gráficos de barras si los contaminantes superan valores límites permitidos por la OMS.

## 📸 Vista Previa del Dashboard interactivo
![Dashboard Preview](dashboard_interaction_teaser.gif)
Como se muestra en la interacción, el dashboard permite:
1. Estudiar la evolución, los sectores, y sus actividades, que emiten contaminantes a lo largo del tiempo en la Comunidad de Madrid, a nivel general y por municipio y zona regional.
2. Analizar la evolución, distribución territorial y principales contaminantes presentes por municipio, haciendo foco en la ciudad de Madrid por distritos. Esto permite diferenciar donde y cuando se dan ciertos contaminantes en mayor o menor medida. (Partiendo de los datos disponibles por las estaciones de medición de calidad del aire, esto implica que algunos municipios o distritos no tengan datos disponibles porque no tomaron medida de un contaminante en específico).
3. Por último se analiza visualmente la correlación, si existe, con distintos parámetros metereológicos, y como influyen en la aparición de un contamimante en distintos periodos del año en mayor o menor medida.
