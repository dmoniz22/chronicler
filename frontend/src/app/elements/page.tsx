import Link from "next/link";
import { fetchElements, fetchEntityMentions } from "@/lib/api";

export const dynamic = 'force-dynamic';

const elementColors: Record<string, string> = {
  'Earth': 'from-amber-700 to-amber-900',
  'Fire': 'from-red-600 to-red-800',
  'Water': 'from-blue-500 to-blue-700',
  'Wind': 'from-slate-300 to-slate-500',
  'Spirit': 'from-purple-400 to-purple-600',
};

const elementEmojis: Record<string, string> = {
  'Earth': '🪨',
  'Fire': '🔥',
  'Water': '💧',
  'Wind': '💨',
  'Spirit': '✨',
};

export default async function ElementsPage({ searchParams }: {
  searchParams: Promise<{ name?: string }>
}) {
  const elements = await fetchElements();
  const params = await searchParams;
  const selectedName = params.name;

  const mentions = selectedName ? await fetchEntityMentions('element', selectedName) : null;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white">✨ The Five Elements</h1>

      {/* Element Cards */}
      <div className="grid md:grid-cols-5 gap-4">
        {elements.map((elem: any) => {
          const isSelected = selectedName === elem.name;
          return (
            <Link
              key={elem.name}
              href={`/elements?name=${encodeURIComponent(elem.name)}`}
              className={`p-6 rounded-xl border-2 transition-all ${
                isSelected ? 'border-amber-400 scale-105' : 'border-slate-700 hover:border-slate-500'
              } bg-gradient-to-br ${elementColors[elem.name] || 'from-slate-600 to-slate-800'}`}
            >
              <div className="text-4xl mb-2">{elementEmojis[elem.name] || '🔮'}</div>
              <h3 className="text-xl font-bold text-white">{elem.name}</h3>
            </Link>
          );
        })}
      </div>

      {/* Element Details */}
      {selectedName && mentions && (
        <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
          <h2 className="text-2xl font-bold text-amber-400 mb-4">
            {elementEmojis[selectedName]} {selectedName}
          </h2>
          <h3 className="text-lg font-semibold text-white mb-3">Mentioned in:</h3>
          <ul className="space-y-2">
            {mentions.map((doc: any, i: number) => (
              <li key={i} className="p-3 bg-slate-700/50 rounded-lg">
                <Link
                  href={`/documents?path=${encodeURIComponent(doc.path)}`}
                  className="text-slate-200 hover:text-amber-400"
                >
                  {doc.title}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
