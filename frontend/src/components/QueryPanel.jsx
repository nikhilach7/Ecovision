import { useState } from "react";
import { Bot, SendHorizonal } from "lucide-react";
import { askQuery } from "../services/api";

export default function QueryPanel() {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("Ask about bin fullness or today's waste stats.");
  const [loading, setLoading] = useState(false);

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      const response = await askQuery(query);
      setAnswer(response.answer);
    } catch {
      setAnswer("chat bot service is temporarily unavailable.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel p-6">
      <div className="mb-4 flex items-center gap-2">
        <Bot className="text-cyan-700" size={20} />
        <h3 className="font-title text-xl font-semibold text-[var(--text-main)]">NLP Query Console</h3>
      </div>

      <form onSubmit={handleAsk} className="flex gap-2">
        <input
          className="flex-1 rounded-xl border border-[var(--line)] bg-[var(--soft-panel)] p-3 text-sm text-[var(--text-main)]"
          placeholder='Try: "How much plastic waste today?"'
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button className="rounded-xl bg-cyan-700 px-4 text-white hover:bg-cyan-800" disabled={loading}>
          <SendHorizonal size={16} />
        </button>
      </form>

      <div className="mt-4 rounded-xl border border-[var(--line)] bg-[var(--soft-panel)] p-3 text-sm text-[var(--text-soft)]">
        {loading ? "Thinking..." : answer}
      </div>
    </div>
  );
}
