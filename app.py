import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os

from dotenv import load_dotenv

load_dotenv()

# ---------- CONFIGURATION ----------
API_URL = f"{os.getenv('API_BASEURL')}/chat"

st.set_page_config(
    page_title=os.getenv("APP_NAME", "Data Analyst Assistant"),
    page_icon="💬",
    layout="wide",
)

# ---------- HEADER ----------
st.title(os.getenv("APP_NAME", "Data Analyst Assistant"))
st.caption("Ask your database anything — in plain English!")

st.markdown(
    """
    <style>
    .sql-box {
        background-color: #f8f9fa;
        color: black;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0px;
        font-family: monospace;
        font-size: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- INPUT ----------
user_query = st.text_input("💬 Type your query:", placeholder="e.g., Show total fees collected per class")

col1, col2 = st.columns([1, 6])
with col1:
    ask_button = st.button("Ask", use_container_width=True)
with col2:
    clear_button = st.button("Clear Chat", use_container_width=True)

# Maintain session chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if clear_button:
    st.session_state.chat_history = []
    st.rerun()

# ---------- PROCESS QUERY ----------
if ask_button and user_query.strip():
    with st.spinner("🤖 Thinking..."):
        try:
            res = requests.post(API_URL, json={"query": user_query})
            if res.status_code != 200:
                st.error("Backend error. Please check FastAPI server.")
            else:
                data = res.json()
                sql = data.get("sql", "")
                rows = data.get("data", [])

                st.session_state.chat_history.append(
                    {"query": user_query, "sql": sql, "data": rows}
                )
        except Exception as e:
            st.error(f"⚠️ Unable to connect to API: {e}")

# ---------- DISPLAY RESULTS ----------
for chat in reversed(st.session_state.chat_history):
    with st.container():
        st.markdown(f"**🧑‍💼 You:** {chat['query']}")
        st.markdown("**🤖 Assistant:** Here's what I found:")

        # Show SQL Query
        with st.expander("🧠 Generated SQL Query"):
            st.markdown(f"<div class='sql-box'>{chat['sql']}</div>", unsafe_allow_html=True)

        # Display data
        rows = chat["data"]
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True)

            # ---------- AUTO CHART VISUALIZATION ----------
        numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
        categorical_cols = df.select_dtypes(include=["object"]).columns

        # Case 1: single numeric summary → metric
        if len(df.columns) == 1 and df[df.columns[0]].dtype in ["float64", "int64"]:
            total = df[df.columns[0]].sum()
            st.metric(label=f"💰 {df.columns[0].replace('_', ' ').title()}", value=f"₹{total:,.2f}")

        # Case 2: 1 categorical + 1 numeric → bar chart
        elif len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]
            st.markdown("### 📊 Visualization")
            fig = px.bar(df, x=cat_col, y=num_col, text_auto=True, color=cat_col)
            fig.update_layout(xaxis_title=cat_col.title(), yaxis_title=num_col.title(), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        # ✅ Case 3: 2 numeric columns → detect potential 'group vs value' pattern
        elif len(df.columns) == 2 and len(numeric_cols) == 2:
            group_col, value_col = df.columns
            # If group_col looks like month, year, day, id, etc., treat as X-axis
            if any(k in group_col.lower() for k in ["month", "year", "day", "id", "week"]):
                st.markdown("### 📈 Trend Over Time")
                fig = px.line(df, x=group_col, y=value_col, markers=True)
                fig.update_layout(xaxis_title=group_col.title(), yaxis_title=value_col.title())
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.markdown("### 📊 Numeric Comparison")
                fig = px.bar(df, x=group_col, y=value_col, text_auto=True)
                st.plotly_chart(fig, use_container_width=True)

        # Case 4: small categorical dataset → pie chart
        elif len(df) <= 10 and len(categorical_cols) == 1:
            cat_col = categorical_cols[0]
            st.markdown("### 🥧 Distribution")
            fig = px.pie(df, names=cat_col)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No matching records found.")

        st.markdown("---")

# ---------- FOOTER ----------
st.markdown(
    "<p style='text-align:center; color:grey;'>Built with ❤️ using Streamlit + FastAPI + OpenAI</p>",
    unsafe_allow_html=True,
)
