"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface SyncStatus {
  filesystem_count: number;
  neo4j_count: number;
  only_in_filesystem: string[];
  size_divergent: string[];
  in_sync: boolean;
}

export default function SyncPage() {
  const [status, setStatus] = useState<SyncStatus | null>(null);
  const [reindexing, setReindexing] = useState(false);
  const [message, setMessage] = useState("");

  const fetchStatus = async () => {
    try {
      const res = await fetch("http://localhost:8004/sync/status");
      const data = await res.json();
      setStatus(data);
    } catch (e) {
      setMessage("Failed to fetch status");
    }
  };

  useEffect(() => { fetchStatus(); }, []);

  const reindex = async () => {
    setReindexing(true);
    setMessage("Re-indexing...");
    try {
      const res = await fetch("http://localhost:8004/sync/reindex", { method: "POST" });
      const data = await res.json();
      setMessage(data.success ? "✅ Re-index complete!" : "❌ Failed");
      fetchStatus();
    } catch (e) {
      setMessage("❌ Error");
    }
    setReindexing(false);
  };

  const getFilename = (path: string) => path.split("/").pop() || path;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Sync Status</h1>
          <p className="text-slate-400">Vault to Neo4j synchronization</p>
        </div>
        <Link href="/" className="text-slate-400 hover:text-white">Back</Link>
      </div>

      {status && (
        <div className="grid md:grid-cols-3 gap-4">
          <div className="bg-slate-800/50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-white">{status.filesystem_count}</div>
            <div className="text-sm text-slate-400">Vault Files</div>
          </div>
          <div className="bg-slate-800/50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-white">{status.neo4j_count}</div>
            <div className="text-sm text-slate-400">Indexed</div>
          </div>
          <div className={`p-4 rounded-lg ${status.in_sync ? 'bg-green-900/20' : 'bg-amber-900/20'}`}>
            <div className="text-2xl font-bold text-white">{status.in_sync ? "Synced" : "Needs Sync"}</div>
            <div className="text-sm text-slate-400">Status</div>
          </div>
        </div>
      )}

      <div className="flex gap-4">
        <button onClick={fetchStatus} className="px-4 py-2 bg-slate-600 text-white rounded">
          Refresh
        </button>
        <button onClick={reindex} disabled={reindexing} className="px-4 py-2 bg-amber-600 text-white rounded">
          {reindexing ? "Indexing..." : "Re-index Vault"}
        </button>
      </div>

      {message && <div className="p-3 bg-slate-700 rounded">{message}</div>}

      {status && !status.in_sync && (
        <div className="space-y-4">
          {status.only_in_filesystem?.length > 0 && (
            <div className="bg-slate-800/50 p-4 rounded">
              <h3 className="text-amber-400 mb-2">Not in Neo4j ({status.only_in_filesystem.length})</h3>
              <ul className="text-sm text-slate-300 space-y-1">
                {status.only_in_filesystem.slice(0, 5).map((p, i) => (
                  <li key={i}>{getFilename(p)}</li>
                ))}
              </ul>
            </div>
          )}

          {status.size_divergent?.length > 0 && (
            <div className="bg-slate-800/50 p-4 rounded">
              <h3 className="text-yellow-400 mb-2">Modified Files ({status.size_divergent.length})</h3>
              <ul className="text-sm text-slate-300 space-y-1">
                {status.size_divergent.slice(0, 5).map((p, i) => (
                  <li key={i}>{getFilename(p)}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
