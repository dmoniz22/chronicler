"use client";

import { useState } from "react";
import Link from "next/link";
import { API_BASE } from "@/lib/api";

const ELEMENTS = ["Fire", "Water", "Earth", "Wind", "Spirit", "Any"];
const CATEGORIES = [
  { id: "towns", label: "Towns", icon: "🏘️" },
  { id: "characters", label: "Characters", icon: "👤" },
  { id: "magic", label: "Magic", icon: "✨" },
  { id: "plots", label: "Plot Seeds", icon: "📖" },
];

interface IdeaResult {
  [key: string]: any;
}

export default function IdeaForgePage() {
  const [activeTab, setActiveTab] = useState<string>("towns");
  const [element, setElement] = useState("Any");
  const [mode, setMode] = useState<"quick" | "ai">("quick");
  const [customPrompt, setCustomPrompt] = useState("");
  const [results, setResults] = useState<IdeaResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [aiModel, setAiModel] = useState("");

  const generate = async () => {
    setLoading(true);
    setError("");
    setResults([]);

    const elem = element === "Any" ? null : element;

    try {
      if (mode === "quick") {
        // Template-based generation
        const endpoints: Record<string, string> = {
          towns: `${API_BASE}/idea-forge/towns`,
          characters: `${API_BASE}/idea-forge/characters`,
          magic: `${API_BASE}/idea-forge/magic-techniques`,
          plots: `${API_BASE}/idea-forge/plot-seeds`,
        };
        const url = new URL(endpoints[activeTab]);
        if (elem) url.searchParams.set("element", elem);
        url.searchParams.set("count", "5");
        const res = await fetch(url.toString());
        const data = await res.json();
        const key = activeTab === "magic" ? "techniques" : activeTab;
        setResults(data[key] || []);
      } else {
        // AI-powered generation
        const res = await fetch(`${API_BASE}/idea-forge/ai-generate`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            category: activeTab,
            prompt: customPrompt,
            element: elem || "",
            count: 5,
          }),
        });
        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || "AI generation failed");
        }
        const data = await res.json();
        setResults(data.ideas || []);
        setAiModel(data.model || "");
      }
    } catch (e: any) {
      setError(e.message || "Generation failed");
    }
    setLoading(false);
  };

  const getElementColor = (el: string) => {
    const colors: Record<string, string> = {
      Fire: "text-red-400",
      Water: "text-blue-400",
      Earth: "text-amber-400",
      Wind: "text-cyan-400",
      Spirit: "text-purple-400",
    };
    return colors[el] || "text-slate-400";
  };

  const renderResult = (item: IdeaResult, index: number) => {
    switch (activeTab) {
      case "towns":
        return (
          <div key={index} className="bg-slate-800/50 border border-slate-700 p-4 rounded-lg">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-bold text-white text-lg">{item.name}</span>
              {item.element && (
                <span className={`text-xs ${getElementColor(item.element)}`}>
                  {item.element}
                </span>
              )}
              {item.type && (
                <span className="text-xs text-slate-500">{item.type}</span>
              )}
            </div>
            <p className="text-slate-300 mt-2">{item.description}</p>
          </div>
        );

      case "characters":
        return (
          <div key={index} className="bg-slate-800/50 border border-slate-700 p-4 rounded-lg">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-bold text-white text-lg">{item.name}</span>
              {item.element && (
                <span className={`text-xs ${getElementColor(item.element)}`}>
                  {item.element}
                </span>
              )}
              {item.role && (
                <span className="text-xs bg-slate-600 px-2 py-0.5 rounded">
                  {item.role}
                </span>
              )}
            </div>
            {item.traits && item.traits.length > 0 && (
              <div className="flex gap-2 mt-2 flex-wrap">
                {item.traits.map((t: string, j: number) => (
                  <span
                    key={j}
                    className="text-xs bg-slate-700 px-2 py-1 rounded text-slate-300"
                  >
                    {t}
                  </span>
                ))}
              </div>
            )}
            <p className="text-slate-300 mt-2">{item.concept}</p>
          </div>
        );

      case "magic":
        return (
          <div key={index} className="bg-slate-800/50 border border-slate-700 p-4 rounded-lg">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-bold text-white text-lg">{item.name}</span>
              {item.element && (
                <span className={`text-xs ${getElementColor(item.element)}`}>
                  {item.element}
                </span>
              )}
              {item.difficulty && (
                <span
                  className={`text-xs px-2 py-0.5 rounded ${
                    item.difficulty === "master"
                      ? "bg-purple-600"
                      : item.difficulty === "advanced"
                      ? "bg-red-600"
                      : item.difficulty === "intermediate"
                      ? "bg-yellow-600"
                      : "bg-green-600"
                  }`}
                >
                  {item.difficulty}
                </span>
              )}
            </div>
            <p className="text-slate-300 mt-2">{item.description}</p>
          </div>
        );

      case "plots":
        return (
          <div key={index} className="bg-slate-800/50 border border-slate-700 p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              {item.element && (
                <span className={`text-xs ${getElementColor(item.element)}`}>
                  {item.element}
                </span>
              )}
              {item.type && (
                <span className="text-xs text-slate-500">{item.type}</span>
              )}
            </div>
            <p className="text-slate-200">{item.plot}</p>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Idea Forge</h1>
          <p className="text-slate-400">
            Generate towns, characters, magic, and plot ideas
          </p>
        </div>
        <Link href="/" className="text-slate-400 hover:text-white text-sm">
          Back
        </Link>
      </div>

      {/* Mode Toggle */}
      <div className="flex gap-2 bg-slate-800/50 p-1 rounded-lg w-fit">
        <button
          onClick={() => setMode("quick")}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            mode === "quick"
              ? "bg-amber-600 text-white"
              : "text-slate-400 hover:text-white"
          }`}
        >
          Quick Generate
        </button>
        <button
          onClick={() => setMode("ai")}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            mode === "ai"
              ? "bg-amber-600 text-white"
              : "text-slate-400 hover:text-white"
          }`}
        >
          AI Generate
        </button>
      </div>

      {mode === "ai" && (
        <div className="bg-amber-900/20 border border-amber-500/30 rounded-lg p-3 text-sm text-amber-200">
          AI mode uses your vault documents as context to generate ideas consistent
          with your world.{" "}
          <Link href="/settings" className="underline text-amber-400">
            Configure your API key in Settings
          </Link>
          .
        </div>
      )}

      {/* Category Tabs */}
      <div className="flex gap-2 border-b border-slate-700 pb-2">
        {CATEGORIES.map((tab) => (
          <button
            key={tab.id}
            onClick={() => {
              setActiveTab(tab.id);
              setResults([]);
            }}
            className={`px-4 py-2 rounded-t-lg text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? "bg-amber-600 text-white"
                : "text-slate-400 hover:text-white"
            }`}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
      </div>

      {/* Controls */}
      <div className="flex flex-wrap gap-3 items-end">
        <div>
          <label className="text-xs text-slate-400 block mb-1">Element</label>
          <select
            value={element}
            onChange={(e) => setElement(e.target.value)}
            className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm"
          >
            {ELEMENTS.map((el) => (
              <option key={el} value={el}>
                {el}
              </option>
            ))}
          </select>
        </div>

        {mode === "ai" && (
          <div className="flex-1 min-w-[200px]">
            <label className="text-xs text-slate-400 block mb-1">
              Custom direction (optional)
            </label>
            <input
              type="text"
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
              placeholder="e.g. A fishing village with a dark secret"
              className="w-full bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm placeholder-slate-500"
            />
          </div>
        )}

        <button
          onClick={generate}
          disabled={loading}
          className="px-5 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-500 disabled:opacity-50 font-medium whitespace-nowrap"
        >
          {loading
            ? "Generating..."
            : mode === "ai"
            ? "AI Generate"
            : "Generate"}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-900/30 border border-red-500 text-red-200 p-3 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* Results */}
      {results.length > 0 && (
        <div className="space-y-3">
          {mode === "ai" && aiModel && (
            <p className="text-xs text-slate-500">
              Generated by {aiModel}
            </p>
          )}
          {results.map((item, i) => renderResult(item, i))}
        </div>
      )}

      {!loading && results.length === 0 && !error && (
        <div className="text-center text-slate-500 py-12">
          <p className="text-3xl mb-2">🎲</p>
          <p>Click Generate to create ideas</p>
        </div>
      )}
    </div>
  );
}
