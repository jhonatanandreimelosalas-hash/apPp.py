# Nexo Finanzas — prototipo mejorado

## Contenido
- `gemini-code-1789271135905.py`: archivo principal configurado para coincidir con el nombre que aparecía en los logs de Streamlit Cloud.
- `requirements.txt`: dependencias.
- `Proyecto_Financiero_Eventos_Actualizado.xlsx`: libro inicial vacío (también se crea automáticamente si falta).
- `README.md`: instrucciones.

## Publicar en Streamlit Cloud
1. Descomprime este ZIP.
2. Sube los archivos a la raíz del repositorio de GitHub que usa la app, conservando sus nombres.
3. En Streamlit Cloud, confirma que el repositorio y la rama sean los correctos y que el Main file path sea `gemini-code-1789271135905.py`.
4. Espera a que se instalen las dependencias y se reinicie.

## Funciones
- Panel resumen con ingresos, gastos, resultado y pendientes.
- Registro de ingresos y gastos con categorías, medio de pago y estado.
- Historial con filtros y exportación CSV.
- Presupuestos por categoría y alertas al acercarse/superar el límite.
- Registro de comprobantes, QR y descarga de imagen.
- Informes por rango de fechas y exportación Excel.

## Limitación importante
Esta versión usa un archivo Excel como almacenamiento. En Streamlit Cloud el sistema de archivos local no debe tratarse como almacenamiento permanente ni multiusuario. Para uso real con varios negocios y datos importantes, migrar la persistencia a Firebase/Firestore o una base de datos gestionada y añadir autenticación, permisos por empresa, auditoría y copias de seguridad.
