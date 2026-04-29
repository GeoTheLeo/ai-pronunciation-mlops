import React, { useState, useRef, useEffect } from "react";
import WaveSurfer from "wavesurfer.js";

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [recording, setRecording] = useState(false);

  const mediaRecorderRef = useRef(null);
  const audioChunks = useRef([]);
  const waveformRef = useRef(null);
  const waveSurferRef = useRef(null);

  // -----------------------------
  // INIT WAVESURFER
  // -----------------------------
  useEffect(() => {
    if (waveformRef.current) {
      waveSurferRef.current = WaveSurfer.create({
        container: waveformRef.current,
        waveColor: "#3b82f6",
        progressColor: "#1d4ed8",
        height: 80,
      });
    }

    return () => {
      if (waveSurferRef.current) {
        waveSurferRef.current.destroy();
      }
    };
  }, []);

  // -----------------------------
  // START RECORDING
  // -----------------------------
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);

      mediaRecorderRef.current = mediaRecorder;
      audioChunks.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunks.current.push(event.data);
      };

      mediaRecorder.onstop = handleStop;

      mediaRecorder.start();
      setRecording(true);
    } catch (err) {
      alert("Microphone access denied");
    }
  };

  // -----------------------------
  // STOP RECORDING
  // -----------------------------
  const stopRecording = () => {
    mediaRecorderRef.current.stop();
    setRecording(false);
  };

  // -----------------------------
  // HANDLE STOP (UPLOAD + WAVEFORM)
  // -----------------------------
  const handleStop = async () => {
    const blob = new Blob(audioChunks.current, { type: "audio/wav" });

    // Show waveform
    const url = URL.createObjectURL(blob);
    if (waveSurferRef.current) {
      waveSurferRef.current.load(url);
    }

    // Send to backend
    const formData = new FormData();
    formData.append("audio", blob, "recording.wav");

    setLoading(true);

    try {
      const res = await fetch("http://91.99.24.27:8080/analyze", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      setResult(data);
    } catch (err) {
      alert("Backend error");
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white shadow-xl rounded-2xl p-8 w-full max-w-lg text-center">

        <h1 className="text-3xl font-bold mb-4">🎤 Pronunciation Coach</h1>
        <p className="text-gray-600 mb-6">
          Speak and get instant AI feedback
        </p>

        {!recording ? (
          <button
            onClick={startRecording}
            className="bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700"
          >
            Start Recording
          </button>
        ) : (
          <button
            onClick={stopRecording}
            className="bg-red-600 text-white px-6 py-3 rounded-xl hover:bg-red-700"
          >
            Stop Recording
          </button>
        )}

        {/* Waveform */}
        <div ref={waveformRef} className="mt-6"></div>

        {loading && <p className="mt-4">Processing...</p>}

        {result && (
          <div className="mt-6 text-left">
            <h3 className="font-semibold mb-2">Result</h3>

            <p><b>Transcript:</b> {result.transcript}</p>

            <p className={`font-bold ${
              result.pronunciation_score > 0.8 ? "text-green-600" : "text-red-600"
            }`}>
              Score: {result.pronunciation_score}
            </p>

            <p><b>CEFR:</b> {result.cefr_level}</p>
            <p><b>Feedback:</b> {result.feedback}</p>
          </div>
        )}

      </div>
    </div>
  );
}

export default App;