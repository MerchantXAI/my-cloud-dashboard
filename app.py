import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# 1. Page Configuration
st.set_page_config(page_title="Cloud Analytics AI", layout="wide")
st.title("📊 Cloud Business Analytics & AI Dashboard")
st.caption("0% local MacBook resources used | 100% Free Cloud Setup")

# 2. Get the Cloud AI Token Securely from Streamlit
HF_TOKEN = st.secrets.get("HF_TOKEN", "")
API_URL = "https://huggingface.co"

# 3. Generate Mock Business Data
@st.cache_data
def get_clean_data():
    data = {
        "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "Revenue": [45000, 52000, 49000, 61000, 58000, 71000, 75000, 68000, 82000, 89000, 94000, 115000],
        "Expenses": [32000, 34000, 35000, 40000, 38000, 42000, 45000, 41000, 48000, 51000, 55000, 62000],
        "New_Users": [120, 150, 140, 210, 190, 280, 310, 250, 390, 420, 480, 610]
    }
    df = pd.DataFrame(data)
    df["Net_Profit"] = df["Revenue"] - df["Expenses"]
    return df

df = get_clean_data()

# 4. Filter Dashboard Controls
st.sidebar.header("⚙️ Filter Options")
months = st.sidebar.multiselect("Pick Months:", options=df["Month"].tolist(), default=df["Month"].tolist())
filtered_df = df[df["Month"].isin(months)]

# 5. Core Metric KPI Cards
rev_total = filtered_df["Revenue"].sum()
prof_total = filtered_df["Net_Profit"].sum()
users_total = filtered_df["New_Users"].sum()
margin = (prof_total / rev_total) * 100 if rev_total > 0 else 0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("💰 Total Revenue", f"${rev_total:,}")
kpi2.metric("📈 Net Profit", f"${prof_total:,}")
kpi3.metric("👥 New Users", f"{users_total:,}")
kpi4.metric("📊 Profit Margin", f"{margin:.1f}%")

st.markdown("---")

# 6. Charts & Graphs
left_chart, right_chart = st.columns(2)

with left_chart:
    st.subheader("Financial Performance")
    fig_line = px.line(filtered_df, x="Month", y=["Revenue", "Expenses", "Net_Profit"], markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

with right_chart:
    st.subheader("User Acquisition")
    fig_bar = px.bar(filtered_df, x="Month", y="New_Users", color="New_Users")
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# 7. AI Analysis Block
st.subheader("🤖 AI Data Analyst")
user_input = st.text_input("Ask the AI to evaluate this performance or build a strategy:", 
                          placeholder="e.g., How can I reduce expenses next quarter?")

context = f"Data overview: Revenue is ${rev_total}, Profit is ${prof_total}, Margin is {margin:.1f}%."

if st.button("Run AI Analysis"):
    if not HF_TOKEN:
        st.error("Missing AI Key! Please paste your token in Streamlit Advanced Settings.")
    elif user_input:
        with st.spinner("Cloud AI processing your dashboard numbers..."):
            headers = {"Authorization": f"Bearer {HF_TOKEN}"}
            payload = {
                "inputs": f"Context: {context} Question: {user_input} Strategy Response:",
                "parameters": {"max_new_tokens": 200}
            }
            try:
                res = requests.post(API_URL, headers=headers, json=payload)
                if res.status_code == 200:
                    output = res.json()
                    st.info("💡 Strategic Suggestion:")
                    if isinstance(output, list) and len(output) > 0:
                        st.write(output[0].get('generated_text', 'No answer.'))
                    else:
                        st.write(output.get('generated_text', str(output)))
                else:
                    st.error("Server is waking up or busy. Click the button again in 10 seconds.")
            except Exception as e:
                st.error(f"Network issue: {e}")
