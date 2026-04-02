import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Link from "next/link";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Chronicler - Etheria Writing Companion",
  description: "Your AI-powered fantasy writing assistant for The Etheria Chronicles",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
          <nav className="border-b border-slate-700 bg-slate-900/50 backdrop-blur">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex items-center justify-between h-16">
                <div className="flex items-center space-x-8">
                  <Link href="/" className="text-xl font-bold text-amber-400">
                    🔮 Chronicler
                  </Link>
                  <div className="flex space-x-4">
                    <NavLink href="/">Dashboard</NavLink>
                    <NavLink href="/documents">Documents</NavLink>
                    <NavLink href="/characters">Characters</NavLink>
                    <NavLink href="/locations">Locations</NavLink>
                    <NavLink href="/elements">Elements</NavLink>
                    <NavLink href="/possession">Possession</NavLink>
                    <NavLink href="/ideaforge">Idea Forge</NavLink>
                    <NavLink href="/settings">Settings</NavLink>
                  </div>
                </div>
              </div>
            </div>
          </nav>
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}

function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <Link
      href={href}
      className="text-slate-300 hover:text-amber-400 transition-colors px-3 py-2 rounded-md text-sm font-medium"
    >
      {children}
    </Link>
  );
}
