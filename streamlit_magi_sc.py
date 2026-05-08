import os
import pandas as pd
import streamlit as st
from supabase import create_client, Client

st.set_page_config(page_title="Magi@SC", layout="wide")

def get_supabase() -> Client:
    url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
    key = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))
    if not url or not key:
        st.error("Defina SUPABASE_URL e SUPABASE_KEY em .streamlit/secrets.toml ou variáveis de ambiente.")
        st.stop()
    return create_client(url, key)

def fmt_money(v):
    try:
        return f"R$ {float(v or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"

supabase = get_supabase()

st.title("Magi@Solicitações de Compras")
st.caption("Rastreio de solicitações de compra.")

left, right = st.columns([7, 1], gap="large")

with left:
    st.subheader("Pendências")
    data = supabase.table("purchase_requests").select("*").order("created_at", desc=True).execute().data or []
    df = pd.DataFrame(data)

    if df.empty:
        st.info("Nenhuma solicitação cadastrada.")
    else:
        for col in ("valor_total",):
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Pendentes", int((df["status"] == "PENDENTE").sum()))
        c2.metric("Cotação", int((df["status"] == "COTACAO").sum()))
        c3.metric("Comprado", int((df["status"] == "COMPRADO").sum()))
        c4.metric("Valor aberto", fmt_money(df.loc[df["status"] != "COMPRADO", "valor_total"].sum()))

        q = st.text_input("Buscar")
        status_filter = st.selectbox("Status", ["", "PENDENTE", "COTACAO", "COMPRADO"])
        cont_filter = st.selectbox("Contingência", ["", "SIM", "NAO"])

        view = df.copy()
        if q:
            mask = (
                view["sc_number"].astype(str).str.contains(q, case=False, na=False)
                | view["cc"].astype(str).str.contains(q, case=False, na=False)
                | view["observation"].astype(str).str.contains(q, case=False, na=False)
            )
            view = view[mask]
        if status_filter:
            view = view[view["status"] == status_filter]
        if cont_filter == "SIM":
            view = view[view["contingencia"] == True]
        elif cont_filter == "NAO":
            view = view[view["contingencia"] != True]

        if view.empty:
            st.warning("Sem resultados com os filtros atuais.")
        else:
            display = view[["sc_number", "created_at", "cc", "observation", "valor_total", "contingencia", "status"]].copy()
            display.rename(columns={
                "sc_number": "SC",
                "created_at": "Criada em",
                "cc": "CC",
                "observation": "Observação",
                "valor_total": "Valor total",
                "contingencia": "Contingência",
                "status": "Status",
            }, inplace=True)
            st.dataframe(display, use_container_width=True, hide_index=True)
