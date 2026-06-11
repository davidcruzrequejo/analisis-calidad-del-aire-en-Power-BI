# 📁 Data Lineage & Processing Notes

* **`/raw`:** Contains the original, unaltered open data files from the Comunidad de Madrid and the Ayuntamiento de Madrid.
* **`/cleaned`:** Contains the optimized datasets feeding directly into the Power BI model.

### ⚙️ Transformation Logic
* **Python (Pandas):** Used for complex data engineering, including reshaped tables via **unpivot transformations**, handling missing sensor matrices, and adapting numerical fields to European locale formats.
* **Power Query:** Used for lightweight upstream transformations and **merged queries** to consolidate straightforward relational data during the ingestion phase.
