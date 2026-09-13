import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuración principal de la página
st.set_page_config(
    page_title="Gestión Financiera - Prototipo Eventos",
    page_icon="💰",
    layout="wide" 
)

# 2. Inicialización de base de datos local (Simulando la nube para pruebas)
if "movimientos" not in st.session_state:
    st.session_state.movimientos = pd.DataFrame(columns=["ID", "Tipo", "Concepto", "Monto", "Fecha", "Usuario", "Comprobante"])
if "auditoria" not in st.session_state:
    st.session_state.auditoria = pd.DataFrame(columns=["Fecha/Hora", "Usuario", "Acción", "Detalle"])

# 3. Función central de Auditoría (Aquí se integra Firestore)
def registrar_auditoria(usuario, accion, detalle):
    # Guardado local para que la app funcione sin romperse
    nuevo_registro = pd.DataFrame([{
        "Fecha/Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Usuario": usuario,
        "Acción": accion,
        "Detalle": detalle
    }])
    st.session_state.auditoria = pd.concat([st.session_state.auditoria, nuevo_registro], ignore_index=True)
    
    # 🟢 INTEGRACIÓN FIRESTORE: Descomenta este bloque e inserta tus credenciales
    # try:
    #     db = firestore.client()
    #     db.collection('auditoria').add({
    #         "fecha_hora": datetime.now(),
    #         "usuario": usuario,
    #         "accion": accion,
    #         "detalle": detalle
    #     })
    # except Exception as e:
    #     st.error(f"Error guardando en Firestore: {e}")

# 4. Barra lateral (Sidebar) con control de usuarios
with st.sidebar:
    st.title("💰 Control Financiero")
    st.caption("Institución: Colegio Francisco de Paula Santander")
    
    st.divider()
    st.write("👤 **Simulador de Sesión:**")
    # Selector para simular quién está usando el sistema y registrarlo en la auditoría
    usuario_actual = st.selectbox(
        "¿Quién está usando el sistema?", 
        ["Saray Medina", "Lidiana", "Ivan Valencia", "Nicol Vanegas", "Sahra Sofia", "Shara Aguilar", "Alejandro Martinez"]
    )
    
    st.divider()
    st.write("📌 **Navegación:**")
    seccion = st.radio(
        "Ir a...",
        ["Inicio", "Registro e Ingresos", "Gastos e Insumos", "Balance", "Auditoría del Sistema"],
        label_visibility="collapsed"
    )

# 5. Contenido de la página principal (Inicio)
if seccion == "Inicio":
    st.title("🏛️ Proyecto de Control y Gestión Financiera")
    st.write("Plataforma centralizada para la administración y supervisión de recursos en eventos")
    
    st.success("✅ Estado del Sistema: Operativo y Sincronizado.")
    
    st.divider()
    st.subheader("👥 Equipo de Trabajo")
    
    datos_equipo = {
        "N.°": [1, 2, 3, 4],
        "Nombre Completo": [
            "Saray Medina / Ivan Santiago Valencia Villamil",
            "Nicol Vanegas Cruz",
            "Sahra Sofia Águila Vargas y Shara Aguilar",
            "Alejandro Martinez Rubio"
        ],
        "Rol / Responsabilidad": [
            "Liderazgo General / Administración",
            "Gestión de Registro e Ingresos",
            "Control de Gastos e Insumos",
            "Soportes y Control de Balance"
        ]
    }
    
    df_equipo = pd.DataFrame(datos_equipo)
    st.table(df_equipo.set_index("N.°"))

# 6. Módulo de Ingresos
elif seccion == "Registro e Ingresos":
    st.title("📈 Gestión de Registro e Ingresos")
    
    with st.form("form_ingresos", clear_on_submit=True):
        concepto = st.text_input("Concepto del Ingreso (Ej. Venta de entradas)")
        monto = st.number_input("Monto ($)", min_value=0.0, step=1000.0)
        submit = st.form_submit_button("Registrar Ingreso")
        
        if submit and concepto and monto > 0:
            nuevo_movimiento = pd.DataFrame([{
                "ID": len(st.session_state.movimientos) + 1,
                "Tipo": "Ingreso",
                "Concepto": concepto,
                "Monto": monto,
                "Fecha": datetime.now().strftime("%Y-%m-%d"),
                "Usuario": usuario_actual,
                "Comprobante": "N/A"
            }])
            st.session_state.movimientos = pd.concat([st.session_state.movimientos, nuevo_movimiento], ignore_index=True)
            
            registrar_auditoria(usuario_actual, "Registro de Ingreso", f"Añadió ingreso por ${monto:,.2f} concepto: {concepto}")
            st.success("¡Ingreso registrado correctamente!")

# 7. Módulo de Gastos (Con subida de PDFs)
elif seccion == "Gastos e Insumos":
    st.title("📉 Control de Gastos e Insumos")
    
    with st.form("form_gastos", clear_on_submit=True):
        concepto = st.text_input("Concepto del Gasto (Ej. Compra de decoración)")
        monto = st.number_input("Monto ($)", min_value=0.0, step=1000.0)
        comprobante = st.file_uploader("Subir Comprobante (Soporta PDF, PNG, JPG)", type=["pdf", "png", "jpg"])
        
        submit = st.form_submit_button("Registrar Gasto")
        
        if submit and concepto and monto > 0:
            nombre_archivo = comprobante.name if comprobante else "Sin comprobante adjunto"
            
            nuevo_movimiento = pd.DataFrame([{
                "ID": len(st.session_state.movimientos) + 1,
                "Tipo": "Gasto",
                "Concepto": concepto,
                "Monto": monto,
                "Fecha": datetime.now().strftime("%Y-%m-%d"),
                "Usuario": usuario_actual,
                "Comprobante": nombre_archivo
            }])
            st.session_state.movimientos = pd.concat([st.session_state.movimientos, nuevo_movimiento], ignore_index=True)
            
            registrar_auditoria(usuario_actual, "Registro de Gasto", f"Movió un gasto por ${monto:,.2f} - {concepto} (Adjunto: {nombre_archivo})")
            st.success("¡Gasto registrado correctamente!")

# 8. Módulo de Balance General
elif seccion == "Balance":
    st.title("⚖️ Soportes y Control de Balance")
    
    df = st.session_state.movimientos
    if df.empty:
        st.info("No hay movimientos financieros registrados todavía.")
    else:
        total_ingresos = df[df["Tipo"] == "Ingreso"]["Monto"].sum()
        total_gastos = df[df["Tipo"] == "Gasto"]["Monto"].sum()
        balance = total_ingresos - total_gastos
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Ingresos", f"${total_ingresos:,.2f}")
        col2.metric("Total Gastos", f"${total_gastos:,.2f}")
        
        # Color dinámico para el balance
        if balance >= 0:
            col3.metric("Balance Neto", f"${balance:,.2f}")
        else:
            col3.metric("Balance Neto", f"${balance:,.2f}", "- Déficit")
        
        st.divider()
        st.subheader("Historial de Movimientos Monetarios")
        st.dataframe(df, use_container_width=True, hide_index=True)

# 9. Módulo de Auditoría (El rastro de todos los usuarios)
elif seccion == "Auditoría del Sistema":
    st.title("🔎 Auditoría del Sistema")
    st.write("Control estricto de todos los movimientos y acciones realizadas por los usuarios.")
    
    if st.session_state.auditoria.empty:
        st.info("Aún no hay acciones registradas.")
    else:
        st.dataframe(st.session_state.auditoria, use_container_width=True, hide_index=True)
