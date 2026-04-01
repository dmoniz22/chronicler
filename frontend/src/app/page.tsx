import Link from "next/link";
import { fetchStats, fetchDocuments, fetchCharacters, fetchLocations, fetchElements } from "@/lib/api";

export const dynamic = 'force-dynamic';

async function getData() {
  const [stats, documents, characters, locations, elements] = await Promise.all([
    fetchStats(),
    fetchDocuments(),
    fetchCharacters(),
    fetchLocations(),
    fetchElements()
  ]);
  return { stats, documents, characters, locations, elements };
}

export default async function Home() {
  const { stats, documents, characters, locations, elements } = await getData();

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-amber-400 mb-2">
          The Etheria Chronicles
        </h1>
        <p className="text-slate-400 text-lg">
          Your AI-powered fantasy writing companion
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard 
          title="Documents" 
          value={stats.documents} 
          icon="📄" 
          href="/documents"
        />
        <StatCard 
          title="Characters" 
          value={stats.characters} 
          icon="👤" 
          href="/characters"
          note="Including aliases"
        />
        <StatCard 
          title="Locations" 
          value={stats.locations} 
          icon="🏰" 
          href="/locations"
        />
        <StatCard 
          title="Elements" 
          value={stats.elements} 
          icon="✨" 
          href="/elements"
        />
      </div>

      {/* Quick Access */}
      <div className="grid md:grid-cols-3 gap-6">
        {/* Recent Documents */}
        <Card title="📖 Recent Documents">
          <ul className="space-y-2">
            {documents.slice(0, 5).map((doc: any) => (
              <li key={doc.path}>
                <Link 
                  href={`/documents?path=${encodeURIComponent(doc.path)}`}
                  className="text-slate-300 hover:text-amber-400 block truncate"
                >
                  {doc.title}
                </Link>
              </li>
            ))}
          </ul>
          <Link href="/documents" className="text-amber-400 text-sm mt-4 inline-block hover:underline">
            View all documents →
          </Link>
        </Card>

        {/* Elements */}
        <Card title="✨ The Five Elements">
          <div className="flex flex-wrap gap-2">
            {elements.map((elem: any) => (
              <Link
                key={elem.name}
                href={`/elements?name=${elem.name}`}
                className="px-3 py-1 bg-slate-700 rounded-full text-sm text-slate-200 hover:bg-amber-600 hover:text-white transition-colors"
              >
                {elem.name}
              </Link>
            ))}
          </div>
          <p className="text-slate-500 text-sm mt-3">
            Earth · Fire · Water · Wind · Spirit
          </p>
        </Card>

        {/* Key Locations */}
        <Card title="🏰 Key Locations">
          <ul className="space-y-2">
            {locations.slice(0, 5).map((loc: any) => (
              <li key={loc.name}>
                <Link 
                  href={`/locations?name=${loc.name}`}
                  className="text-slate-300 hover:text-amber-400"
                >
                  {loc.name}
                </Link>
                <span className="text-slate-500 text-xs ml-2">
                  ({loc.mentioned_in?.length || 0} refs)
                </span>
              </li>
            ))}
          </ul>
        </Card>
      </div>

      {/* Features */}
      <Card title="🚀 Features" gradient>
        <div className="grid md:grid-cols-3 gap-4">
          <Link href="/possession" className="p-4 bg-slate-800/50 rounded-lg hover:bg-slate-700/50 transition-colors">
            <h3 className="font-semibold text-amber-400 mb-2">🎭 Possession Chamber</h3>
            <p className="text-slate-400 text-sm">
              Chat with your characters directly. AI embodies Alatha, Fidomar, or any character.
            </p>
          </Link>
          <Link href="/ideaforge" className="p-4 bg-slate-800/50 rounded-lg hover:bg-slate-700/50 transition-colors">
            <h3 className="font-semibold text-amber-400 mb-2">⚒️ Idea Forge</h3>
            <p className="text-slate-400 text-sm">
              Generate town names, character ideas, plot seeds, and magic techniques.
            </p>
          </Link>
          <div className="p-4 bg-slate-800/50 rounded-lg opacity-60">
            <h3 className="font-semibold text-slate-400 mb-2">🔍 Consistency Oracle</h3>
            <p className="text-slate-500 text-sm">
              Check your drafts for timeline and magic system contradictions.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}

function StatCard({ title, value, icon, href, note }: { 
  title: string; 
  value: number; 
  icon: string;
  href: string;
  note?: string;
}) {
  return (
    <Link href={href} className="block">
      <div className="bg-slate-800/50 backdrop-blur rounded-xl p-6 border border-slate-700 hover:border-amber-500/50 transition-colors">
        <div className="flex items-center justify-between">
          <span className="text-3xl">{icon}</span>
          <span className="text-3xl font-bold text-white">{value}</span>
        </div>
        <p className="text-slate-400 mt-2">{title}</p>
        {note && <p className="text-slate-500 text-xs">{note}</p>}
      </div>
    </Link>
  );
}

function Card({ title, children, gradient }: { 
  title: string; 
  children: React.ReactNode;
  gradient?: boolean;
}) {
  return (
    <div className={`rounded-xl p-6 border ${
      gradient 
        ? 'bg-gradient-to-br from-amber-900/20 to-slate-800 border-amber-500/30' 
        : 'bg-slate-800/50 border-slate-700'
    }`}>
      <h2 className="text-lg font-semibold text-white mb-4">{title}</h2>
      {children}
    </div>
  );
}
