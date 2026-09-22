# AI Pronunciation Coach

A full-stack pronunciation coaching app that listens to you speak, transcribes it with Whisper, scores your pronunciation, and tells you specifically what to fix - not just a number, but feedback like "keep vowel timing even" or "focus on pitch consistency." It supports seven languages: German, French, Spanish, Portuguese, Russian, Japanese, and Chinese.

## Live Demo

**Frontend (Streamlit):** https://ai-pronunciation-mlops-4ejy6jjuq74jj6zecjtbnf.streamlit.app/
**Backend API (FastAPI):** https://ai-pronunciation-mlops.onrender.com/docs

> Use Chrome and allow microphone access for real-time recording.

## Application Interface

**Main frontend** - pick a target language, generate practice sentences, record yourself, and get an instant transcript and score.

![Frontend](docs/frontend.png)

**Waveform + feedback** - every recording gets a waveform visualization alongside transcript-aware phoneme feedback, not just a pass/fail score.

![Waveform](docs/waveform.png)

**Progress tracking** - scores are logged over time so improvement is visible across sessions, not just per-attempt.

![Analytics](docs/analytics.png)

## Why the Whisper API, not local Whisper

Early versions ran Whisper locally via torch. That worked fine on my machine, but it made the Docker image too large and too memory-hungry to deploy reliably on Render's free tier - builds were slow and the container kept failing to start under memory pressure. I switched to OpenAI's hosted Whisper API instead: smaller image, faster cold starts, and one less heavyweight dependency to manage. The tradeoff is a per-request API cost instead of free local inference, which is the right call for a demo app but wouldn't necessarily be for a high-volume production service.

## Tech Stack

**Frontend:** Streamlit, streamlit-mic-recorder
**Backend:** FastAPI, Uvicorn, Docker, Render
**AI/ML:** OpenAI Whisper API (transcription), OpenAI GPT-4o-mini (pronunciation feedback), NumPy, SciPy, pandas
**Analytics:** Text-similarity pronunciation scoring, feature logging, score-trend tracking

## Architecture

```text
Streamlit Frontend
     |
     v
FastAPI Backend
     |
     v
Whisper Transcription API
     |
     v
Pronunciation Analysis + Feedback
     |
     v
Analytics + Feature Store
```

## Quick Start (Local)

**1. Clone the repository**
```bash
git clone https://github.com/geotheleo/ai-pronunciation-mlops.git
cd ai-pronunciation-mlops
```

**2. Create a virtual environment**
```bash
python -m venv venv
venv\Scripts\activate
```
(macOS/Linux: `source venv/bin/activate`)

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Create a `.env` file:
```
OPENAI_API_KEY=your_openai_api_key
API_BASE=https://ai-pronunciation-mlops.onrender.com
```

**5. Run the backend and frontend**
```bash
uvicorn app.main:app --reload
streamlit run app_streamlit.py
```

## API Endpoints

- **POST /analyze** - analyzes uploaded speech audio (with an optional `target_text` field for guided practice sentences); returns the transcript, a pronunciation score (text-similarity against `target_text`, `null` for free practice where there's nothing to score against), and AI-generated feedback with phoneme-level tips.
- **POST /generate-practice** - generates multilingual practice sentences with phonetic guidance.
- **GET /analytics** - returns stored pronunciation score history for progress visualization.

## Evaluation

Here's a real session: the German phrase "Guten Morgen, wie geht es Ihnen?" transcribed by Whisper, scored 0.85 on text-similarity against a deliberately imperfect attempt, with GPT-4o-mini feedback noting "Great effort! You captured most of the phrase well, but pay attention to the pronunciation of 'geht' and 'Ihnen'" alongside phoneme-level tips on the German "g" and final "n" sounds. The score is a text-similarity proxy (transcript vs. target phrase) - mispronunciations tend to surface as transcription mismatches with a strong ASR model like Whisper - not acoustic phoneme alignment, so treat it as an approximation, not a lab-grade pronunciation metric.

Formal evaluation against a labeled pronunciation dataset (rather than spot-checked sessions) is a natural next step, not yet done.

## Deployment

- **Frontend:** Streamlit Community Cloud
- **Backend:** Render, Dockerized FastAPI service
- CORS-enabled API, environment-variable configuration, separated frontend/backend so each can scale or redeploy independently.

## Future Improvements

- Real phoneme alignment (acoustic model, beyond text-similarity)
- PostgreSQL-backed feature store (currently file-based)
- User authentication and per-user history
- CI/CD pipeline and automated retraining jobs
- Adaptive difficulty based on session history

## License

MIT License

## Author

GeoTheLeo - Geo Smith
