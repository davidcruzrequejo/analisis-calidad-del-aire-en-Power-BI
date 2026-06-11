import pandas as pd

# Define the base path for the CSV files (adjust if running locally)
base_path = '../data/raw/Datos calidad del aire horarios 20-25/'

# Define the years and their specific file suffixes
years_files = {
    2020: 'Calidad-Aire-CCMM-20.csv',
    2021: 'Calidad-Aire-CCMM-21.csv',
    2022: 'Calidad-Aire-CCMM-22.csv',
    2023: 'Calidad-Aire-CCMM-23.csv',
    2024: 'Calidad-Aire-CCMM-24.csv',
    2025: 'Calidad-Aire-CCMM-25.csv',
    2026: 'Calidad-Aire-CCMM-26.csv'
}

dataframes = {}

print("--- Starting Data Loading ---")
# Load each CSV file into a DataFrame, explicitly using semicolon as separator
for year, filename in years_files.items():
    file_path = base_path + filename
    try:
        df = pd.read_csv(file_path, sep=';')
        dataframes[year] = df
        print(f"Successfully loaded {filename}.")
    except FileNotFoundError:
        print(f"Error: {filename} not found at {file_path}. Skipping.")
    except Exception as e:
        print(f"An error occurred loading {filename}: {e}. Skipping.")

print("All CSV files loaded using semicolon separator.")

print("\n--- Combining DataFrames ---")
all_data = []
for year, df in dataframes.items():
    if df is not None:
        df_copy = df.copy()
        df_copy['year'] = year
        all_data.append(df_copy)
    else:
        print(f"Warning: DataFrame for year {year} is empty or None and will be skipped during combination.")

if all_data:
    combined_df = pd.concat(all_data, ignore_index=True)
    print("All DataFrames successfully combined into 'combined_df'.")
else:
    print("No DataFrames were available to combine.")
    exit() # Exit if no data to process

print("\n--- Unpivoting Data (hXX and vXX columns) ---")
# Identify ID variables
id_vars = ['provincia', 'municipio', 'estacion', 'magnitud', 'punto_muestreo', 'ano', 'mes', 'dia', 'year']

# Identify columns to unpivot (h01-h24 and v01-v24)
h_v_cols = [col for col in combined_df.columns if col.startswith(('h', 'v')) and col[1:].isdigit()]

# Perform melt operation
melted_df = pd.melt(combined_df, id_vars=id_vars, value_vars=h_v_cols, var_name='variable_hora', value_name='valor_raw')

# Extract data type (h or v) and hour from original column name
melted_df['tipo_dato'] = melted_df['variable_hora'].str[0]
melted_df['hora'] = melted_df['variable_hora'].str[1:].astype(int)

# Pivot again to separate 'h' and 'v' values into distinct columns
hourly_data_df = melted_df.pivot_table(
    index=id_vars + ['hora'],
    columns='tipo_dato',
    values='valor_raw',
    aggfunc='first'
).reset_index()

# Rename the resulting 'h' and 'v' columns
hourly_data_df = hourly_data_df.rename(columns={'h': 'valor_medida', 'v': 'verificado'})

# Clean 'valor_medida': replace commas with dots and convert to numeric
hourly_data_df['valor_medida'] = hourly_data_df['valor_medida'].astype(str).str.replace(',', '.', regex=False)
hourly_data_df['valor_medida'] = pd.to_numeric(hourly_data_df['valor_medida'], errors='coerce')

# Clean 'verificado': ensure it's a consistent type, e.g., string
hourly_data_df['verificado'] = hourly_data_df['verificado'].astype(str)

# Select final desired columns
final_columns_unpivot = ['provincia', 'municipio', 'estacion', 'magnitud', 'punto_muestreo', 'ano', 'mes', 'dia', 'hora', 'valor_medida', 'verificado']
hourly_data_df = hourly_data_df[final_columns_unpivot]

print(f"Hourly data unpivoted. Initial shape: {hourly_data_df.shape}")

print("\n--- Filtering and Cleaning Data ---")
# Remove rows where 'ano' is 2020 or 2026
initial_rows_filter_year = hourly_data_df.shape[0]
hourly_data_df = hourly_data_df[~hourly_data_df['ano'].isin([2020, 2026])]
print(f"Removed {initial_rows_filter_year - hourly_data_df.shape[0]} rows for years 2020/2026. Current rows: {hourly_data_df.shape[0]}")

