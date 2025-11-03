import pandas as pd 
from pathlib import Path
from pandas.errors import ParserError

# -------------------------------------------------
# Definimos la carga segura de los datos
# -------------------------------------------------

def carga_datos(ruta_archivo: Path) -> pd.DataFrame:
    """
    Carga un archivo CSV desde la ruta especificada de forma segura,
    manejando codificaciones y errores comunes I/O (Input/Output).
    
    Aplica una lógica de respaldo: intenta cargar con UTF-8, y si falla
    por codificación, prueba con ISO-8859-1.
    
    Args:
        ruta_archivo (Path): Objeto Path de la libreria pathib que apunta al archivo CSV.
    
    Returns:
        pd.DataFrame: El DataFrame cargado, o un DataFrame vacio (pd.DataFrame())
                        si ocurre un error crítico.
    """
    print(f"\n⏳ Intentando cargar el archivo: {ruta_archivo.name}\n")
    try:
        # 1. Intentamos la codificación más moderna (UTF-8)
        df = pd.read_csv(
            ruta_archivo,
            encoding='UTF-8'
        )
        print("✅ Archivo cargado exitosamente.")
        return df
    except UnicodeDecodeError:
        # 2. Si UTF-8 falla, probamos con la altenativa común ISO-8859-1 o 'latin-1' si 'utf-8' falla
        print("⚠️ Abvertencia: Error de decodificación UTF-8. Intentando con ISO-8859-1.")
        df = pd.read_csv(
            ruta_archivo,
            encoding='ISO-8859-1' # Codificación comun para evitar errores de caracteres
            )
        print("✅ Archivo cargado exitosamente.")
        return df
    
    except FileNotFoundError:
        print(f"❌ ERROR CRÍTICO: Archivo no encontrado. Verificar la ruta: {ruta_archivo}")
        # Retornamos un DataFrame vacío (instancia) para evitar que el resto del script falle
        return pd.DataFrame()
    
    except ParserError as e:
        print(f"❌ ERROR DE PARSEO: Problema con el formato o separador CSV.\nDetalles: {e}")
        return pd.DataFrame()
    
    except Exception as e:
        print(f"❌ ERROR DESCONOCIDO durante la carga: {e}")
        return pd.DataFrame()
    
    
if __name__ == "__main__":
    # -------------------------------------------------
    # 1. Definición de la RUTA BASE
    # -------------------------------------------------
    # Se usa pathlib para calcular la ruta absoluta de la raíz del proyecto.
    # .parent.parent.parent sube 3 niveles: .../proyecto_rfm/ (Raíz del proyecto)
    RUTA_BASE = Path(__file__).resolve().parent.parent.parent

    # -------------------------------------------------
    # 2. Definición de Ruta de I (Input)
    # -------------------------------------------------
    # Ruta de Entrada (Input): data/raw
    RUTA_RAW_DATA =  RUTA_BASE / 'data' / 'raw' / 'Online_Rentail.csv'

    print(f"\n🛣️    Ruta base del proyecto: {RUTA_BASE}")
    print(f"\n🛣️    Ruta al Archivo Raw: {RUTA_RAW_DATA}")

    # -------------------------------------------------
    # 3. Cargamos los datos y probarlos en un df
    # -------------------------------------------------
    df_rfm = carga_datos(RUTA_RAW_DATA)
    
    if not df_rfm.empty:
        # Imprimimos las primeras filas y la descripción estadística
        print("\nPrimeras 5 filas:")
        print(df_rfm.head())
        print("\nDescripción estadistica:")
        print(df_rfm.describe())
        print("\nINFO:")
        df_rfm.info(verbose=True, memory_usage='deep')
    else:
        print("\n❌ PRUEBA FALLIDA: El DataFrame final está vacío debido a un error de carga.")
