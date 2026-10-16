import os
import uuid
from datetime import date, datetime
from io import BytesIO

import pandas as pd
import qrcode
import streamlit as st

# ------------------------------------------------------------
# Configuración
# ------------------------------------------------------------
st.set_page_config(
    page_title="Nexo Finanzas | Control simple",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = "Proyecto_Financiero_Eventos_Actualizado.xlsx"
SHEETS = {
    "Movimientos": ["ID", "Fecha", "Tipo", "Concepto", "Categoría", "Valor", "Responsable", "Medio", "Estado", "Notas"],
    "Presupuestos": ["Mes", "Categoría", "Límite"],
    "Comprobantes": ["ID", "Fecha", "Movimiento_ID", "Concepto", "Valor", "Enlace", "Tipo"],
}
CATEGORIES = {
    "Ingreso": ["Ventas", "Servicios", "Recaudos", "Otros ingresos"],
    "Gasto": ["Arriendo", "Nómina", "Inventario", "Transporte", "Servicios públicos", "Marketing", "Alimentación", "Impuestos", "Otros gastos"],
}
PAYMENT_METHODS = ["Efectivo", "Transferencia", "Tarjeta", "Nequi/Daviplata", "Otro"]
STATES = ["Pagado/recibido", "Pendiente"]


def init_workbook():
    """Crea un libro vacío con las hojas esperadas si no existe."""
    if not os.path.exists(DATA_FILE):
        with pd.ExcelWriter(DATA_FILE, engine="openpyxl") as writer:
            for sheet, columns in SHEETS.items():
                pd.DataFrame(columns=columns).to_excel(writer, sheet_name=sheet, index=False)


def read_workbook():
    init_workbook()
    result = {}
    try:
        xls = pd.ExcelFile(DATA_FILE)
        for sheet, columns in SHEETS.items():
            if sheet in xls.sheet_names:
                frame = pd.read_excel(xls, sheet_name=sheet)
            else:
                frame = pd.DataFrame(columns=columns)
            for col in columns:
                if col not in frame.columns:
                    frame[col] = None
            result[sheet] = frame[columns]
    except Exception as exc:
        st.error(f"No se pudo leer el archivo de datos: {exc}")
        st.stop()
    return result


def save_workbook(data):
    """Guarda las hojas sin usar caché para que los cambios aparezcan al recargar."""
    with pd.ExcelWriter(DATA_FILE, engine="openpyxl") as writer:
        for sheet, columns in SHEETS.items():
            frame = data.get(sheet, pd.DataFrame(columns=columns)).copy()
            for col in columns:
                if col not in frame.columns:
                    frame[col] = None
            frame[columns].to_excel(writer, sheet_name=sheet, index=False)


def money(value):
    try:
        return f"${float(value or 0):,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return "$0"


def num_series(frame, col="Valor"):
    if frame.empty or col not in frame.columns:
        return pd.Series(dtype="float64")
    return pd.to_numeric(frame[col], errors="coerce").fillna(0)


def normalized_movements(frame):
    if frame.empty:
        return frame.copy()
    frame = frame.copy()
    frame["Fecha"] = pd.to_datetime(frame["Fecha"], errors="coerce")
    frame["Valor"] = pd.to_numeric(frame["Valor"], errors="coerce").fillna(0)
    frame["Tipo"] = frame["Tipo"].fillna("Gasto")
    frame["Categoría"] = frame["Categoría"].fillna("Sin categoría")
    frame["Estado"] = frame["Estado"].fillna("Pagado/recibido")
    return frame


def add_movement(data, values):
    row = {**values, "ID": str(uuid.uuid4())[:8].upper()}
    data["Movimientos"] = pd.concat(
        [data["Movimientos"], pd.DataFrame([row])], ignore_index=True
    )
    save_workbook(data)


def create_qr(payload):
    qr = qrcode.QRCode(version=1, box_size=8, border=3)
    qr.add_data(payload)
    qr.make(fit=True)
    image = qr.make_image(fill_color="#14213d", back_color="white")
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def export_excel(data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for sheet, columns in SHEETS.items():
            frame = data.get(sheet, pd.DataFrame(columns=columns)).copy()
            for col in columns:
                if col not in frame.columns:
                    frame[col] = None
            frame[columns].to_excel(writer, sheet_name=sheet, index=False)
    return output.getvalue()


# ------------------------------------------------------------
# Diseño visual
# ------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background: #f5f7fb; }
    [data-testid="stSidebar"] { background: #101a2c; }
    [data-testid="stSidebar"] * { color: #eef3ff; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #c5d0e5; }
    .brand { font-family: 'Manrope', sans-serif; font-size: 1.45rem; font-weight: 800; letter-spacing: -0.04em; color: #fff; }
    .brand span { color: #65e0bd; }
    .eyebrow { color: #62718a; text-transform: uppercase; letter-spacing: .12em; font-size: .72rem; font-weight: 700; }
    .hero { background: linear-gradient(125deg, #15243d 0%, #233e61 100%); padding: 1.7rem 1.8rem; border-radius: 22px; color: white; margin: .2rem 0 1.1rem 0; box-shadow: 0 12px 30px rgba(25,43,72,.12); }
    .hero h1 { color: white; font-family: 'Manrope', sans-serif; font-size: 2rem; line-height: 1.15; margin: .35rem 0 .55rem 0; }
    .hero p { color: #d7e3f4; margin-bottom: 0; max-width: 720px; }
    .metric-card { background: white; border: 1px solid #e7ebf3; border-radius: 17px; padding: 1rem 1.1rem; min-height: 120px; box-shadow: 0 4px 14px rgba(32,54,88,.035); }
    .metric-label { color: #718098; font-size: .83rem; font-weight: 600; }
    .metric-value { color: #17243a; font-family: 'Manrope', sans-serif; font-size: 1.65rem; font-weight: 800; letter-spacing: -.04em; margin-top: .4rem; }
    .metric-foot { color: #8591a5; font-size: .76rem; margin-top: .15rem; }
    .section-title { color: #17243a; font-family: 'Manrope', sans-serif; font-size: 1.25rem; font-weight: 800; letter-spacing: -.03em; margin: .25rem 0 .8rem 0; }
    .info-card { background: white; border: 1px solid #e7ebf3; border-radius: 16px; padding: 1.1rem 1.2rem; }
    .positive { color: #07875d; } .negative { color: #c43d54; }
    div.stButton > button, div.stDownloadButton > button { border-radius: 10px; font-weight: 700; min-height: 2.65rem; }
    div[data-testid="stForm"] { background: white; border: 1px solid #e7ebf3; border-radius: 16px; padding: 1.15rem; }
    [data-testid="stDataFrame"] { border: 1px solid #e7ebf3; border-radius: 12px; overflow: hidden; }
    .small-muted { color: #748198; font-size: .85rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

data = read_workbook()
movements = normalized_movements(data["Movimientos"])
if not movements.empty:
    movements["Mes"] = movements["Fecha"].dt.to_period("M").astype(str)

# Sidebar
with st.sidebar:
    st.markdown('<div class="brand">nexo<span>.</span></div>', unsafe_allow_html=True)
    st.caption("CONTROL FINANCIERO SIMPLE")
    st.markdown("---")
    page = st.radio(
        "MENÚ PRINCIPAL",
        ["🏠  Resumen", "➕  Nuevo movimiento", "📚  Movimientos", "🎯  Presupuestos", "🧾  Comprobantes", "📈  Informes"],
        label_visibility="visible",
    )
    st.markdown("---")
    st.markdown("**Tu negocio, más claro.**")
    st.caption("Registra, entiende y decide.")
    st.markdown("---")
    st.caption("Prototipo local · Datos en Excel")
    st.caption("Conecta Firebase para persistencia en producción.")

# Header helper
def page_header(kicker, title, description):
    st.markdown(f'<div class="eyebrow">{kicker}</div><div class="section-title" style="font-size:1.8rem;margin-top:.25rem">{title}</div><p class="small-muted">{description}</p>', unsafe_allow_html=True)


def metric(col, label, value, foot, icon=""):
    with col:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">{icon} {label}</div>'
            f'<div class="metric-value">{value}</div><div class="metric-foot">{foot}</div></div>',
            unsafe_allow_html=True,
        )


# ------------------------------------------------------------
# Resumen
# ------------------------------------------------------------
if page == "🏠  Resumen":
    today = pd.Timestamp(date.today())
    month_start = today.replace(day=1)
    this_month = movements[movements["Fecha"].between(month_start, today)] if not movements.empty else movements
    incomes = movements[(movements["Tipo"] == "Ingreso") & (movements["Estado"] != "Pendiente")] if not movements.empty else movements
    expenses = movements[(movements["Tipo"] == "Gasto") & (movements["Estado"] != "Pendiente")] if not movements.empty else movements
    total_income = num_series(incomes).sum()
    total_expense = num_series(expenses).sum()
    net = total_income - total_expense
    pending = movements[movements["Estado"] == "Pendiente"] if not movements.empty else movements
    pending_value = num_series(pending).sum()

    st.markdown(
        '<div class="hero"><div style="color:#8ee9d0;font-weight:700;font-size:.76rem;letter-spacing:.13em">TU NEGOCIO, EN CLARO</div>'
        '<h1>Las finanzas no tienen<br>por qué ser complicadas.</h1>'
        '<p>Todo lo importante de tu negocio en un solo lugar. Registra tus movimientos, revisa tu dinero y decide con más tranquilidad.</p></div>',
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    metric(c1, "Ingresos recibidos", money(total_income), "Total de movimientos recibidos", "↗")
    metric(c2, "Gastos pagados", money(total_expense), "Total de gastos pagados", "↘")
    metric(c3, "Resultado neto", money(net), "Ingresos menos gastos pagados", "◈")
    metric(c4, "Pendiente", money(pending_value), "Movimientos aún por completar", "◷")

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([1.35, 1], gap="large")
    with left:
        st.markdown('<div class="section-title">Movimiento del dinero</div>', unsafe_allow_html=True)
        if not movements.empty:
            chart = movements[movements["Estado"] != "Pendiente"].copy()
            chart["Mes"] = chart["Fecha"].dt.to_period("M").astype(str)
            chart = chart.groupby(["Mes", "Tipo"])["Valor"].sum().unstack(fill_value=0)
            chart = chart.sort_index().tail(6)
            st.line_chart(chart, use_container_width=True)
        else:
            st.markdown('<div class="info-card"><b>Tu primer paso empieza aquí.</b><p class="small-muted">Cuando registres ingresos y gastos, aquí verás cómo se mueve el dinero mes a mes.</p></div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="section-title">Últimos movimientos</div>', unsafe_allow_html=True)
        if not movements.empty:
            recent = movements.sort_values("Fecha", ascending=False).head(6)
            show = recent[["Fecha", "Tipo", "Concepto", "Valor", "Estado"]].copy()
            show["Fecha"] = show["Fecha"].dt.strftime("%d/%m/%Y")
            show["Valor"] = show["Valor"].apply(money)
            st.dataframe(show, use_container_width=True, hide_index=True)
        else:
            st.info("Todavía no hay movimientos. Registra el primero desde “Nuevo movimiento”.")
        st.markdown('<div class="info-card"><b>Consejo rápido</b><p class="small-muted">Registra también los pagos pendientes para que no se te escape ninguna obligación o cobro.</p></div>', unsafe_allow_html=True)

# ------------------------------------------------------------
# Nuevo movimiento
# ------------------------------------------------------------
elif page == "➕  Nuevo movimiento":
    page_header("REGISTRO RÁPIDO", "Nuevo movimiento", "Registra un ingreso o gasto en pocos pasos. Solo pedimos lo necesario.")
    with st.form("new_movement", clear_on_submit=True):
        kind = st.segmented_control("¿Qué quieres registrar?", ["Ingreso", "Gasto"], default="Ingreso")
        c1, c2 = st.columns(2)
        with c1:
            concept = st.text_input("Concepto *", placeholder="Ej. Venta del día, arriendo, cliente...")
            amount = st.number_input("Valor en pesos colombianos *", min_value=0, value=0, step=10000)
            movement_date = st.date_input("Fecha", value=date.today())
            category = st.selectbox("Categoría", CATEGORIES[kind], key=f"cat_{kind}")
        with c2:
            responsible = st.text_input("Responsable", placeholder="Nombre de quien registra")
            method = st.selectbox("Medio de pago", PAYMENT_METHODS)
            state = st.selectbox("Estado", STATES)
            notes = st.text_area("Nota (opcional)", placeholder="Un detalle útil para recordar...")
        submitted = st.form_submit_button("Guardar movimiento", type="primary", use_container_width=True)
        if submitted:
            if not concept.strip():
                st.error("Escribe un concepto para identificar el movimiento.")
            elif amount <= 0:
                st.error("El valor debe ser mayor que cero.")
            else:
                add_movement(data, {
                    "Fecha": movement_date.isoformat(),
                    "Tipo": kind,
                    "Concepto": concept.strip(),
                    "Categoría": category,
                    "Valor": float(amount),
                    "Responsable": responsible.strip(),
                    "Medio": method,
                    "Estado": state,
                    "Notas": notes.strip(),
                })
                st.success(f"{kind} guardado correctamente.")
                st.rerun()
    st.caption("* Campos obligatorios. Los movimientos se guardan en el archivo Excel de esta versión.")

# ------------------------------------------------------------
# Movimientos
# ------------------------------------------------------------
elif page == "📚  Movimientos":
    page_header("HISTORIAL", "Movimientos", "Busca, filtra y exporta tus ingresos y gastos.")
    if movements.empty:
        st.info("Aún no hay movimientos registrados.")
    else:
        f1, f2, f3 = st.columns([1, 1, 1.5])
        with f1:
            kind_filter = st.selectbox("Tipo", ["Todos", "Ingreso", "Gasto"])
        with f2:
            state_filter = st.selectbox("Estado", ["Todos"] + STATES)
        with f3:
            query = st.text_input("Buscar", placeholder="Concepto, categoría o responsable")
        filtered = movements.copy()
        if kind_filter != "Todos":
            filtered = filtered[filtered["Tipo"] == kind_filter]
        if state_filter != "Todos":
            filtered = filtered[filtered["Estado"] == state_filter]
        if query.strip():
            pattern = query.strip().lower()
            cols = ["Concepto", "Categoría", "Responsable", "Notas"]
            mask = filtered[cols].fillna("").astype(str).apply(lambda col: col.str.lower().str.contains(pattern, regex=False)).any(axis=1)
            filtered = filtered[mask]
        display = filtered.drop(columns=["Mes"], errors="ignore").copy()
        display["Fecha"] = display["Fecha"].dt.strftime("%d/%m/%Y")
        display["Valor"] = display["Valor"].apply(money)
        st.dataframe(display, use_container_width=True, hide_index=True)
        st.caption(f"{len(filtered)} movimiento(s) encontrado(s).")
        csv_bytes = filtered.drop(columns=["Mes"], errors="ignore").to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇ Descargar resultados en CSV", csv_bytes, "movimientos.csv", "text/csv")

# ------------------------------------------------------------
# Presupuestos
# ------------------------------------------------------------
elif page == "🎯  Presupuestos":
    page_header("PLANIFICACIÓN", "Presupuestos", "Define límites de gasto por categoría y compara lo planeado con lo gastado.")
    month_value = date.today().strftime("%Y-%m")
    with st.form("budget_form", clear_on_submit=True):
        b1, b2, b3 = st.columns(3)
        with b1:
            budget_month = st.text_input("Mes (AAAA-MM)", value=month_value)
        with b2:
            budget_category = st.selectbox("Categoría", CATEGORIES["Gasto"])
        with b3:
            limit_value = st.number_input("Límite de gasto ($)", min_value=0, value=0, step=50000)
        save_budget = st.form_submit_button("Guardar presupuesto", type="primary")
        if save_budget:
            try:
                pd.Period(budget_month, freq="M")
                if limit_value <= 0:
                    st.error("El límite debe ser mayor que cero.")
                else:
                    budget_row = pd.DataFrame([{"Mes": budget_month, "Categoría": budget_category, "Límite": float(limit_value)}])
                    old = data["Presupuestos"]
                    old = old[~((old["Mes"].astype(str) == budget_month) & (old["Categoría"].astype(str) == budget_category))]
                    data["Presupuestos"] = pd.concat([old, budget_row], ignore_index=True)
                    save_workbook(data)
                    st.success("Presupuesto guardado.")
                    st.rerun()
            except Exception:
                st.error("Usa el formato de mes AAAA-MM, por ejemplo 2026-10.")
    budgets = data["Presupuestos"].copy()
    if budgets.empty:
        st.info("Todavía no tienes presupuestos. Crea uno arriba para empezar a controlar tus gastos.")
    else:
        month_choice = st.selectbox("Ver mes", sorted(budgets["Mes"].dropna().astype(str).unique(), reverse=True))
        month_budgets = budgets[budgets["Mes"].astype(str) == month_choice].copy()
        month_expenses = movements[(movements["Tipo"] == "Gasto") & (movements["Estado"] != "Pendiente") & (movements["Fecha"].dt.strftime("%Y-%m") == month_choice)] if not movements.empty else movements
        spent = month_expenses.groupby("Categoría")["Valor"].sum().to_dict() if not month_expenses.empty else {}
        for _, row in month_budgets.iterrows():
            cat = str(row["Categoría"])
            limit_amt = float(pd.to_numeric(row["Límite"], errors="coerce") or 0)
            spent_amt = float(spent.get(cat, 0))
            ratio = spent_amt / limit_amt if limit_amt else 0
            st.markdown(f"**{cat}** — {money(spent_amt)} de {money(limit_amt)}")
            st.progress(min(max(ratio, 0.0), 1.0))
            if ratio >= 1:
                st.error(f"Superaste el presupuesto de {cat}." if ratio > 1 else f"Alcanzaste el límite de {cat}.")
            elif ratio >= .8:
                st.warning(f"Ya usaste {ratio:.0%} del presupuesto.")
            else:
                st.caption(f"Disponible: {money(limit_amt - spent_amt)}")

# ------------------------------------------------------------
# Comprobantes
# ------------------------------------------------------------
elif page == "🧾  Comprobantes":
    page_header("SOPORTES", "Comprobantes y códigos QR", "Guarda enlaces a soportes y genera un QR que abre el enlace.")
    with st.form("receipt_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            receipt_concept = st.text_input("Concepto *", placeholder="Ej. Factura de proveedor")
            receipt_amount = st.number_input("Valor ($)", min_value=0, value=0, step=10000)
            receipt_date = st.date_input("Fecha del comprobante", value=date.today())
        with c2:
            receipt_type = st.selectbox("Tipo", ["Ingreso", "Gasto"])
            receipt_url = st.text_input("Enlace al archivo", placeholder="https://...")
        receipt_submit = st.form_submit_button("Guardar comprobante y generar QR", type="primary")
        if receipt_submit:
            if not receipt_concept.strip():
                st.error("Escribe un concepto.")
            elif not receipt_url.strip().startswith(("https://", "http://")):
                st.error("Ingresa un enlace válido que comience con http:// o https://.")
            else:
                receipt_id = "REC-" + str(uuid.uuid4())[:8].upper()
                new_receipt = pd.DataFrame([{
                    "ID": receipt_id,
                    "Fecha": receipt_date.isoformat(),
                    "Movimiento_ID": "",
                    "Concepto": receipt_concept.strip(),
                    "Valor": float(receipt_amount),
                    "Enlace": receipt_url.strip(),
                    "Tipo": receipt_type,
                }])
                data["Comprobantes"] = pd.concat([data["Comprobantes"], new_receipt], ignore_index=True)
                save_workbook(data)
                st.session_state["last_qr"] = create_qr(receipt_url.strip())
                st.session_state["last_qr_id"] = receipt_id
                st.session_state["last_qr_concept"] = receipt_concept.strip()
                st.success(f"Comprobante {receipt_id} guardado.")
    if "last_qr" in st.session_state:
        st.image(st.session_state["last_qr"], caption=f"QR: {st.session_state['last_qr_id']} · {st.session_state['last_qr_concept']}", width=210)
        st.download_button("Descargar código QR", st.session_state["last_qr"], "comprobante_qr.png", "image/png")
    receipts = data["Comprobantes"]
    if not receipts.empty:
        st.markdown('<div class="section-title">Comprobantes guardados</div>', unsafe_allow_html=True)
        st.dataframe(receipts, use_container_width=True, hide_index=True)

# ------------------------------------------------------------
# Informes
# ------------------------------------------------------------
elif page == "📈  Informes":
    page_header("ANÁLISIS", "Informes financieros", "Filtra un periodo y descarga los datos para compartirlos o analizarlos.")
    if movements.empty:
        st.info("Registra movimientos para generar informes.")
    else:
        min_date = movements["Fecha"].min().date()
        max_date = movements["Fecha"].max().date()
        c1, c2 = st.columns(2)
        with c1:
            start_date = st.date_input("Desde", value=min_date)
        with c2:
            end_date = st.date_input("Hasta", value=max_date)
        if start_date > end_date:
            st.error("La fecha inicial debe ser anterior o igual a la fecha final.")
        else:
            period = movements[(movements["Fecha"].dt.date >= start_date) & (movements["Fecha"].dt.date <= end_date)]
            received = period[(period["Tipo"] == "Ingreso") & (period["Estado"] != "Pendiente")]["Valor"].sum()
            paid = period[(period["Tipo"] == "Gasto") & (period["Estado"] != "Pendiente")]["Valor"].sum()
            outstanding = period[period["Estado"] == "Pendiente"]["Valor"].sum()
            c1, c2, c3 = st.columns(3)
            metric(c1, "Ingresos recibidos", money(received), "En el periodo seleccionado")
            metric(c2, "Gastos pagados", money(paid), "En el periodo seleccionado")
            metric(c3, "Resultado", money(received-paid), "Ingresos menos gastos pagados")
            st.markdown("<br>", unsafe_allow_html=True)
            category_expenses = period[(period["Tipo"] == "Gasto") & (period["Estado"] != "Pendiente")].groupby("Categoría")["Valor"].sum().sort_values(ascending=False)
            if not category_expenses.empty:
                st.markdown('<div class="section-title">Gastos por categoría</div>', unsafe_allow_html=True)
                st.bar_chart(category_expenses)
            monthly = period.copy()
            monthly["Mes"] = monthly["Fecha"].dt.to_period("M").astype(str)
            pivot = monthly[monthly["Estado"] != "Pendiente"].groupby(["Mes", "Tipo"])["Valor"].sum().unstack(fill_value=0)
            if not pivot.empty:
                st.markdown('<div class="section-title">Ingresos y gastos por mes</div>', unsafe_allow_html=True)
                st.bar_chart(pivot)
            st.download_button("⬇ Descargar Excel completo", export_excel(data), "nexo_finanzas_datos.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.markdown("---")
st.markdown('<p class="small-muted" style="text-align:center">nexo · Control financiero simple · Versión de mejora inicial</p>', unsafe_allow_html=True)
