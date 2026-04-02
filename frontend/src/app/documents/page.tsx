"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { fetchDocuments, fetchDocument, updateDocument, createDocument } from "@/lib/api";

interface Document {
  path: string;
  title: string;
  type: string;
  relative_path: string;
  content: string;
  full_length: number;
  frontmatter?: Record<string, any>;
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [editContent, setEditContent] = useState("");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newType, setNewType] = useState("note");
  const [newContent, setNewContent] = useState("");

  // Load document list
  useEffect(() => {
    fetchDocuments()
      .then(setDocuments)
      .finally(() => setLoading(false));
  }, []);

  // Load selected document
  useEffect(() => {
    if (!selectedPath) {
      setSelectedDoc(null);
      return;
    }
    setEditing(false);
    setMessage("");
    fetchDocument(selectedPath).then((doc) => {
      setSelectedDoc(doc);
      setEditContent(doc.content || "");
    });
  }, [selectedPath]);

  const handleSave = async () => {
    if (!selectedPath) return;
    setSaving(true);
    setMessage("");
    try {
      await updateDocument(selectedPath, editContent, false);
      setMessage("Saved!");
      setEditing(false);
      // Reload to get updated content
      const doc = await fetchDocument(selectedPath);
      setSelectedDoc(doc);
    } catch {
      setMessage("Save failed");
    }
    setSaving(false);
  };

  const handleCreate = async () => {
    if (!newTitle.trim()) return;
    setSaving(true);
    try {
      const result = await createDocument(newTitle, newContent, newType);
      setShowCreate(false);
      setNewTitle("");
      setNewContent("");
      setNewType("note");
      // Refresh list
      const docs = await fetchDocuments();
      setDocuments(docs);
      setSelectedPath(result.path);
    } catch {
      setMessage("Create failed");
    }
    setSaving(false);
  };

  // Group documents by type
  const grouped = documents.reduce(
    (acc, doc) => {
      const type = doc.type || "note";
      if (!acc[type]) acc[type] = [];
      acc[type].push(doc);
      return acc;
    },
    {} as Record<string, Document[]>
  );

  const typeOrder = ["chapter", "character", "location", "worldbuilding", "series", "note"];

  return (
    <div className="grid md:grid-cols-3 gap-6">
      {/* Document List */}
      <div className="md:col-span-1 space-y-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-white">Documents</h1>
          <button
            onClick={() => setShowCreate(true)}
            className="text-sm px-3 py-1 bg-amber-600 text-white rounded hover:bg-amber-500"
          >
            + New
          </button>
        </div>

        {loading && <p className="text-slate-400">Loading...</p>}

        {typeOrder.map((type) => {
          const docs = grouped[type];
          if (!docs || docs.length === 0) return null;
          return (
            <div
              key={type}
              className="bg-slate-800/50 rounded-lg p-4 border border-slate-700"
            >
              <h3 className="text-sm font-semibold text-slate-400 uppercase mb-2">
                {type}s ({docs.length})
              </h3>
              <ul className="space-y-1">
                {docs.map((doc) => (
                  <li key={doc.path}>
                    <button
                      onClick={() => setSelectedPath(doc.path)}
                      className={`block w-full text-left truncate hover:text-amber-400 transition-colors ${
                        selectedPath === doc.path
                          ? "text-amber-400"
                          : "text-slate-300"
                      }`}
                    >
                      {doc.title}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          );
        })}
      </div>

      {/* Document Content */}
      <div className="md:col-span-2">
        {/* Create Modal */}
        {showCreate && (
          <div className="bg-slate-800/50 rounded-xl p-6 border border-amber-500/50 mb-4">
            <h2 className="text-xl font-bold text-amber-400 mb-4">
              Create New Document
            </h2>
            <div className="space-y-3">
              <input
                type="text"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                placeholder="Title"
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white placeholder-slate-400"
              />
              <select
                value={newType}
                onChange={(e) => setNewType(e.target.value)}
                className="bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white"
              >
                <option value="note">Note</option>
                <option value="character">Character</option>
                <option value="location">Location</option>
                <option value="chapter">Chapter</option>
                <option value="worldbuilding">Worldbuilding</option>
              </select>
              <textarea
                value={newContent}
                onChange={(e) => setNewContent(e.target.value)}
                placeholder="Content..."
                rows={10}
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white placeholder-slate-400 font-mono text-sm"
              />
              <div className="flex gap-2">
                <button
                  onClick={handleCreate}
                  disabled={saving || !newTitle.trim()}
                  className="px-4 py-2 bg-amber-600 text-white rounded hover:bg-amber-500 disabled:opacity-50"
                >
                  {saving ? "Creating..." : "Create"}
                </button>
                <button
                  onClick={() => setShowCreate(false)}
                  className="px-4 py-2 bg-slate-600 text-white rounded hover:bg-slate-500"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {selectedDoc ? (
          <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold text-amber-400">
                {selectedDoc.title}
              </h2>
              <div className="flex gap-2 items-center">
                <span className="px-3 py-1 bg-slate-700 rounded-full text-sm text-slate-300">
                  {selectedDoc.type}
                </span>
                {!editing ? (
                  <button
                    onClick={() => setEditing(true)}
                    className="px-4 py-2 bg-amber-600 hover:bg-amber-700 rounded-lg text-sm font-medium transition-colors"
                  >
                    Edit
                  </button>
                ) : (
                  <>
                    <button
                      onClick={handleSave}
                      disabled={saving}
                      className="px-4 py-2 bg-green-600 hover:bg-green-500 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
                    >
                      {saving ? "Saving..." : "Save"}
                    </button>
                    <button
                      onClick={() => {
                        setEditing(false);
                        setEditContent(selectedDoc.content || "");
                      }}
                      className="px-4 py-2 bg-slate-600 hover:bg-slate-500 rounded-lg text-sm font-medium transition-colors"
                    >
                      Cancel
                    </button>
                  </>
                )}
              </div>
            </div>

            {message && (
              <div
                className={`mb-4 p-2 rounded text-sm ${
                  message.includes("!")
                    ? "bg-green-900/30 text-green-300"
                    : "bg-red-900/30 text-red-300"
                }`}
              >
                {message}
              </div>
            )}

            {/* Content */}
            {editing ? (
              <textarea
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                rows={25}
                className="w-full bg-slate-900 border border-slate-600 rounded-lg px-4 py-3 text-slate-200 font-mono text-sm leading-relaxed focus:outline-none focus:border-amber-500"
              />
            ) : (
              <div className="prose prose-invert max-w-none">
                <p className="text-slate-300 whitespace-pre-wrap leading-relaxed">
                  {selectedDoc.content || "(empty document)"}
                </p>
              </div>
            )}

            {/* Footer */}
            <p className="text-slate-500 text-sm mt-4">
              {selectedDoc.full_length} characters &middot;{" "}
              {selectedDoc.relative_path}
            </p>
          </div>
        ) : (
          <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700 flex items-center justify-center h-64">
            <p className="text-slate-500">Select a document to view</p>
          </div>
        )}
      </div>
    </div>
  );
}
