## 📁 Origen de Datos y Transformación

* **`/cleaned`:** Contiene los conjuntos de datos optimizados que alimentan directamente el modelo de Power BI.
* **`/raw`:** Contiene los archivos de datos originales y sin alterar del portal de datos abiertos de la Comunidad de Madrid y del Ayuntamiento de Madrid.

### ⚙️ Lógica de Transformación
* **Python (Pandas):** Utilizado para ingeniería de datos compleja, incluyendo la reestructuración de tablas mediante la **anulación de dinamización de columnas (unpivot)**, el manejo de matrices de sensores con valores faltantes y la adaptación de campos numéricos al formato europeo.
* **Power Query:** Utilizado para transformaciones ligeras durante la fase de ingesta y **consultas combinadas** para consolidar los datos relacionales directamente.
