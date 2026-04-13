import { useState } from "react";
import { Camera, LoaderCircle, UploadCloud } from "lucide-react";
import { uploadWasteImage } from "../services/api";

export default function UploadPanel({ onUploaded }) {
  const [file, setFile] = useState(null);
  const [location, setLocation] = useState("Campus Block A");
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError("");
    try {
      const response = await uploadWasteImage(file, location);
      setPrediction(response);
      onUploaded();
    } catch (err) {
      setError(err?.response?.data?.detail || "Upload failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-2xl bg-white/95 p-6 shadow-panel">
      <div className="mb-4 flex items-center gap-2">
        <Camera className="text-emerald-600" size={20} />
        <h3 className="font-title text-xl font-semibold text-slate-800">Image Classification</h3>
      </div>

      <form onSubmit={handleSubmit} className="space-y-3">
        <input
          type="file"
          accept="image/*"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="w-full rounded-xl border border-slate-200 p-3 text-sm"
        />
        <input
          type="text"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          placeholder="Bin location"
          className="w-full rounded-xl border border-slate-200 p-3 text-sm"
        />
        <button
          disabled={!file || loading}
          className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-600 px-4 py-3 font-medium text-white transition hover:bg-emerald-700 disabled:opacity-60"
        >
          {loading ? <LoaderCircle className="animate-spin" size={18} /> : <UploadCloud size={18} />}
          {loading ? "Classifying..." : "Upload & Predict"}
        </button>
      </form>

      {error && <p className="mt-3 text-sm text-rose-600">{error}</p>}

      {prediction && (
        <div className="mt-4 rounded-xl border border-emerald-100 bg-emerald-50 p-3 text-sm text-emerald-800">
          <p>
            Predicted Type: <strong>{prediction.waste_type}</strong>
          </p>
          <p>Confidence: {(prediction.confidence * 100).toFixed(1)}%</p>
          <p>Location: {prediction.location}</p>
        </div>
      )}
    </div>
  );
}
