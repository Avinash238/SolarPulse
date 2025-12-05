from fastapi import FastAPI
import joblib
import pandas as pd
from pydantic import BaseModel
from openai import AzureOpenAI

app = FastAPI()

# ----------------------
# Load forecasting model
# ----------------------
model = joblib.load("model.pkl")

from dotenv import load_dotenv
import os
load_dotenv()
# ----------------------
# Configure Azure OpenAI
# ----------------------
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version="2024-12-01-preview"
)

DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")
# ----------------------
# Store forecast in memory
# ----------------------
stored_forecast = None   # <--- important


# ----------------------
# Default regressor values
# ----------------------
median_values = {
    "temperature": -15,
    "humidity": 0.001,
    "irradiance_ground": 50,
    "irradiance_atmos": 150
}


# ----------------------
# FORECAST ENDPOINT
# ----------------------
@app.post("/forecast")
def forecast(days: int = 7):
    global stored_forecast

    future = model.make_future_dataframe(periods=24 * days, freq="H")
    for col, val in median_values.items():
        if col not in future.columns:
            future[col] = val

    result = model.predict(future)
    result = result[["ds", "yhat"]].tail(24 * days)
    result["ds"] = result["ds"].astype(str)
    result["yhat"] = result["yhat"].astype(float)

    stored_forecast = result.to_dict(orient="records")  # 🔥 Save forecast
    return stored_forecast


# ----------------------
# CHAT ENDPOINT
# ----------------------
class ChatInput(BaseModel):
    question: str


@app.post("/chat")
def chat(data: ChatInput):
    global stored_forecast
    question = data.question

    # Use stored forecast if available
    if stored_forecast:
        df = pd.DataFrame(stored_forecast)
        peak_time = df.loc[df["yhat"].idxmax(), "ds"]
        peak_value = df["yhat"].max()
        avg_value = df["yhat"].mean()
        min_value = df["yhat"].min()

        forecast_summary = (
            f"Forecast period: {df['ds'].iloc[0]} → {df['ds'].iloc[-1]}\n"
            f"Average predicted generation: {avg_value:.2f}\n"
            f"Peak generation: {peak_value:.2f} at {peak_time}\n"
            f"Minimum generation: {min_value:.2f}"
        )
    else:
        forecast_summary = "No forecast has been generated yet."


    prompt = f"""
You are SOLAR_AI — expert in solar forecasting and PV engineering.

FORECAST SUMMARY:
{forecast_summary}

USER QUESTION:
{question}

Guidelines:
- If forecast exists → analyze peak, dips, trends and provide insights.
- Include technical causes (temperature, irradiance, shading, etc.)
- Provide practical actions to boost solar energy generation.
- If no forecast exists → answer normally as an AI assistant.
- Use simple, clean language and bullet points.
"""


    # Call Azure AI
    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
        return {"answer": answer}

    # Fallback AI (no crash even if Azure is down)
    except Exception as e:
        fallback = (
            f"⚠️ AI unavailable.\n\n"
            f"Forecast summary:\n{forecast_summary}\n\n"
            f"You asked: {question}\n"
            f"General advice: clean panels, check shading, schedule heavy loads during peak hours."
        )
        return {"answer": fallback}
