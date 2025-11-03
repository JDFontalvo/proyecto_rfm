import pandas as pd 
from pathlib import Path
from carga_datos import carga_datos
import numpy as np

def _max_invoice_mas_un_dia(df: pd.DataFrame, col: str ='InvoiceDate'):
    """
    Calcula y devuelve la 'Fecha de Referencia' para la recencia.
    
    Esta es la fecha máxima en la columna 'col' más un día (max_day + 1 día).
    
    Args:
        df (pd.DataFrame): DataFrame de transacciones.
        col (str): Nombre de la columna de fecha ('InvoiceDate').
    
    Returns:
        pd.Timestamp: La fecha de referencia para el cálculo de Referencia, o pd.NaT si no hay fechas válidas.
        
    Raises:
        KeyError: Si la columna espificada no existe en el DataFrame.
    """
    if col not in df.columns:
        raise KeyError(f"La columna {col} no existe en el DataFrame")
        
    # Convierte la columna a datetime con manejo de errores (coerce a NaT)
    serie = pd.to_datetime(df[col], errors='coerce')
    
    # Verifica si existe fehcas válidas. Si todos son NaT, devuelve pd.Nat.
    if serie.dropna().empty:
        return pd.NaT
    
    max_fecha = serie.max()
    
    # Devolvemos la (Fecha de Referencia) = fecha máxima + 1 día
    return max_fecha + pd.Timedelta(days=1)


def generar_rfm_clientes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula y devuelve las métricas Recencia (R), Frecuencia (F), Monetary (M)
    agrupadas por cliente.
    
    Args:
        df (pd.DataFrame): DataFrame de transacciones con columnas necesarias.
        
    Returns:
        pd.DataFrame: DataFrame con las métricas RFM (CustomerID, Recency, Frequency, Monetary).
        
    Raises:
        ValueError: Si la 'Fecha de Referencia' no puede ser calculada.
        KeyError: Si faltan columnas criticas para el cálculo (TotalVenta, Quantity, Monetary).
    """
    # Creamos una copia para evitar modificar el DataFrame original.
    df_base = df.copy()
    
    # 1. Aseguramos que la columna de fecha ('InvoiceDate') sea  datetime
    df_base['InvoiceDate'] = pd.to_datetime(df_base.get('InvoiceDate'), errors='coerce')

    # 2. Calculamos la fecha de referencia
    fecha_ref = _max_invoice_mas_un_dia(df_base, col='InvoiceDate')

    # 3. Guardián: Verifica la validez de la Fecha de Referencia
    # Si (todos los valores de la columna son nulos) -> Aborta y levanta ValueError
    if pd.isna(fecha_ref):
        raise ValueError('No se puedo calcular fecha de referencia: InvoiceDate no contiene valores válidos')

    # 4. Guardián: Asegura que la columna 'TotalVenta' exista
    if 'TotalVenta' not in df_base.columns:
        # Usamos issubset() para verificar si las columnas requeridas están presentes.
        if {'Quantity','UnitPrice'}.issubset(df_base.columns): 
            # Crea 'Totalventa' si falta su valor en columnas base.
            df_base['TotalVenta'] = df_base['Quantity'] * df_base['UnitPrice']
        else:
            # Lanza error si no se puede obtener el valor monetario.  
            raise KeyError('No se encontró columna para calcular Monetary (necesaria: TotalVenta o Quantity y UnitPrice)')

    # 5. --- Agrupamiento y Limpieza ---
    
    # 5.1. Limpieza y Conversión de CustomerID a string (tipo ideal para claves)
    # Primero a tipo Int64 para limpieza para eliminar decimales (.0) y despues Conversión a string.
    df_base['CustomerID'] = df_base['CustomerID'].astype('Int64').astype('string') 

    # 5.2. Agrupary calcular R, F y M.
    agrup = df_base.groupby('CustomerID').agg(
        LastPurchase=('InvoiceDate', 'max'),    # R: Última compra
        Frequency=('InvoiceNo', 'nunique'),     # F: Conteo de facturas únicas
        Monetary=('TotalVenta', 'sum')          # M: suma total gasta
    ).reset_index()
    
    # 6. Cálculo final de Recency (diferencia en días).
    agrup['Recency'] = (fecha_ref - agrup['LastPurchase']).dt.days
    
    # 7. Redondeo de Monetary a 2 decimales (Redondeado).
    agrup['Monetary'] = agrup['Monetary'].round(2)
    
    # 8. Construimos el DataFrame RFM final.
    df_rfm = agrup[['CustomerID', 'Recency', 'Frequency', 'Monetary']].copy()
    
    # 9. Converciones finales de R y F a Int32 (más eficiente).
    df_rfm['Recency'] = df_rfm['Recency'].astype('Int32')
    df_rfm['Frequency'] = df_rfm['Frequency'].astype('Int32')
    
    print("✅ Cálculo RFM completado con éxito.")
    
    return df_rfm
    
if __name__ == "__main__":
    
    # -------------------------------------------------
    # 1. Definición de la RUTA BASE Y DE I/O
    # -------------------------------------------------
    # Se usa pathlib para calcular la ruta absoluta de la raíz del proyecto.
    # .parent.parent.parent sube 3 niveles: .../proyecto_rfm/ (Raíz del proyecto)
    RUTA_BASE = Path(__file__).resolve().parent.parent.parent
    RUTA_RAW_DATA =  RUTA_BASE / 'data' / 'processed' / 'Online_Rentail_processed.csv'
    RUTA_PROCESSED_DATA = RUTA_BASE / 'data' / 'processed' / 'RFM.csv'
    
    # ------------------------------------------------
    # 2. Cargamos los datos en un df
    # ------------------------------------------------
    df_base = carga_datos(RUTA_RAW_DATA) 

    if not df_base.empty:
        # ------------------------------------------------
        # 3. CÁLCULO Y PROCESAMIENTO RFM
        # ------------------------------------------------
        try:
            df_rfm = generar_rfm_clientes(df=df_base)
            
            # --- Imprimimos el resultado ---
            print("\n--- Resultado del Dataframe RFM")
            df_rfm.info(verbose=True, memory_usage='deep')
            
            # ------------------------------------------------
            # 4. GUARDADO DE RESULTADOS
            # ------------------------------------------------
            df_rfm.to_csv(path_or_buf=RUTA_PROCESSED_DATA, index=False)
            print(f"\n✅ Archivo RFM.csv guardo en: {RUTA_PROCESSED_DATA}")
            
        except ValueError as e:
            print(f"❌ Error en cálculo RFM: {e}")
        except KeyError as e:
            print(f"❌ Error: {e}")