"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { API_BASE } from "@/lib/api";

interface Model {
  id: string;
  name: string;
  cost: string;
}

export default function SettingsPage() {
  const [apiKey, setApiKey] = useState("");
  const [apiKeyMasked, setApiKeyMasked] = useState("");
  const [model, setModel] = useState("openai/gpt-4o-mini");
  const [models, setModels] = useState<Model[]>([]);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState<"success" | "error">("success");

  useEffect(() => {
    // Load current settings
    fetch(`${API_BASE}/settings`)
      .then((r) => r.json())
      .then((data) => {
        setModel(data.openrouter_model || "openai/gpt-4o-mini");
        setApiKeyMasked(data.openrouter_api_key_masked || "");
      });

    // Load available models
    fetch(`${API_BASE}/settings/models`)
      .then((r) => r.json())
      .then((data) => setModels(data.models || []));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setMessage("");
    try {
      const body: Record<string, string> = { openrouter_model: model };
      if (apiKey) {
        body.openrouter_api_key = apiKey;
      }
      const res = await fetch(`${API_BASE}/settings`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (data.success) {
        setMessageType("success");
        setMessage("Settings saved!");
        if (apiKey) {
          const key = apiKey;
          setApiKeyMasked(
            key.length > 12 ? key.substring(0, 8) + "..." + key.slice(-4) : "***"
          );
          setApiKey("");
        }
      }
    } catch {
      setMessageType("error");
      setMessage("Failed to save settings");
    }
    setSaving(false);
  };

  const handleTest = async () => {
    setTesting(true);
    setMessage("");
    try {
      const res = await fetch(`${API_BASE}/settings/test`, { method: "POST" });
      const data = await res.json();
      setMessageType(data.success ? "success" : "error");
      setMessage(data.message);
    } catch {
      setMessageType("error");
      setMessage("Connection test failed");
    }
    setTesting(false);
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Settings</h1>
        <p className="text-slate-400 mt-1">
          Configure your AI provider for idea generation and character chat.
        </p>
      </div>

      {message && (
        <div
          className={`p-3 rounded-lg text-sm ${
            messageType === "success"
              ? "bg-green-900/30 border border-green-500 text-green-300"
              : "bg-red-900/30 border border-red-500 text-red-300"
          }`}
        >
          {message}
        </div>
      )}

      {/* API Key */}
      <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700 space-y-4">
        <h2 className="text-lg font-semibold text-white">OpenRouter API Key</h2>
        <p className="text-slate-400 text-sm">
          Get your key at{" "}
          <a
            href="https://openrouter.ai/keys"
            target="_blank"
            rel="noopener noreferrer"
            className="text-amber-400 hover:underline"
          >
            openrouter.ai/keys
          </a>
          . This enables AI-powered idea generation and character chat.
        </p>
        {apiKeyMasked && (
          <p className="text-slate-500 text-sm">
            Current key: <span className="text-slate-300 font-mono">{apiKeyMasked}</span>
          </p>
        )}
        <input
          type="password"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          placeholder={apiKeyMasked ? "Enter new key to replace..." : "sk-or-..."}
          className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white placeholder-slate-400 font-mono text-sm"
        />
      </div>

      {/* Model Selection */}
      <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700 space-y-4">
        <h2 className="text-lg font-semibold text-white">AI Model</h2>
        <p className="text-slate-400 text-sm">
          Choose the model for idea generation and character chat.
        </p>
        <select
          value={model}
          onChange={(e) => setModel(e.target.value)}
          className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white"
        >
          {models.map((m) => (
            <option key={m.id} value={m.id}>
              {m.name} ({m.cost} cost)
            </option>
          ))}
        </select>
        <div className="text-slate-500 text-xs">
          Recommended: GPT-4o Mini for best cost/quality ratio.
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-3">
        <button
          onClick={handleSave}
          disabled={saving}
          className="px-6 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-500 disabled:opacity-50 font-medium"
        >
          {saving ? "Saving..." : "Save Settings"}
        </button>
        <button
          onClick={handleTest}
          disabled={testing || !apiKeyMasked}
          className="px-6 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-500 disabled:opacity-50"
        >
          {testing ? "Testing..." : "Test Connection"}
        </button>
      </div>
    </div>
  );
}
