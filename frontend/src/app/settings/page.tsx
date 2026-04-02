"use client";

import { useState, useEffect } from "react";
import { API_BASE } from "@/lib/api";

interface Model {
  id: string;
  name: string;
  cost: string;
}

export default function SettingsPage() {
  const [provider, setProvider] = useState("openrouter");
  const [apiKey, setApiKey] = useState("");
  const [apiKeyMasked, setApiKeyMasked] = useState("");
  const [openrouterModel, setOpenrouterModel] = useState("openai/gpt-4o-mini");
  const [ollamaUrl, setOllamaUrl] = useState("http://localhost:11434");
  const [ollamaModel, setOllamaModel] = useState("gemma3:12b");
  const [models, setModels] = useState<Model[]>([]);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState<"success" | "error">("success");

  // Load current settings
  useEffect(() => {
    fetch(`${API_BASE}/settings`)
      .then((r) => r.json())
      .then((data) => {
        setProvider(data.provider || "openrouter");
        setOpenrouterModel(data.openrouter_model || "openai/gpt-4o-mini");
        setOllamaUrl(data.ollama_url || "http://localhost:11434");
        setOllamaModel(data.ollama_model || "gemma3:12b");
        setApiKeyMasked(data.openrouter_api_key_masked || "");
      });
  }, []);

  // Load models when provider changes
  useEffect(() => {
    loadModels();
  }, [provider, ollamaUrl]);

  const loadModels = async () => {
    try {
      const params = new URLSearchParams({ provider });
      if (provider === "ollama") params.set("ollama_url", ollamaUrl);
      const res = await fetch(`${API_BASE}/settings/models?${params}`);
      const data = await res.json();
      setModels(data.models || []);
    } catch {
      setModels([]);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage("");
    try {
      const body: Record<string, string> = {
        provider,
        openrouter_model: openrouterModel,
        ollama_url: ollamaUrl,
        ollama_model: ollamaModel,
      };
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
          setApiKeyMasked(
            apiKey.length > 12
              ? apiKey.substring(0, 8) + "..." + apiKey.slice(-4)
              : "***"
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
      // Save first to ensure env is updated
      await handleSave();
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

  const handleRefreshOllama = async () => {
    await loadModels();
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

      {/* Provider Selection */}
      <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700 space-y-4">
        <h2 className="text-lg font-semibold text-white">AI Provider</h2>
        <div className="flex gap-3">
          <button
            onClick={() => setProvider("openrouter")}
            className={`flex-1 p-4 rounded-lg border-2 transition-all ${
              provider === "openrouter"
                ? "border-amber-500 bg-amber-900/20"
                : "border-slate-600 bg-slate-700/50 hover:border-slate-500"
            }`}
          >
            <div className="text-white font-semibold">OpenRouter</div>
            <div className="text-slate-400 text-xs mt-1">
              Cloud API. GPT-4o, Claude, Gemini, etc. Requires API key.
            </div>
          </button>
          <button
            onClick={() => setProvider("ollama")}
            className={`flex-1 p-4 rounded-lg border-2 transition-all ${
              provider === "ollama"
                ? "border-amber-500 bg-amber-900/20"
                : "border-slate-600 bg-slate-700/50 hover:border-slate-500"
            }`}
          >
            <div className="text-white font-semibold">Ollama (Local)</div>
            <div className="text-slate-400 text-xs mt-1">
              Run models locally. Free, private. Requires Ollama running.
            </div>
          </button>
        </div>
      </div>

      {/* OpenRouter Settings */}
      {provider === "openrouter" && (
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
          </p>
          {apiKeyMasked && (
            <p className="text-slate-500 text-sm">
              Current key:{" "}
              <span className="text-slate-300 font-mono">{apiKeyMasked}</span>
            </p>
          )}
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder={
              apiKeyMasked ? "Enter new key to replace..." : "sk-or-..."
            }
            className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white placeholder-slate-400 font-mono text-sm"
          />
        </div>
      )}

      {/* Ollama Settings */}
      {provider === "ollama" && (
        <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700 space-y-4">
          <h2 className="text-lg font-semibold text-white">Ollama Configuration</h2>
          <p className="text-slate-400 text-sm">
            Make sure Ollama is running locally. Install from{" "}
            <a
              href="https://ollama.ai"
              target="_blank"
              rel="noopener noreferrer"
              className="text-amber-400 hover:underline"
            >
              ollama.ai
            </a>
          </p>
          <div>
            <label className="text-xs text-slate-400 block mb-1">Ollama URL</label>
            <input
              type="text"
              value={ollamaUrl}
              onChange={(e) => setOllamaUrl(e.target.value)}
              placeholder="http://localhost:11434"
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white text-sm font-mono"
            />
          </div>
        </div>
      )}

      {/* Model Selection */}
      <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">Model</h2>
          {provider === "ollama" && (
            <button
              onClick={handleRefreshOllama}
              className="text-xs text-amber-400 hover:text-amber-300"
            >
              Refresh
            </button>
          )}
        </div>
        <select
          value={provider === "ollama" ? ollamaModel : openrouterModel}
          onChange={(e) =>
            provider === "ollama"
              ? setOllamaModel(e.target.value)
              : setOpenrouterModel(e.target.value)
          }
          className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white"
        >
          {models.length === 0 && (
            <option value="">No models found</option>
          )}
          {models.map((m) => (
            <option key={m.id} value={m.id}>
              {m.name} ({m.cost})
            </option>
          ))}
        </select>
        <div className="text-slate-500 text-xs">
          {provider === "ollama"
            ? "Pull more models: ollama pull llama3.1"
            : "Recommended: GPT-4o Mini for best cost/quality ratio."}
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
          disabled={testing}
          className="px-6 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-500 disabled:opacity-50"
        >
          {testing ? "Testing..." : "Test Connection"}
        </button>
      </div>
    </div>
  );
}
