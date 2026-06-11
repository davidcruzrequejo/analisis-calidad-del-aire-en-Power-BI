import pandas as pd
import numpy as np

# --- 1. Data Loading and Concatenation ---
filenames = [
    'Calidad-Aire-Madrid-21.csv',
    'Calidad-Aire-Madrid-22.csv',
    'Calidad-Aire-Madrid-23.csv',
    'Calidad-Aire-Madrid-24.csv',
    'Calidad-Aire-Madrid-25.csv'
]

all_dfs = []
for filename in filenames:
    df = pd.read_csv(f'../data/raw/Datos calidad del aire horarios 20-25/{filename}', delimiter=';')
    # Extract the year from the filename and add as a column
    year = int(filename.split('-')[-1].replace('.csv', ''))
    df['YEAR'] = year
    all_dfs.append(df)

combined_df = pd.concat(all_dfs, ignore_index=True)

# --- 2. Unpivoting DXX and VXX columns ---
# Define the common identifier columns
id_vars = ['PROVINCIA', 'MUNICIPIO', 'ESTACION', 'MAGNITUD', 'PUNTO_MUESTREO', 'ANO', 'MES', 'YEAR']

# Generate lists of DXX and VXX column names (D01-D31, V01-V31)
d_cols = [f'D{i:02d}' for i in range(1, 32)]
v_cols = [f'V{i:02d}' for i in range(1, 32)]

# Filter to only include columns that actually exist in the DataFrame
d_cols_existing = [col for col in d_cols if col in combined_df.columns]
v_cols_existing = [col for col in v_cols if col in combined_df.columns]

# Melt the 'DXX' columns to get 'Valor_Medida' and 'Dia'
df_melted_D = combined_df.melt(
    id_vars=id_vars,
    value_vars=d_cols_existing,
    var_name='Dia_col_D', # Temporary column name for the DXX column
    value_name='Valor_Medida'
)
df_melted_D['Dia'] = df_melted_D['Dia_col_D'].str[1:].astype(int)
df_melted_D = df_melted_D.drop(columns=['Dia_col_D'])

# Melt the 'VXX' columns to get 'Validado_raw'
df_melted_V = combined_df.melt(
    id_vars=id_vars,
    value_vars=v_cols_existing,
    var_name='Dia_col_V', # Temporary column name for the VXX column
    value_name='Validado_raw'
)
df_melted_V['Dia'] = df_melted_V['Dia_col_V'].str[1:].astype(int)
df_melted_V = df_melted_V.drop(columns=['Dia_col_V'])

# Merge the two melted DataFrames
final_df = pd.merge(df_melted_D, df_melted_V, on=id_vars + ['Dia'], how='left')

# Process the 'Validado_raw' column to create the 'Validado' boolean column
final_df['Validado'] = final_df['Validado_raw'].map({'N': False, 'V': True}).fillna(np.nan)
final_df = final_df.drop(columns=['Validado_raw'])

# Reorder columns for clarity (initial order before further drops/renames)
final_df_columns = id_vars + ['Dia', 'Valor_Medida', 'Validado']
final_df = final_df[final_df_columns]

# --- 3. Clean and Transform Data ---

# Convert 'YEAR' from 'YY' to 'YYYY' format (assuming 2000s)
# The original data had 21, 22, 23, 24, 25 for years which was mapped to 2021, 2022, etc
# The 'ANO' column might have full years already.
# Since we saw discrepancies and the user chose to drop YEAR, we'll ensure 'ANO' is used for the year
# and then drop 'YEAR'.

# First, ensure 'ANO' is correctly representing the full year, if it's in YY format, convert it.
# Based on `discrepancy_rows['ANO'].value_counts()`, `ANO` already had full years like `2021`. 
# So, the `YEAR` column (derived from filename, e.g., 21, 22) was the one needing adjustment if kept.
# Since the original notebook ultimately dropped 'YEAR' and kept 'ANO', we will ensure 'ANO' is correct.
# No explicit conversion needed for 'ANO' if it already holds full years from the source CSVs.

# Filter out rows where 'Validado' is False
final_df = final_df[final_df['Validado'] == True]

# Drop the 'YEAR' column (as per user's final decision in the notebook)
final_df = final_df.drop(columns=['YEAR'])

# Rename 'ANO' to 'Año'
final_df = final_df.rename(columns={'ANO': 'Año'})

# Rename 'PUNTO_MUESTREO' to 'Punto Muestreo' and remove underscores
final_df = final_df.rename(columns={'PUNTO_MUESTREO': 'Punto Muestreo'})
final_df['Punto Muestreo'] = final_df['Punto Muestreo'].astype(str).str.replace('_', '')

# Replace 'PROVINCIA' value 28 with 'Comunidad de Madrid'
final_df['PROVINCIA'] = final_df['PROVINCIA'].replace({28: 'Comunidad de Madrid'})

# Create 'Fecha' column by combining 'Dia', 'MES', and 'Año'
final_df['Fecha'] = pd.to_datetime(
    final_df['Dia'].astype(str).str.zfill(2) + '/' +
    final_df['MES'].astype(str).str.zfill(2) + '/' +
    final_df['Año'].astype(str),
    format='%d/%m/%Y'
)

# Rename columns to 'First Letter Upper' style
rename_map = {
    'PROVINCIA': 'Provincia',
    'MUNICIPIO': 'Municipio',
    'ESTACION': 'Estacion',
    'MAGNITUD': 'Magnitud',
    'MES': 'Mes',
    'Valor_Medida': 'Valor Medida'
}
final_df = final_df.rename(columns=rename_map)

# Format 'Fecha' column to 'DD/MM/YYYY' string format for display
final_df['Fecha Formateada'] = final_df['Fecha'].dt.strftime('%d/%m/%Y')

# Custom function to format numbers with Spanish decimal (comma) and thousands (dot) separators
def format_spanish_number(value):
    if pd.isna(value):
        return ''
    s_value = f"{value:.2f}"
    parts = s_value.split('.')
    int_part = parts[0]
    dec_part = parts[1]
    int_part_formatted = "{:,}".format(int(int_part)).replace(',', '.')
    return f"{int_part_formatted},{dec_part}"

# Apply the custom function to 'Valor Medida' to create a new formatted string column
final_df['Valor Medida Formateado'] = final_df['Valor Medida'].apply(format_spanish_number)

# Drop the original 'Fecha' (datetime object) and 'Valor Medida' (float) columns
final_df = final_df.drop(columns=['Fecha', 'Valor Medida'])

# Rename the formatted columns to their final names
final_df = final_df.rename(columns={
    'Fecha Formateada': 'Fecha',
    'Valor Medida Formateado': 'Valor Medida'
})

# Reorder columns as in the final step of the notebook
final_df = final_df[[
    'Provincia',
    'Municipio',
    'Estacion',
    'Punto Muestreo',
    'Magnitud',
    'Año',
    'Mes',
    'Dia',
    'Fecha',
    'Valor Medida',
    'Validado'
]]

# --- 4. Save to CSV ---
output_filename_csv = 'Calidad_Aire_Madrid_Actualizado_21-25.csv'
final_df.to_csv(output_filename_csv, index=False)
print(f"DataFrame saved to '{output_filename_csv}'")