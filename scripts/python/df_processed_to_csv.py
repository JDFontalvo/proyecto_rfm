import pandas as pd 
from pathlib import Path
from carga_datos import carga_datos
from limpieza_y_preparacion_df import limpieza_y_preparacion_rfm

def guardar_datos_procesados(df_procesado: pd.DataFrame, ruta_salida: Path): 
    """
    Exporta el DataFrame de Transacciones limpio a un archivo CSV en data/processed
    """
    if df_procesado.empty:
        print("⚠️ ADVERTENCIA: El DataFrame está vació, no es guardará el archivo")
        return
    
    try:
        # Pasamos el df a csv, con el metodo .to_csv()
        df_procesado.to_csv(
            ruta_salida,
            sep=',',
            index= False, # Evitamos que el índice de Pandas se guarde
            encoding= 'utf-8' 
        )
        print(f"✅ Archivo de transacciones limpio guardado en:\n{ruta_salida}")
        
    except Exception as e:
        print(f"❌ ERROR al intentar guardar el csv:\n{e}") 
    
    
    
if __name__ == "__main__":
    
    # -------------------------------------------------
    # 1. Definición de la RUTA BASE
    # -------------------------------------------------
    # Se usa pathlib para calcular la ruta absoluta de la raíz del proyecto.
    # .parent.parent.parent sube 3 niveles: .../proyecto_rfm/ (Raíz del proyecto)
    RUTA_BASE = Path(__file__).resolve().parent.parent.parent

    # -------------------------------------------------
    # 2. Definición de Rutas de I/O (Input/Output)
    # -------------------------------------------------
    # Ruta de Entrada (Input): data/raw
    RUTA_RAW_DATA =  RUTA_BASE / 'data' / 'raw' / 'Online_Rentail.csv'
    
    # Ruta de Salida (Output): data/processed
    RUTA_PROCESSED_DATA = RUTA_BASE / 'data' / 'processed' / 'Online_Rentail_processed.csv'
    
    # -------------------------------------------------------
    # 3. Cargamos los datos en un df
    # -------------------------------------------------------
    df_rfm = carga_datos(RUTA_RAW_DATA) 

    # Verificamos si la carga de los datos fue exitosa. Si no, omite el resto del ETL.
    if not df_rfm.empty:
        # -------------------------------------------------------
        #  4. Aplicamos limpieza y preparaciones iniales 
        # -------------------------------------------------------
        df_rfm_limpio_y_preparado = limpieza_y_preparacion_rfm(df_rfm)
        
        # -------------------------------------------------------
        #  5. Cargamos los datos limpios y procesados a su destino
        # -------------------------------------------------------
        guardar_datos_procesados(
            df_procesado=df_rfm_limpio_y_preparado,
            ruta_salida=RUTA_PROCESSED_DATA
            )
        print("\n✅ FASE 1 COMPLETADA: Transacciones listas para el análisis RFM.")
    else:
        print(f"\n❌ ETL ABORTADO: No se puede iniciar el procesamiento debido a un en la carga de los datos crudos")
        
