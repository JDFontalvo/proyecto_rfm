# Proyecto RFM — Análisis de Retención y Valor de Vida del Cliente (CLV)

Este repositorio contiene un proyecto end-to-end para calcular scores RFM (Recency, Frequency, Monetary) a partir de transacciones de retail online, preparar los datos y exponer resultados para visualización y acción de negocio.

## Resumen ejecutivo

El objetivo es convertir transacciones crudas en segmentos accionables de clientes. El pipeline realiza:

- Ingesta y limpieza de datos transaccionales.
- Cálculo de métricas R, F, M por cliente.
- Optimización de tipos para eficiencia en memoria.
- Persistencia de resultados y facilidades para crear dashboards (Power BI).

## Estructura del repositorio

- `data/raw/` — CSV crudo ( `Online_Rentail.csv`).
- `data/processed/` — CSV(s) transformados y artefactos (`Online_Rentail_processed`, `RFM`).
- `scripts/python/` — scripts de carga, limpieza, cálculo RFM y utilidades de conexión.
- `reports/` — carpeta para archivos de visualización exportados (`.pbix`).
- `requirements.txt` — dependencias del proyecto.

## Descripción de los datos

El dataset de ejemplo contiene columnas clave:
`InvoiceNo`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `UnitPrice`, `CustomerID`, `Country`.

Recomendaciones de preprocesamiento:

- Convertir `InvoiceDate` a datetime (`pd.to_datetime(..., errors='coerce')`).
- Calcular `TotalVenta = Quantity * UnitPrice` si no existe.
- Eliminar filas con `CustomerID` nulo.
- Filtrar transacciones de devolución (InvoiceNo que comienzan con 'C').

## Pipeline ETL (resumen)

1. Lectura segura del CSV con `carga_datos()` (manejo de codificación y errores).
2. Limpieza y preparación con `limpieza_y_preparacion_rfm()`:
   - Filtrado de devoluciones y nulos.
   - Creación de columnas necesarias (p. ej. `TotalVenta`).
3. Cálculo RFM con `generar_rfm_clientes()`:
   - `fecha_referencia = max(InvoiceDate) + 1 día` (defensivo: convertir a datetime y validar).
   - `Recency` = días desde la última compra hasta `fecha_referencia`.
   - `Frequency` = número de facturas únicas por cliente.
   - `Monetary` = suma de `TotalVenta` por cliente.
4. Optimización de tipos: convertir `Recency` y `Frequency` a `Int32` para ahorrar memoria.
5. Guardar resultados en `data/processed/rfm_clientes_final.csv` y opcionalmente subir a MySQL.

## Cálculo seguro de la fecha de referencia

Se recomienda usar una función que convierta a datetime con coerción y entregue `max + 1 día` o `pd.NaT` si no hay fechas válidas. Ejemplo (ya implementado):

```python
def max_invoice_mas_un_dia(df, col='InvoiceDate'):
    serie = pd.to_datetime(df[col], errors='coerce')
    if serie.dropna().empty:
        return pd.NaT
    return serie.max() + pd.Timedelta(days=1)
```

## Infraestructura local recomendada

Se sugiere usar MySQL en Docker para desarrollo reproducible.

```powershell
# Levantar MySQL en Docker (ejemplo de desarrollo)
docker run --name rfm-mysql-db -e MYSQL_ROOT_PASSWORD=RFM_root_pass -d -p 3307:3306 mysql:8.0

# Crear la base de datos de destino (desde el contenedor o cliente MySQL)
docker exec -it rfm-mysql-db mysql -u root -p
# (ingresa contraseña RFM_root_pass)
# mysql> CREATE DATABASE IF NOT EXISTS mi_proyecto_rfm;
# mysql> EXIT;
```

### Nota sobre Power BI y MySQL 8.0

Power BI puede requerir que el usuario MySQL use `mysql_native_password`. Si aparece error de autenticación, ejecutar:

```sql
ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'RFM_root_pass';
FLUSH PRIVILEGES;
```

## Cómo ejecutar (desarrollo local)

Instalar dependencias:

```powershell
pip install -r requirements.txt
```

Ejecutar el pipeline interactivo que verifica conexión y sube resultados:

```powershell
python ./scripts/python/verificar_conexion_mysql.py
```

Ejecutar solo cálculo RFM y guardar resultado local:

```powershell
python ./scripts/python/calculate_rfm.py
```

Si `python` no está en PATH en Windows usar `py -3`.


## Visualización y dashboards

Flujo recomendado:

1. Persistir `rfm_clientes_final.csv` o su tabla en MySQL.
2. Conectar Power BI al CSV o a la tabla MySQL.
3. Construir vistas y KPIs: distribución R/F/M, mapa de segmentos, KPIs de ventas por segmento.

Guardar artefactos en `reports/powerbi/` (.pbix) y exportar imágenes/PDF para el portafolio.

## Buenas prácticas y reproducibilidad

- Versionar artefactos procesados: `Online_Rentail_processed_YYYYMMDD.csv`.
- Guardar `fecha_referencia` en `data/processed/metadata_fecha_ref.txt` para auditoría.
- Añadir tests unitarios (`pytest`) para funciones críticas.
- Usar entorno virtual y pinnear versiones en `requirements.txt`.


## 🤝 Contacto

Proyecto por: **Jesús David Fontalvo Mendoza**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Perfil_Profesional-blue?style=flat&logo=linkedin)](www.linkedin.com/in/jesús-fontalvo-mendoza-4550072ab)


