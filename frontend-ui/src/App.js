import React, { useState } from "react";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("audio", file);

    setLoading(true);

    try {
      const res = await fetch("http://91.99.24.27:8080/analyze", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      alert("Error connecting to backend");
    }

    setLoading(false);
  };

  return (
    <div style={{ padding: 40, fontFamily: "Arial", maxWidth: 600 }}>
      <h1>🎤 Pronunciation Coach</h1>

      <p>Upload your audio and get instant feedback.</p>

      <input
        type="file"
        accept="audio/*"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <br /><br />

      <button onClick={handleUpload}>
        Analyze
      </button>

      {loading && <p>Processing...</p>}

      {result && (
        <div style={{ marginTop: 20 }}>
          <h3>Result</h3>

          <p><b>Transcript:</b> {result.transcript}</p>
          <p><b>Score:</b> {result.pronunciation_score}</p>
          <p><b>CEFR:</b> {result.cefr_level}</p>
          <p><b>Feedback:</b> {result.feedback}</p>
        </div>
      )}
    </div>
  );
}

export default App;