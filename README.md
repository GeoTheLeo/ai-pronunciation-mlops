# 🎤 AI Pronunciation Coach (MLOps + GenAI)

A full-stack, production-style system for real-time pronunciation coaching with:
- 🎙️ microphone input + batch uploads
- 🧠 AI feedback + phoneme guidance
- 🌍 multi-language practice (EN/DE/ES/FR/RU/JP/ZH)
- 🔁 automated retraining (MLOps loop)
- 📊 experiment tracking (MLflow)
- 📈 analytics + waveform visualization

---

## 🚀 Live Demo

- **Frontend (Streamlit):** [AI Pronunciation Coach Frontend] (https://ai-pronunciation-mlops-4ejy6jjuq74jj6zecjtbnf.streamlit.app/  
- **Backend (FastAPI):** https://ai-pronunciation-mlops.onrender.com  

> _Tip: Use Chrome and allow microphone access._

---

## 🎥 Demo

<!-- Replace with your GIF/screenshot -->
![demo](docs/demo.gif)

---

## 🧰 Tech Stack

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![MLflow](https://img.shields.io/badge/MLflow-Tracking-blue)
![scikit-learn](https://img.shields.io/badge/Scikit--learn-Model-orange)

- **Frontend:** Streamlit
- **Backend:** FastAPI + Uvicorn
- **Modeling:** scikit-learn
- **Tracking:** MLflow
- **Audio:** streamlit-mic-recorder, NumPy, SciPy
- **Orchestration:** simple retraining trigger (data-driven)

---

## ⚡ Quick Start (Local)

### 1) Clone & install
```bash
git clone https://github.com/geotheleo/ai-pronunciation-mlops.git
cd ai-pronunciation-mlops
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt