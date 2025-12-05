# Solar Forecasting & AI Insights Dashboard

## Project Overview
A full-stack application that predicts solar power generation and provides AI-based insights for performance improvement. Users can forecast solar output for upcoming days, visualize results through an interactive dashboard, and chat with an AI assistant for analysis and recommendations.

## Features
- Solar power forecasting using Prophet model
- Interactive Plotly visualization
- AI assistant for forecast interpretation and improvement suggestions
- Chat history support
- Backend: FastAPI + Forecast model + Azure OpenAI
- Frontend: Streamlit dashboard
- Dockerized deployment to Azure Container Apps

## Folder Structure
```
Solar/
│
├── backend/
│   ├── app.py
│   ├── model.pkl
│   ├── requirements.txt
│   ├── .env
│
├── frontend/
│   ├── app.py
│   ├── requirements.txt
│   ├── .env
│
└── docker-compose.yml
```

## Environment Variables

### backend/.env
```
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
```

### frontend/.env
```
BACKEND_URL=http://localhost:8000
```

## Commands to Run Locally

### Backend
```
cd backend
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

### Frontend
```
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

## Docker

### Build
```
docker compose build
```

### Run
```
docker compose up
```

## Publish to Azure Container Registry (ACR)


## Deploy Backend to Azure Container Apps


## Deploy Frontend to Azure Container Apps


## Update Frontend Image Later


## Update Backend Image Later


## Live App URL

