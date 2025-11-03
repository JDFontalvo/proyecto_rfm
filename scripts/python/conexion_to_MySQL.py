from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import pandas as pd 
from typing import Optional
from sqlalchemy.engine import Engine
import getpass
from pathlib import Path
from carga_datos import carga_datos
from limpieza_y_preparacion_df import limpieza_y_preparacion_rfm
from calculate_rfm import generar_rfm_clientes
from verificar_conexion_mysql import get_connection

def conexion_mysql(
    db_name: str = 'mi_proyecto_rfm',
    host: str = 'localhost',
    user: str = 'root',
    password: str = 'RFM_root_pass',
    port: str = '3307'
    ) -> Optional[Engine]:
    """
    Verifica la conexión a MySQL usando la utilidad `get_connection` (mysql-connector)
    y, si es exitosa, crea y devuelve un SQLAlchemy Engine para operaciones posteriores.

    Retorna:
      - Engine (sqlalchemy.engine.Engine) si la conexión y verificación son exitosas
      - None si hay algún fallo
    """
    print(f"\n⏳ Verificando la conexión a la base de datos `{db_name}` usando conexion_to_MySQL.get_connection...")

    # 1) Intentar verificar con get_connection (mysql-connector)
    try:
        conn, ok = get_connection(host=host, port=int(port), user=user, password=password, database=db_name)
    except Exception as e:
        print(f"❌ Error al intentar verificar conexión con get_connection: {e}")
        return None

    if not ok or conn is None:
        print(f"\n❌ No se pudo conectar a MySQL usando mysql-connector-python. Revisa credenciales/host/puerto.")
        return None

    # 2) Cerrar la conexión directa y construir un SQLAlchemy engine reutilizable
    try:
        try:
            conn.close()
        except Exception:
            pass

        connection_string = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db_name}"
        engine = create_engine(connection_string, connect_args={'connect_timeout': 10})

        # Verificar que el engine responda
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        print(f"✅ Conexion a '{db_name}' establecida con éxito (engine SQLAlchemy listo).")
        return engine

    except OperationalError as e:
        print(f"\n❌ ERROR DE CONEXIÓN OPERACIONAL al crear el engine SQLAlchemy: {e}")
        return None
    except Exception as e:
        print(f"❌ ERROR INESPERADO al crear/verificar el engine SQLAlchemy: {e}")
        return None
            
# --- Función Auxiliar para Seleccionar Opciones ---
def _seleccionar_opcionn(opciones: dict, mensaje: str) -> str:
    """
    Muestra opciones numeradas y pide al usuario que seleccione una.
    
    Returns:
        opciones[seleccion] (dict): Diccionario con la opcionn y la selección
    
    """
    print(f"\n{mensaje}")
    for key, value in opciones.items():
        print(f" [{key}] {value}")
        
    seleccion = input("\n   >Ingrese el número o ingrese su propio valor aquí: ")
    
    if seleccion.isdigit() and int(seleccion) in opciones:
        return opciones[int(seleccion)]
    else:
        #Si el usuario no elige una opción, se tomo su entrada como valor personalizado
        return seleccion.strip()

