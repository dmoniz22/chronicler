import Link from "next/link";
import { fetchLocations, fetchEntityMentions } from "@/lib/api";

export const dynamic = 'force-dynamic';

export default async function LocationsPage({ searchParams }: {
  searchParams: Promise<{ name?: string }>
}) {
  const locations = await fetchLocations();
  const params = await searchParams;
  const selectedName = params.name;

  const mentions = selectedName ? await fetchEntityMentions('location', selectedName) : null;

  return (
    <div className="grid md:grid-cols-3 gap-6">
      {/* Location List */}
      <div className="md:col-span-1 space-y-4">
        <h1 className="text-2xl font-bold text-white">🏰 Locations</h1>
        <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
          <ul className="space-y-1">
            {locations.map((loc: any) => (
              <li key={loc.name}>
                <Link
                  href={`/locations?name=${encodeURIComponent(loc.name)}`}
                  className={`flex justify-between items-center hover:text-amber-400 transition-colors ${
                    selectedName === loc.name ? 'text-amber-400' : 'text-slate-300'
                  }`}
                >
                  <span>{loc.name}</span>
                  <span className="text-xs text-slate-500">
                    {loc.mentioned_in?.length || 0}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Location Details */}
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
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700 flex items-center justify-center h-64">
            <p className="text-slate-500">Select a location to see where it's mentioned</p>
          </div>
        )}
      </div>
    </div>
  );
}
