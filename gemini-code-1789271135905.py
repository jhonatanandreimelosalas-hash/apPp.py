import streamlit as st
import pandas as pd

# 1. Configuración principal de la página
st.set_page_config(
    page_title="Gestión Financiera - Prototipo Eventos",
    page_icon="💰",
    layout="centered" # Puede ser "wide" si prefieres que ocupe toda la pantalla
)

# 2. Barra lateral (Sidebar)
with st.sidebar:
    st.title("💰 Control Financiero")
    st.write("📌 Selecciona una sección:")
    
    # Menú de navegación simulado basado en los roles del equipo
    seccion = st.radio(
        "Navegación",
        ["Inicio", "Registro e Ingresos", "Gastos e Insumos", "Balance"],
        label_visibility="collapsed"
    )

# 3. Contenido de la página principal (Inicio)
if seccion == "Inicio":
    st.title("🏛️ Proyecto de Control y Gestión Financiera")
    st.write("Plataforma centralizada para la administración y supervisión de recursos en eventos")
    
    st.divider() # Línea separadora
    
    st.subheader("🎯 Objetivo del Sistema")
    st.write("Control transparente y automatizado de los movimientos monetarios, auditoría en tiempo real y generación de comprobantes.")
    
    # Mensaje de estado (usando st.success para el cuadro verde de éxito)
    st.success("✅ Estado del Sistema: Operativo y Sincronizado.")
    
    st.divider()
    
    st.subheader("👥 Equipo de Trabajo")
    
    # 4. Creación de la tabla de datos
    datos_equipo = {
        "N.°": [1, 2, 3, 4],
        "Nombre Completo": [
            "Ivan Santiago Valencia Villamil",
            "Nicol Vanegas Cruz",
            "Jhonatan Andrey Melo",
            "Alejandro Martinez Rubio"
        ],
        "Rol / Responsabilidad": [
            "Líder de Proyecto / Administración",
            "Gestión de Registro e Ingresos",
            "Control de Gastos e Insumos",
            "Soportes y Control de Balance"
        ]
    }
    
    df_equipo = pd.DataFrame(datos_equipo)
    
    # Mostramos la tabla ocultando el índice por defecto para que sea idéntica a la original
    st.table(df_equipo.set_index("N.°"))

# Plantillas vacías para las otras secciones
elif seccion == "Registro e Ingresos":
    st.title("Gestión de Registro e Ingresos")
    st.info("Módulo en construcción...")

elif seccion == "Gastos e Insumos":
    st.title("Control de Gastos e Insumos")
    st.info("Módulo en construcción...")

elif seccion == "Balance":
    st.title("Soportes y Control de Balance")
    st.info("Módulo en construcción...")