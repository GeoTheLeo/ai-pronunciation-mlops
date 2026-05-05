import React, { useState, useEffect, useRef } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer
} from "recharts";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [recording, setRecording] = useState(false);
  const [practiceText, setPracticeText] = useState(null);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // -----------------------------
  // FETCH ANALYTICS
  // -----------------------------
  const fetchAnalytics = async () => {
    const res = await fetch("http://localhost:8000/analytics");
    const data = await res.json();
    setAnalytics(data);
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  // -----------------------------
  // RECORD AUDIO
  // -----------------------------
  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorderRef.current = mediaRecorder;
    audioChunksRef.current = [];

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) audioChunksRef.current.push(e.data);
    };

    mediaRecorder.onstop = () => {
      const blob = new Blob(audioChunksRef.current, { type: "audio/webm" });
      const audioFile = new File([blob], "recording.webm");
      setFile(audioFile);
    };

    mediaRecorder.start();
    setRecording(true);
    setResult(null);
  };

  const stopRecording = () => {
    mediaRecorderRef.current.stop();
    setRecording(false);
  };

  // -----------------------------
  // ANALYZE
  // -----------------------------
  const analyze = async () => {
    if (!file) return alert("Record audio first.");

    const formData = new FormData();
    formData.append("audio", file);

    const res = await fetch("http://localhost:8000/analyze", {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    setResult(data);
    fetchAnalytics();
  };

  // -----------------------------
  // IMPROVEMENT METRICS
  // -----------------------------
  const lastScore =
    analytics?.history?.length > 1
      ? analytics.history[analytics.history.length - 2].pronunciation_score
      : null;

  const improvement =
    lastScore !== null && result
      ? Math.round((result.pronunciation_score - lastScore) * 100)
      : null;

  const bestScore = analytics?.history
    ? Math.max(...analytics.history.map(h => h.pronunciation_score))
    : null;

  return (
    <div style={{ padding: 40, maxWidth: 800, margin: "auto" }}>
      <h1>🎤 AI Pronunciation Coach</h1>

      {/* PRACTICE MODE */}
      {practiceText && (
        <div style={styles.practiceMode}>
          <h3>🎯 Practice Mode</h3>
          <p><b>Say this:</b> {practiceText}</p>
        </div>
      )}

      {/* RECORD BUTTONS */}
      {!recording ? (
        <button onClick={startRecording}>🎙 Start Recording</button>
      ) : (
        <button onClick={stopRecording}>⏹ Stop Recording</button>
      )}

      <br /><br />

      <button onClick={analyze}>Analyze</button>

      {/* RESULTS */}
      {result && (
        <div style={styles.card}>
          <h3>Score: {Math.round(result.pronunciation_score * 100)}%</h3>
          <p>Confidence: {result.confidence}</p>

          {improvement !== null && (
            <p>
              Improvement: {improvement > 0 ? "+" : ""}
              {improvement}%
            </p>
          )}

          {bestScore && (
            <p>Best Score: {Math.round(bestScore * 100)}%</p>
          )}

          <p>{result.feedback}</p>

          {/* PHONEMES */}
          <h4>Phoneme Feedback</h4>
          {result.phoneme_feedback.map((p, i) => (
            <p key={i}>• {p}</p>
          ))}

          {/* PRACTICE SENTENCES */}
          <h4>Practice (click to use)</h4>
          {result.practice_sentences.map((s, i) => (
            <p
              key={i}
              style={{ cursor: "pointer" }}
              onClick={() => setPracticeText(s)}
            >
              • {s}
            </p>
          ))}
        </div>
      )}

      {/* CHART */}
      {analytics?.history && (
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={analytics.history}>
            <XAxis dataKey="step" />
            <YAxis domain={[0, 1]} />
            <Tooltip />
            <Line dataKey="pronunciation_score" stroke="#4CAF50" />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

export default App;

const styles = {
  card: {
    marginTop: 20,
    padding: 15,
    background: "#f5f5f5",
    borderRadius: 10
  },
  practiceMode: {
    marginBottom: 20,
    padding: 15,
    background: "#263238",
    color: "white",
    borderRadius: 10
  }
};