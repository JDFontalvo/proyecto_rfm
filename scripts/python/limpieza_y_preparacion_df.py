import pandas as pd 
from pathlib import Path
from carga_datos import carga_datos

def limpieza_y_preparacion_rfm(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplicar la limpieza de datos de transacciones (filtrado de filas)
    y realiza la ingenieria inial de la columna 'TotalVentas'.
    
    Este DataFrame limpio es el input para el cálculo RFM.
    
    Args:
        df (pd.DataFrame): DataFrame crudo de transacciones.
        
    Returns:
        pd.DataFrame: DataFrame limpio, listo para el calculo RFM.
    """
    if df.empty:
        print("⚠️ ABVERTENCIA: DataFrame vacío. No se puede realizar la limpieza")
        return df
    
    print(f"\n🧹 Iniciando la limpiado y preparación del datos.\n")
    
    # --- 1. Filtrado Críticos (Nulos en el ID) ---
    # La eliminación de filas sin CustomerID CRÍTICA porque no pueden ser segmentadas.
    df.dropna(subset=['CustomerID'], inplace=True)
    print("✅ 1. Filas sin CustomerID eliminadas.")
    
    
    # --- 2. MANEJO DE CANCELACIONES Y VALORES NO VÁLIDOS ---
    
    # 2.1 Normalización 'InvoiceNo' 
    # primero, se estandariza a string, elimina espacios y se capitaliza para facilitar el filtrado 'C'. 
    df['InvoiceNo'] = df['InvoiceNo'].astype(str).str.strip().str.capitalize()
    

    # 2.2 Eliminación transacciones canceladas
    # Las transaciónes con 'InvoiceNo' que empizan por 'C' son devoluciones.
    df = df[~df['InvoiceNo'].astype(str).str.contains('C')]
    print("✅ 2. Transacciones canceladas eliminadas.")
    
    
    # 2.3 Eliminación de errores de Rango Numérico (Canridad y Precio)
    # Se asegura que la cantidad vendida y el unitario son positivos.
    # Asegura tambien filtrar cualquier fila donde el precio o la cantidad se haya perdido
    # después de filtrar las 'C'.
    df = df[df['Quantity'] > 0]
    df = df[df['UnitPrice'] > 0]
    print("✅ 3. Filas con Quantity/UnitPrice no válidos eliminadas.")
    
    
    # --- 3. INGENIRIÁ  DE VARIABLES CLAVE --- 
    
    # 3.1 Cálculo de la Columna Monetary
    # El valor monetario por transacción es el producto de la cantidad vendida y 
    # su precio unitario, redondeado para asegurar formato contable.
    df['TotalVenta'] = (df['Quantity'] * df['UnitPrice']).round(2)
    print("✅ 4. Columna 'TotalVenta' calculada y agregada.")
    
    
    # --- 4. CONVERSIÓN INICIAL DE TIPOS (Recomendado aquí) ---
    
    # 4.1 InvoiceNO (Se carga como VARCHAR en SQL) 
    # Se mantiene como string, ya que contiene alfanuméricos.
    df['InvoiceNo'] = df['InvoiceNo'].astype('string') 
    
    # 4.2 CustomerID (Se carga como VARCHAR en SQL)
    # Limpieza y Conversión a String de float -> Int -> Str.
    df['CustomerID'] = df['CustomerID'].astype('Int64') # Limpieza a entero para eliminar dicimales (.0)
    df['CustomerID'] = df['CustomerID'].astype('string') # Conversión a string (el tipo ideal para identificadores/claves)
    
    # 4.3 Fecha/Tiempo (Se carga como DATETIME/TIMESTAMP en SQL)
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    # --- OPTIMIZACIÓN Y MANTENIMIENTO DE TIPO ---
    
    # 4.4 Optimización de Memoria (Se carga como VARCHAR en SQL) 
    # Se usa 'category' para columnas de baja cardinalidad.
    df['StockCode'] = df['StockCode'].astype('category') 
    df['Country'] = df['Country'].astype('category') 
    
    # 4.5 Descripción: Mantenemos como string explícito, ya que es texto libre(Alta cardinalidad).
    df['Description'] = df['Description'].astype('category') 
    
    # 4.6 Mantenimiento de Tipos (confirmación)
    # Quantity (int64/Int64) y UnitPrice (floar64/Decimal) están bien como están.
    
    print("✅ 5. Converciones finales aplicadas a las columanas del df exitosamente.")
    
    print("\n✅ DataFrame de Transacciones (df_limpio) listo para cálculo RFM.")
    
    return df

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

    print(f"\n🛣️    Ruta base del proyecto: {RUTA_BASE}")
    print(f"\n🛣️    Ruta al Archivo Raw: {RUTA_RAW_DATA}")

    # -------------------------------------------------
    # 3. Cargamos los datos y probarlos en un df
    # -------------------------------------------------
    df_rfm = carga_datos(RUTA_RAW_DATA)

    # -------------------------------------------------
    # 4. Cargamos los datos y probarlos en un df
    # -------------------------------------------------
    df_rfm_listo = limpieza_y_preparacion_rfm(df=df_rfm)
    
    if not df_rfm.empty:
        # Imprimimos las primeras filas y la descripción estadística
        print("\nPrimeras 5 filas:")
        print(df_rfm_listo.head())
        print("\nDescripción estadistica:")
        print(df_rfm_listo.describe())
        print("\nINFO:")
        df_rfm_listo.info(verbose=True, memory_usage='deep')
    else:
        print("\n❌ PRUEBA FALLIDA: El DataFrame final está vacío debido a un error de carga.")
    