import { Leaf } from "lucide-react";
import { useState } from "react";

export default function LoginPage({ onLogin }) {
  const [mode, setMode] = useState("login");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await onLogin({ mode, fullName, email, password });
    } catch (err) {
      setError(err?.response?.data?.detail || "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto flex min-h-screen w-full max-w-6xl items-center px-4 py-10">
      <div className="grid w-full overflow-hidden rounded-3xl bg-white/95 shadow-panel md:grid-cols-2">
        <div className="bg-[linear-gradient(145deg,#0f3d23,#1d6d3f)] p-8 text-white md:p-12">
          <div className="mb-8 inline-flex items-center gap-2 rounded-full bg-white/15 px-4 py-2 text-sm">
            <Leaf size={16} /> EcoVision AI
          </div>
          <h1 className="font-title text-4xl font-bold leading-tight">Smart Waste Segregation & Monitoring</h1>
          <p className="mt-4 text-emerald-100">
            Monitor live bin fill, classify waste images using AI, and query city waste insights using natural language.
          </p>
        </div>

        <div className="p-8 md:p-12">
          <h2 className="font-title text-2xl font-bold text-slate-800">Dashboard Login</h2>
          <p className="mt-2 text-sm text-slate-500">Authenticated access for operators and municipal teams.</p>
          <div className="mt-6 inline-flex rounded-xl bg-slate-100 p-1 text-sm">
            <button
              type="button"
              className={`rounded-lg px-4 py-2 ${mode === "login" ? "bg-white shadow" : "text-slate-600"}`}
              onClick={() => setMode("login")}
            >
              Sign In
            </button>
            <button
              type="button"
              className={`rounded-lg px-4 py-2 ${mode === "register" ? "bg-white shadow" : "text-slate-600"}`}
              onClick={() => setMode("register")}
            >
              Create Account
            </button>
          </div>
          <form onSubmit={handleSubmit} className="mt-8 space-y-4">
            {mode === "register" && (
              <input
                className="w-full rounded-xl border border-slate-200 p-3"
                placeholder="Full name"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
              />
            )}
            <input
              className="w-full rounded-xl border border-slate-200 p-3"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <input
              className="w-full rounded-xl border border-slate-200 p-3"
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            {error && <p className="text-sm text-rose-600">{error}</p>}
            <button
              className="w-full rounded-xl bg-emerald-600 p-3 font-semibold text-white transition hover:bg-emerald-700"
              disabled={loading}
            >
              {loading ? "Please wait..." : mode === "login" ? "Sign In" : "Create Account"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