# --- Bloque de Ejecución Principal Interactivo ---
if __name__ == "__main__":

    #------------------------------------------------------------
    # BUCLE INTERACTIVO DE CONEXIÓN 
    #------------------------------------------------------------
    while True:   
          
        print("\n===================================================")
        print("⚙️   INICIANDO CONFIGURACIÓN INTERACTIVA DE MYSQL")
        print("===================================================\n")
        
        # --- 1. HOST (Dirección del servidor) ---
        host_opciones = {1: 'localhost', 2: '127.0.0.1'}
        # host_opciones = {1: 'localhost', 2: '127.0.0.1', 3: 'Otra (Ingresa IP/Nombre)'}
        DB_HOST = _seleccionar_opcionn(host_opciones, "¿Cuál es la dirección (Host) de se servidor MySQL") or 'localhost'
        
        # --- 2. PUERTO (Puerto de conexión) ---
        port_opciones = {1:'3307', 2:'3306'}
        DB_PORT = _seleccionar_opcionn(port_opciones, "¿Cuál es el Puerto de Conexión de su instancia MySQL") or '3307'
        
        # --- 3. USUARIO ---
        DB_USER = input("\n👤 Ingrese el Nombre de Usuario de MySQL (ej: root): ").strip() or 'root'
        
        # --- 4. CONTRASEÑA ---
        DB_PASS = getpass.getpass("🔒 Ingrese la Contraseña de MySQL :").strip() or 'RFM_root_pass'
        
        # --- 5. BASE DE DATOS (Shema) ---
        DB_NAME = input("\n Ingrese el Nombre de la Base de Datos (Schema) donde se guardará el archivo RFM: ").strip() or 'mi_proyecto_rfm'
        
        # --- 6. NOMBRE DE LA TABLA ---
        DB_TABLE = input(" Ingrese el Nombre que desea darle a la tabla RFM (ej: rfm): ").strip() or 'rfm'
        
        
        print("\n Configuración de conexión completada.\n Datos recogidos: ")
        print(40*"=")
        print(f"    Host: {DB_HOST}")
        print(f"    Puerto: {DB_PORT}")
        print(f"    Usuario: {DB_USER}")
        print(f"    DB/Schema: {DB_NAME}")
        print(f"    Tabla: {DB_TABLE}")
        print(40*"="+"\n")

        # Lógica de confirmación: pide la entrada y la valida
        opcion_confirmacion = input("La información es correcta?\n[1] Para confirmar\n[2] Para reintentar\n[3] Para salir de forma segura\n  >Ingrese el número aquí: ").strip()
        
        
        if opcion_confirmacion == '1':
            # Sale del bucle para continuar con el resto del codigo
            print(f"\n✅ Datos confirmados. \n⏳ Intentando la prueba de conexión a MySQL...")
            # -------------------------------------------
            # 5. PRUEBA y continuación del flujo: si la conexión es exitosa
            # -------------------------------------------
            engine = conexion_mysql(
                db_name=DB_NAME,
                password=DB_PASS,
                user=DB_USER,
                host=DB_HOST,
                port=DB_PORT)

            if engine is not None:
                
                try:
                    # Definimos ruta base y archivo raw (misma convención que en otros scripts)
                    RUTA_BASE = Path(__file__).resolve().parent.parent.parent
                    RUTA_RAW_DATA = RUTA_BASE / 'data' / 'raw' / 'Online_Rentail.csv'

                    print("\n⏳ Cargando y procesando datos para subir a la base de datos...")
                    df_raw = carga_datos(RUTA_RAW_DATA)

                    # Aplicar limpieza y preparación (función del repo)
                    df_processed = limpieza_y_preparacion_rfm(df_raw)
                
                    # Generar RFM
                    df_rfm = generar_rfm_clientes(df_processed)
                    
                    # ----------------------------------------------------------------------
                    # --- SUBIDA DE LOS DOS DATAFRAMES A MYSQL (POR SEPARADO) ---
                    # ----------------------------------------------------------------------
                    
                    # 1. Subir la tabla de transacciones procesadas
                    print("⚙️ Subiendo tabla de transacciones limpias: 'Online_Ratail_processed'")
                    df_processed.to_sql(
                        name='Online_Ratail_processed',  # Nombre de la tabla 1
                        con=engine,
                        if_exists='replace',
                        index=False
                    )

                    # 2. Subir la tabla de resultados RFM (Segmentación)
                    print(f"⚙️ Subiendo tabla de segmentación RFM: '{DB_TABLE}'")
                    df_rfm.to_sql(
                        name=DB_TABLE,  # Nombre de la tabla 2 (por ejemplo, 'rfm')
                        con=engine,
                        if_exists='replace',
                        index=False
                    )
                    
                    print(f" !Éxito¡ Ambas tablas se subieron correctamente a la base '{DB_NAME}'. ")
                    print(f"Tablas subidas: 'Online_Ratail_processed' y '{DB_TABLE}'.")
                    print(f"Puedes verificar la tabla y su contenido en tu gestor de MySQL")
                    exit()
                except Exception as e:
                    print(f"❌ Error durante preparación o subida de datos: {e}")
                finally:
                    # Cerrar el engine cuando terminemos
                    try:
                        engine.dispose()
                    except Exception:
                        pass

        elif opcion_confirmacion == '2':
            # El buble True se repetira, pidiendo los datos nuevamente
            print("\n🔄  Reiniciando la conifiguaración de conexión ...")
            continue
        elif opcion_confirmacion == '3':
            # Salida segura, interrumpe la ejecución completa del script
            print("⚠️  Salida segura solicitada. El script terminará ahora.")
            exit()
        else:
            # Opción no reconocida, se asuma que debe reintentar.
            print("\n🚫 Opción no válida, Por favor, ingrese 1, 2 o 3 ..\n🔄 Reiniciando la configuración de conexión ...")
            continue
        

            
    
    