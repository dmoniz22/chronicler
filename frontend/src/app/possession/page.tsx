"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface Character {
  name: string;
  description: string;
  status: string;
  affinity: string;
}

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function PossessionPage() {
  const [characters, setCharacters] = useState<Character[]>([]);
  const [selectedChar, setSelectedChar] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load characters
  useEffect(() => {
    fetch("http://localhost:8004/possession/characters")
      .then((r) => r.json())
      .then((data) => setCharacters(data.characters))
      .catch((e) => setError("Failed to load characters"));
  }, []);

  const sendMessage = async () => {
    if (!input.trim() || !selectedChar) return;

    const userMsg: Message = { role: "user", content: input };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(
        `http://localhost:8004/possession/${encodeURIComponent(selectedChar)}/chat`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: userMsg.content, session_id: "web" }),
        }
      );

      if (!res.ok) {
        throw new Error(`Chat failed: ${res.status}`);
      }

      const data = await res.json();
      setMessages((m) => [...m, { role: "assistant", content: data.response }]);
    } catch (e: any) {
      const errorMsg = e?.message || "";
      if (errorMsg.includes("No API key") || errorMsg.includes("No Ollama")) {
        setError(`No AI provider configured. Go to Settings to set up OpenRouter or Ollama.`);
      } else {
        setError(`AI unavailable. Using offline mode.`);
      }
      // Fallback: simple character responses
      const fallbackResponses: Record<string, string> = {
        "Alatha": "*shifts nervously, eyes showing five colors for a moment* I... I'm still getting used to this. Ask me about anything, I guess. But not too loud. Not yet.",
        "Fidomar": "*places a steady hand on the table* Whatever guidance you seek, I'm here. Earth endures, and so do friends.",
        "Elora": "*grins, hair fluttering in a breeze you don't feel* Oh! Are you going to interview me? How fun! What do you want to know? My rates are reasonable."
      };
      setMessages((m) => [...m, { role: "assistant", content: fallbackResponses[selectedChar] || "*nods silently*" }]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = async () => {
    if (!selectedChar) return;
    await fetch(
      `http://localhost:8004/possession/${encodeURIComponent(selectedChar)}/clear?session_id=web`,
      { method: "POST" }
    );
    setMessages([]);
  };

  return (
    <div className="grid md:grid-cols-4 gap-6 h-[calc(100vh-8rem)]">
      {/* Character Selection */}
      <div className="md:col-span-1 space-y-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-white">🎭 Possession Chamber</h1>
          <Link href="/" className="text-slate-400 hover:text-white text-sm">
            ← Back
          </Link>
        </div>

        <p className="text-slate-400 text-sm">
          Speak with your characters. They remember your conversations.
        </p>

        <div className="space-y-2">
          {characters.map((char) => (
            <button
              key={char.name}
              onClick={() => {
                setSelectedChar(char.name);
                setMessages([]);
              }}
              className={`w-full text-left p-3 rounded-lg border transition-all ${
                selectedChar === char.name
                  ? "bg-amber-900/30 border-amber-500"
                  : "bg-slate-800/50 border-slate-700 hover:border-slate-500"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold text-white">{char.name}</span>
                <span className="text-xs text-slate-400">{char.affinity}</span>
              </div>
              <p className="text-xs text-slate-400 mt-1 line-clamp-2">
                {char.description}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Chat Interface */}
      <div className="md:col-span-3 flex flex-col bg-slate-800/30 rounded-xl border border-slate-700">
        {/* Chat Header */}
        <div className="p-4 border-b border-slate-700 flex items-center justify-between">
          {selectedChar ? (
            <>
              <div>
                <h2 className="text-lg font-bold text-amber-400">{selectedChar}</h2>
                <p className="text-xs text-slate-400">
                  {characters.find((c) => c.name === selectedChar)?.affinity}
                </p>
              </div>
              <button
                onClick={clearChat}
                className="text-xs text-slate-400 hover:text-white px-3 py-1 rounded bg-slate-700"
              >
                Clear History
              </button>
            </>
          ) : (
            <p className="text-slate-500">Select a character to begin</p>
          )}
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {!selectedChar ? (
            <div className="text-center text-slate-500 mt-20">
              <p className="text-4xl mb-4">🎭</p>
              <p>Choose a character from the left to begin your interview</p>
            </div>
          ) : messages.length === 0 ? (
            <div className="text-center text-slate-500 mt-20">
              <p className="text-2xl mb-4">👋</p>
              <p>Say something to {selectedChar}</p>
            </div>
          ) : (
            messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[80%] p-3 rounded-lg ${
                    msg.role === "user"
                      ? "bg-amber-600 text-white"
                      : "bg-slate-700 text-slate-200"
                  }`}
                >
                  <p className="text-xs text-slate-400 mb-1">
                    {msg.role === "user" ? "You" : selectedChar}
                  </p>
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            ))
          )}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-slate-700 p-3 rounded-lg">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:0.1s]" />
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                </div>
              </div>
            </div>
          )}
          {error && (
            <div className="bg-red-900/30 border border-red-500 text-red-200 p-3 rounded">
              {error}
            </div>
          )}
        </div>

        {/* Input */}
        <div className="p-4 border-t border-slate-700">
          <div className="flex space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e: React.KeyboardEvent) => e.key === "Enter" && sendMessage()}
              placeholder={selectedChar ? `Speak to ${selectedChar}...` : "Select a character first"}
              disabled={!selectedChar || loading}
              className="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white placeholder-slate-400 focus:outline-none focus:border-amber-500"
            />
            <button
              onClick={sendMessage}
              disabled={!selectedChar || !input.trim() || loading}
              className="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}