# Remove rows where 'verificado' is 'N', keeping only 'V'
initial_rows_filter_verified = hourly_data_df.shape[0]
hourly_data_df = hourly_data_df[hourly_data_df['verificado'] == 'V']
print(f"Removed {initial_rows_filter_verified - hourly_data_df.shape[0]} rows where 'verificado' was not 'V'. Current rows: {hourly_data_df.shape[0]}")

# Drop rows where 'valor_medida' is NaN
initial_rows_dropna = hourly_data_df.shape[0]
hourly_data_df.dropna(subset=['valor_medida'], inplace=True)
print(f"Removed {initial_rows_dropna - hourly_data_df.shape[0]} rows with NaN in 'valor_medida'. Current rows: {hourly_data_df.shape[0]}")

# Rename 'valor_medida' to 'Valor de medida'
hourly_data_df.rename(columns={'valor_medida': 'Valor de medida'}, inplace=True)
print("Column 'valor_medida' renamed to 'Valor de medida'.")

print("\n--- Creating Daily Summary ---")
daily_summary_df = hourly_data_df.groupby(['provincia', 'municipio', 'estacion', 'magnitud', 'punto_muestreo', 'ano', 'mes', 'dia'])['Valor de medida'].mean().reset_index()
print(f"Daily summary created. Shape: {daily_summary_df.shape}")

print("\n--- Applying Final Transformations ---")
# 1. Create 'Fecha' column and drop 'ano', 'mes', 'dia'
daily_summary_df['Fecha'] = pd.to_datetime(daily_summary_df[['ano', 'mes', 'dia']].astype(str).agg('-'.join, axis=1), format='%Y-%m-%d')
daily_summary_df['Fecha'] = daily_summary_df['Fecha'].dt.strftime('%d/%m/%Y')
daily_summary_df = daily_summary_df.drop(columns=['ano', 'mes', 'dia'])

# 2. Modify 'provincia' column
daily_summary_df['provincia'] = daily_summary_df['provincia'].astype(str)
daily_summary_df['provincia'] = daily_summary_df['provincia'].replace('28', 'Comunidad de Madrid')

# 3. Create 'Codigo Muestreo' and modify 'punto_muestreo'
daily_summary_df['Codigo Muestreo'] = daily_summary_df['punto_muestreo'].apply(lambda x: str(x).split('_')[0])
daily_summary_df['punto_muestreo'] = daily_summary_df['punto_muestreo'].astype(str).str.replace('_', ' ').str.title()

# 4. Format 'Valor de medida' to string with comma for decimals
daily_summary_df['Valor de medida'] = daily_summary_df['Valor de medida'].apply(lambda x: str(x).replace('.', ','))

# 5. Rename all columns (capitalize and remove underscores)
new_columns_mapping = {}
for col in daily_summary_df.columns:
    if col == 'Valor de medida':
        new_columns_mapping[col] = 'Valor De Medida'
    elif col == 'Fecha':
        new_columns_mapping[col] = 'Fecha'
    elif col == 'Codigo Muestreo':
        new_columns_mapping[col] = 'Codigo Muestreo'
    else:
        new_columns_mapping[col] = col.replace('_', ' ').title()
daily_summary_df = daily_summary_df.rename(columns=new_columns_mapping)

# 6. Reorder columns for better readability
final_order = [
    'Provincia', 'Municipio', 'Estacion', 'Codigo Muestreo', 'Punto Muestreo',
    'Magnitud', 'Fecha', 'Valor De Medida'
]
daily_summary_df = daily_summary_df[final_order]
print("Final transformations applied and columns reordered.")

# Verify years included
unique_years = pd.to_datetime(daily_summary_df['Fecha'], format='%d/%m/%Y').dt.year.unique()
print(f"Years considered in the final DataFrame: {sorted(unique_years)}")

print("\n--- Saving Final DataFrame to CSV ---")
output_csv_filename = 'Calidad_Aire_Comunidad_21-25.csv'
daily_summary_df.to_csv(output_csv_filename, index=False, encoding='utf-8')
print(f"DataFrame successfully saved as '{output_csv_filename}'")

print("\n--- Script Finished ---")