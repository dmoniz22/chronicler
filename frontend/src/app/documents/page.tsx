import Link from "next/link";
import { fetchDocuments, fetchDocument } from "@/lib/api";

export const dynamic = 'force-dynamic';

export default async function DocumentsPage({ searchParams }: {
  searchParams: Promise<{ path?: string }>
}) {
  const documents = await fetchDocuments();
  const params = await searchParams;
  // Replace + with space (query param encoding) before fetching
  const docPath = params.path ? params.path.replace(/\+/g, ' ') : null;
  const selectedDoc = docPath ? await fetchDocument(docPath) : null;

  return (
    <div className="grid md:grid-cols-3 gap-6">
      {/* Document List */}
      <div className="md:col-span-1 space-y-4">
        <h1 className="text-2xl font-bold text-white">📄 Documents</h1>

        {/* Group by type */}
        {['book', 'chapter', 'character', 'location'].map(type => {
          const docs = documents.filter((d: any) => d.type === type);
          if (docs.length === 0) return null;

          return (
            <div key={type} className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
              <h3 className="text-sm font-semibold text-slate-400 uppercase mb-2">{type}s</h3>
              <ul className="space-y-1">
                {docs.map((doc: any) => (
                  <li key={doc.path}>
                    <Link
                      href={`/documents?path=${encodeURIComponent(doc.path)}`}
                      className={`block truncate hover:text-amber-400 transition-colors ${
                        params.path === doc.path ? 'text-amber-400' : 'text-slate-300'
                      }`}
                    >
                      {doc.title}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          );
        })}
      </div>

      {/* Document Content */}
      <div className="md:col-span-2">
        {selectedDoc ? (
          <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold text-amber-400">{selectedDoc.title}</h2>
              <span className="px-3 py-1 bg-slate-700 rounded-full text-sm text-slate-300">
                {selectedDoc.type}
              </span>
            </div>
            <div className="prose prose-invert max-w-none">
              <p className="text-slate-300 whitespace-pre-wrap">
                {selectedDoc.content.slice(0, 3000)}
                {selectedDoc.content.length > 3000 && '...'}
              </p>
            </div>
            <p className="text-slate-500 text-sm mt-4">
              {selectedDoc.full_length} characters · {selectedDoc.relative_path}
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
