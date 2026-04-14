import { useState } from "react";
import { Bot, SendHorizonal } from "lucide-react";
import { askQuery } from "../services/api";

export default function QueryPanel() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([
    { type: "bot", text: "Ask about bin fullness or today's waste stats." }
  ]);
  const [loading, setLoading] = useState(false);

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMessage = { type: "user", text: query };
    setMessages(prev => [...prev, userMessage]);
    setQuery("");
    setLoading(true);

    try {
      const response = await askQuery(query);
      const botMessage = { type: "bot", text: response.answer };
      setMessages(prev => [...prev, botMessage]);
    } catch {
      const errorMessage = { type: "bot", text: "NLP service is temporarily unavailable." };
      setMessages(prev => [...prev, errorMessage]);
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

      <div className="mb-4 max-h-64 overflow-y-auto rounded-xl border border-[var(--line)] bg-[var(--soft-panel)] p-3">
        {messages.map((msg, index) => (
          <div key={index} className={`mb-2 ${msg.type === "user" ? "text-right" : "text-left"}`}>
            <span className={`inline-block rounded-lg px-3 py-1 text-sm ${
              msg.type === "user"
                ? "bg-cyan-700 text-white"
                : "bg-[var(--bg)] text-[var(--text-main)]"
            }`}>
              {msg.text}
            </span>
          </div>
        ))}
        {loading && (
          <div className="text-left">
            <span className="inline-block rounded-lg bg-[var(--bg)] px-3 py-1 text-sm text-[var(--text-soft)]">
              Thinking...
            </span>
          </div>
        )}
      </div>

      <form onSubmit={handleAsk} className="flex gap-2">
        <input
          className="flex-1 rounded-xl border border-[var(--line)] bg-[var(--soft-panel)] p-3 text-sm text-[var(--text-main)]"
          placeholder='Try: "How much plastic waste today?"'
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={loading}
        />
        <button className="rounded-xl bg-cyan-700 px-4 text-white hover:bg-cyan-800 disabled:opacity-50" disabled={loading}>
          <SendHorizonal size={16} />
        </button>
      </form>
    </div>
  );
}
