import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Backend URL
backend_url = "http://localhost:8000"

st.set_page_config(page_title="Solar Forecast", layout="wide")
st.title("🔆 Solar Power Forecasting Dashboard")


# -----------------------------------------------------
# FORECAST SECTION
# -----------------------------------------------------
st.subheader("📊 Forecast Generation")

days = st.slider("Select forecast range (days):", 1, 90, 7)

# Generate Forecast
col_gen, col_reset = st.columns([1, 0.15])

# Generate Forecast Button (left side)
with col_gen:
    if st.button("Generate Forecast"):
        try:
            response = requests.post(f"{backend_url}/forecast", params={"days": days})
            forecast_df = pd.DataFrame(response.json())

            # Save forecast
            st.session_state["forecast_data"] = forecast_df

            st.success("Forecast generated successfully!")
        except Exception as e:
            st.error("❌ Unable to connect to backend")
            st.exception(e)

# Reset Forecast Button (right side)
with col_reset:
    if st.button("Reset Forecast"):
        st.session_state.pop("forecast_data", None)
        st.success("Forecast cleared!")
        st.rerun()

# Always display forecast if stored
if "forecast_data" in st.session_state:
    forecast_df = st.session_state["forecast_data"]

    st.subheader("📈 Solar Power Forecast Graph")
    fig = px.line(forecast_df, x="ds", y="yhat", title="Predicted Solar Power Output")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📄 Forecast Table (Last 10 Rows)")
    st.dataframe(forecast_df.tail(10))


# -----------------------------------------------------
# CHAT SECTION
# -----------------------------------------------------
st.markdown("---")
st.subheader("🤖 Chat With Solar AI Assistant")

if "history" not in st.session_state:
    st.session_state.history = []

user_msg = st.text_input(
    "Ask anything (forecasting, solar output, improvements, ROI, etc.)"
)

if st.button("Send"):
    if not user_msg.strip():
        st.warning("⚠ Please enter a question.")
    else:
        try:
            response = requests.post(
                f"{backend_url}/chat",
                json={"question": user_msg}
            )
            ai_answer = response.json()["answer"]

            st.session_state.history.append(("You", user_msg))
            st.session_state.history.append(("AI", ai_answer))

        except Exception as e:
            st.error("❌ Couldn't reach backend for chat")
            st.exception(e)


# Display Chat History
for sender, msg in st.session_state.history:
    if sender == "You":
        st.markdown(f"🧑 **You:** {msg}")
    else:
        st.markdown(f"🤖 **AI:** {msg}")
