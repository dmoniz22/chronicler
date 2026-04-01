"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface Town { name: string; element: string; type: string; description: string; }
interface Character { name: string; element: string; role: string; traits: string[]; concept: string; }
interface Technique { name: string; element: string; difficulty: string; description: string; }
interface Plot { plot: string; element: string; type: string; }

const ELEMENTS = ["Fire", "Water", "Earth", "Wind", "Spirit", "Any"];
const ROLES = ["ally", "mentor", "rival", "antagonist", "neutral"];
const DIFFICULTIES = ["basic", "intermediate", "advanced", "master"];

export default function IdeaForgePage() {
  const [activeTab, setActiveTab] = useState<"towns" | "characters" | "magic" | "plots">("towns");
  const [element, setElement] = useState("Any");
  const [towns, setTowns] = useState<Town[]>([]);
  const [characters, setCharacters] = useState<Character[]>([]);
  const [techniques, setTechniques] = useState<Technique[]>([]);
  const [plots, setPlots] = useState<Plot[]>([]);
  const [loading, setLoading] = useState(false);

  const generate = async () => {
    setLoading(true);
    const elem = element === "Any" ? null : element;
    
    try {
      if (activeTab === "towns") {
        const res = await fetch(`http://localhost:8004/idea-forge/towns?element=${elem || ''}&count=5`);
        const data = await res.json();
        setTowns(data.towns || []);
      } else if (activeTab === "characters") {
        const res = await fetch(`http://localhost:8004/idea-forge/characters?element=${elem || ''}&count=5`);
        const data = await res.json();
        setCharacters(data.characters || []);
      } else if (activeTab === "magic") {
        const res = await fetch(`http://localhost:8004/idea-forge/magic-techniques?element=${elem || ''}&count=5`);
        const data = await res.json();
        setTechniques(data.techniques || []);
      } else if (activeTab === "plots") {
        const res = await fetch(`http://localhost:8004/idea-forge/plot-seeds?element=${elem || ''}&count=5`);
        const data = await res.json();
        setPlots(data.plots || []);
      }
    } catch (e) {
      console.error("Generation failed:", e);
    }
    setLoading(false);
  };

  useEffect(() => { generate(); }, [activeTab, element]);

  const getElementColor = (el: string) => {
    const colors: Record<string, string> = {
      Fire: "text-red-400", Water: "text-blue-400", Earth: "text-amber-400",
      Wind: "text-cyan-400", Spirit: "text-purple-400"
    };
    return colors[el] || "text-slate-400";
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">⚒️ Idea Forge</h1>
          <p className="text-slate-400">Generate content for your world</p>
        </div>
        <Link href="/" className="text-slate-400 hover:text-white">← Back</Link>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap gap-4 items-center">
        <select
          value={element}
          onChange={(e) => setElement(e.target.value)}
          className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-white"
        >
          {ELEMENTS.map(el => <option key={el} value={el}>{el} Element</option>)}
        </select>
        <button
          onClick={generate}
          disabled={loading}
          className="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-500 disabled:opacity-50"
        >
          {loading ? "Generating..." : "🎲 Generate"}
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-slate-700 pb-2">
        {[
          { id: "towns", label: "🏘️ Towns" },
          { id: "characters", label: "👤 Characters" },
          { id: "magic", label: "✨ Magic" },
          { id: "plots", label: "📖 Plot Seeds" }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`px-4 py-2 rounded-t-lg ${
              activeTab === tab.id
                ? "bg-amber-600 text-white"
                : "text-slate-400 hover:text-white"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Results */}
      <div className="space-y-4">
        {activeTab === "towns" && towns.map((town, i) => (
          <div key={i} className="bg-slate-800/50 border border-slate-700 p-4 rounded-lg">
            <div className="flex items-center gap-2">
              <span className="font-bold text-white">{town.name}</span>
              <span className={`text-xs ${getElementColor(town.element)}`}>{town.element}</span>
              <span className="text-xs text-slate-500">{town.type}</span>
            </div>
            <p className="text-slate-300 mt-2">{town.description}</p>
          </div>
        ))}

        {activeTab === "characters" && characters.map((char, i) => (
          <div key={i} className="bg-slate-800/50 border border-slate-700 p-4 rounded-lg">
            <div className="flex items-center gap-2">
              <span className="font-bold text-white">{char.name}</span>
              <span className={`text-xs ${getElementColor(char.element)}`}>{char.element}</span>
              <span className="text-xs bg-slate-600 px-2 py-0.5 rounded">{char.role}</span>
            </div>
            <p className="text-slate-300 mt-2">{char.concept}</p>
            <div className="flex gap-2 mt-2">
              {char.traits.map((t, j) => (
                <span key={j} className="text-xs bg-slate-700 px-2 py-1 rounded text-slate-300">{t}</span>
              ))}
            </div>
          </div>
        ))}

        {activeTab === "magic" && techniques.map((tech, i) => (
          <div key={i} className="bg-slate-800/50 border border-slate-700 p-4 rounded-lg">
            <div className="flex items-center gap-2">
              <span className="font-bold text-white">{tech.name}</span>
              <span className={`text-xs ${getElementColor(tech.element)}`}>{tech.element}</span>
              <span className={`text-xs px-2 py-0.5 rounded ${
                tech.difficulty === "master" ? "bg-purple-600" :
                tech.difficulty === "advanced" ? "bg-red-600" :
                tech.difficulty === "intermediate" ? "bg-yellow-600" : "bg-green-600"
              }`}>{tech.difficulty}</span>
            </div>
            <p className="text-slate-300 mt-2">{tech.description}</p>
          </div>
        ))}

        {activeTab === "plots" && plots.map((plot, i) => (
          <div key={i} className="bg-slate-800/50 border border-slate-700 p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <span className={`text-xs ${getElementColor(plot.element)}`}>{plot.element}</span>
              <span className="text-xs text-slate-500">{plot.type}</span>
            </div>
            <p className="text-slate-200">{plot.plot}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
