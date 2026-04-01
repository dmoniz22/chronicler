import Link from "next/link";
import { fetchCharacters, fetchEntityMentions } from "@/lib/api";

export const dynamic = 'force-dynamic';

export default async function CharactersPage({ searchParams }: {
  searchParams: Promise<{ name?: string }>
}) {
  const characters = await fetchCharacters();
  const params = await searchParams;
  const selectedName = params.name;

  // Filter to only real character names (not false positives)
  const knownCharacters = [
    'Alatha', 'Fidomar', 'Elora', 'Ignatius', 'Galen',
    'Vesta', 'Lyria', 'Zephyros', 'Brannor'
  ];

  // Filter characters - keep known ones or ones mentioned in multiple docs
  const filteredCharacters = characters.filter((c: any) =>
    knownCharacters.some(k => c.name.toLowerCase() === k.toLowerCase()) ||
    (c.mentioned_in && c.mentioned_in.length > 1)
  );

  const mentions = selectedName ? await fetchEntityMentions('character', selectedName) : null;

  return (
    <div className="grid md:grid-cols-3 gap-6">
      {/* Character List */}
      <div className="md:col-span-1 space-y-4">
        <h1 className="text-2xl font-bold text-white">👤 Characters</h1>
        <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
          <ul className="space-y-1">
            {filteredCharacters.slice(0, 20).map((char: any) => (
              <li key={char.name}>
                <Link
                  href={`/characters?name=${encodeURIComponent(char.name)}`}
                  className={`flex justify-between items-center hover:text-amber-400 transition-colors ${
                    selectedName === char.name ? 'text-amber-400' : 'text-slate-300'
                  }`}
                >
                  <span>{char.name}</span>
                  <span className="text-xs text-slate-500">
                    {char.mentioned_in?.length || 0}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Character Details */}
      <div className="md:col-span-2">
        {selectedName && mentions ? (
          <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
            <h2 className="text-2xl font-bold text-amber-400 mb-4">{selectedName}</h2>
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
                  <p className="text-slate-500 text-sm mt-1 truncate">
                    {doc.content?.slice(0, 150)}...
                  </p>
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700 flex items-center justify-center h-64">
            <p className="text-slate-500">Select a character to see where they're mentioned</p>
          </div>
        )}
      </div>
    </div>
  );
}
