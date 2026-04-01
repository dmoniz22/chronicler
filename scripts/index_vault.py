#!/usr/bin/env python3
"""
Chronicler Vault Indexer
Indexes the Etheria Obsidian vault into Neo4j knowledge graph.
"""

import os
import re
import sys
from pathlib import Path
from typing import Optional

import frontmatter
from neo4j import GraphDatabase

# Configuration
VAULT_PATH = "/home/dmoniz/Documents/obsidian/Obsidian/Etheria/The Ehteria Chronicles"
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "chronicler123"

class VaultIndexer:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        self.processed = 0
        self.entities = {
            'characters': [],
            'locations': [],
            'concepts': [],
            'documents': []
        }
        
    def init_schema(self):
        """Create Neo4j constraints and indexes."""
        with self.driver.session() as session:
            # Constraints
            session.run("CREATE CONSTRAINT document_path IF NOT EXISTS FOR (d:Document) REQUIRE d.path IS UNIQUE")
            session.run("CREATE CONSTRAINT character_name IF NOT EXISTS FOR (c:Character) REQUIRE c.name IS UNIQUE")
            session.run("CREATE CONSTRAINT location_name IF NOT EXISTS FOR (l:Location) REQUIRE l.name IS UNIQUE")
            session.run("CREATE CONSTRAINT element_name IF NOT EXISTS FOR (e:Element) REQUIRE e.name IS UNIQUE")
            
            # Indexes
            session.run("CREATE INDEX document_title IF NOT EXISTS FOR (d:Document) ON (d.title)")
            print("✅ Schema initialized")
    
    def extract_entities(self, content: str) -> dict:
        """Extract entities from content using patterns."""
        entities = {
            'characters': [],
            'locations': [],
            'elements': []
        }
        
        # Character patterns (capitalized names that appear multiple times)
        # Look for proper nouns with context clues
        char_patterns = [
            r'([A-Z][a-z]+) (?:of|from|the|said|replied|asked|thought)',
            r'([A-Z][a-z]+) (?:graduated|discovered|remembered|felt)',
            r'([A-Z][a-z]+)\'s',
        ]
        
        for pattern in char_patterns:
            matches = re.findall(pattern, content)
            entities['characters'].extend(matches)
        
        # Location patterns
        location_keywords = ['City', 'Town', 'Village', 'Citadel', 'Tower', 'Reach', 'Hold', 'Bridge']
        for keyword in location_keywords:
            pattern = rf'(\w*{keyword}\w*)'
            matches = re.findall(pattern, content)
            entities['locations'].extend(matches)
        
        # Element references
        elements = ['Earth', 'Fire', 'Water', 'Wind', 'Spirit']
        for element in elements:
            if element in content:
                entities['elements'].append(element)
        
        # Deduplicate
        entities['characters'] = list(set(entities['characters']))
        entities['locations'] = list(set(entities['locations']))
        entities['elements'] = list(set(entities['elements']))
        
        return entities
    
    def parse_file(self, file_path: Path) -> Optional[dict]:
        """Parse a markdown file and extract metadata."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter if exists
            try:
                post = frontmatter.loads(content)
                metadata = post.metadata
                body = post.content
            except:
                metadata = {}
                body = content
            
            # Extract title
            title = metadata.get('title', file_path.stem)
            if not title or title == '':
                # Try to extract from first h1
                h1_match = re.search(r'^# (.+)$', content, re.MULTILINE)
                if h1_match:
                    title = h1_match.group(1).strip()
                else:
                    title = file_path.stem
            
            # Extract entities
            entities = self.extract_entities(body)
            
            # File type detection
            file_type = 'note'
            if 'Character' in str(file_path) or 'character' in title.lower():
                file_type = 'character'
            elif 'Town' in str(file_path) or 'City' in str(file_path) or 'location' in title.lower():
                file_type = 'location'
            elif 'Chapter' in title:
                file_type = 'chapter'
            elif 'Book' in title and 'Book' in str(file_path):
                file_type = 'book'
            
            return {
                'path': str(file_path),
                'relative_path': str(file_path.relative_to(VAULT_PATH)),
                'title': title,
                'content': body[:5000],  # First 5000 chars for indexing
                'full_length': len(body),
                'metadata': metadata,
                'type': file_type,
                'entities': entities
            }
            
        except Exception as e:
            print(f"❌ Error parsing {file_path}: {e}")
            return None
    
    def create_document_node(self, doc: dict):
        """Create Neo4j nodes for document and linked entities."""
        with self.driver.session() as session:
            # Create Document node
            session.run("""
                MERGE (d:Document {path: $path})
                SET d.title = $title,
                    d.type = $type,
                    d.content = $content,
                    d.relative_path = $relative_path,
                    d.full_length = $full_length
            """, {
                'path': doc['path'],
                'title': doc['title'],
                'type': doc['type'],
                'content': doc['content'],
                'relative_path': doc['relative_path'],
                'full_length': doc['full_length']
            })
            
            # Create Character nodes and relationships
            for char in doc['entities']['characters']:
                if len(char) > 3 and not char.lower() in ['the', 'she', 'her', 'his', 'him']:
                    session.run("""
                        MERGE (c:Character {name: $name})
                        WITH c
                        MATCH (d:Document {path: $doc_path})
                        MERGE (d)-[:MENTIONS]->(c)
                    """, {'name': char, 'doc_path': doc['path']})
            
            # Create Location nodes
            for loc in doc['entities']['locations']:
                session.run("""
                    MERGE (l:Location {name: $name})
                    WITH l
                    MATCH (d:Document {path: $doc_path})
                    MERGE (d)-[:MENTIONS]->(l)
                """, {'name': loc, 'doc_path': doc['path']})
            
            # Create Element nodes
            for elem in doc['entities']['elements']:
                session.run("""
                    MERGE (e:Element {name: $name})
                    WITH e
                    MATCH (d:Document {path: $doc_path})
                    MERGE (d)-[:MENTIONS]->(e)
                """, {'name': elem, 'doc_path': doc['path']})
    
    def index_vault(self):
        """Main indexing process."""
        vault = Path(VAULT_PATH)
        
        if not vault.exists():
            print(f"❌ Vault not found at {VAULT_PATH}")
            sys.exit(1)
        
        print(f"🚀 Indexing vault: {VAULT_PATH}")
        print("=" * 60)
        
        # Clear existing data (optional - remove if you want incremental)
        # self._clear_database()
        
        self        
        self.init_schema()
        
        # Walk through all markdown files
        for md_file in vault.rglob("*.md"):
            # Skip hidden directories and trash
            if '.obsidian' in str(md_file) or '.trash' in str(md_file):
                continue
            
            doc = self.parse_file(md_file)
            if doc:
                self.create_document_node(doc)
                self.processed += 1
                
                if self.processed % 5 == 0:
                    print(f"  Processed {self.processed} files...")
        
        print(f"\n✅ Indexing complete!")
        print(f"   Total files processed: {self.processed}")
        
        # Print summary
        self._print_summary()
    
    def _print_summary(self):
        """Print index summary."""
        with self.driver.session() as session:
            # Count nodes
            docs = session.run("MATCH (d:Document) RETURN count(d) as count").single()
            chars = session.run("MATCH (c:Character) RETURN count(c) as count").single()
            locs = session.run("MATCH (l:Location) RETURN count(l) as count").single()
            elems = session.run("MATCH (e:Element) RETURN count(e) as count").single()
            
            print(f"\n📊 Graph Summary:")
            print(f"   Documents: {docs['count']}")
            print(f"   Characters: {chars['count']}")
            print(f"   Locations: {locs['count']}")
            print(f"   Elements: {elems['count']}")
            
            # Sample characters found
            sample_chars = session.run("MATCH (c:Character) RETURN c.name AS name LIMIT 10").data()
            if sample_chars:
                print(f"\n   Sample Characters: {', '.join([c['name'] for c in sample_chars])}")
    
    def close(self):
        self.driver.close()

def main():
    indexer = VaultIndexer()
    indexer.index_vault()
    indexer.close()

if __name__ == "__main__":
    main()
