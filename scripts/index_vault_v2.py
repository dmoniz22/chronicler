#!/usr/bin/env python3
"""
Chronicler Vault Indexer v2 - Fixed Version
Simple indexer with _backup folder exclusion
"""

import os
import re
import sys
from pathlib import Path
from typing import Optional
import frontmatter
from neo4j import GraphDatabase

VAULT_PATH = "/home/dmoniz/Documents/obsidian/Obsidian/Etheria/The Ehteria Chronicles"
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "chronicler123"

STOP_WORDS = {
    'the', 'she', 'her', 'his', 'him', 'they', 'them', 'their', 'this', 'that',
    'when', 'then', 'what', 'where', 'which', 'who', 'why', 'how',
    'gathering', 'enclave', 'test', 'testing', 'impact', 'battle', 'types',
    'evolution', 'planning', 'discovery', 'trials', 'rumors', 'whispers'
}

KNOWN_CHARACTERS = {
    'Alatha', 'Fidomar', 'Elora', 'Ignatius', 'Galen', 'Vesta', 'Lyria',
    'Zephyros', 'Brannor', 'Terra', 'Caelum', 'Silverbrook', 'Evershade',
    'Headmaster Galen', 'Master Ignatius', 'Mistress Vesta'
}


def index_vault():
    print("🚀 Starting Chronicler Indexer v2")
    
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    vault = Path(VAULT_PATH)
    
    if not vault.exists():
        print(f"❌ Vault not found at {VAULT_PATH}")
        sys.exit(1)
    
    # Clear and init
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        print("🧹 Database cleared")
        
        # Constraints
        try:
            session.run("CREATE CONSTRAINT doc_path IF NOT EXISTS FOR (d:Document) REQUIRE d.path IS UNIQUE")
            session.run("CREATE CONSTRAINT char_name IF NOT EXISTS FOR (c:Character) REQUIRE c.name IS UNIQUE")
            session.run("CREATE CONSTRAINT loc_name IF NOT EXISTS FOR (l:Location) REQUIRE l.name IS UNIQUE")
            session.run("CREATE CONSTRAINT elem_name IF NOT EXISTS FOR (e:Element) REQUIRE e.name IS UNIQUE")
        except:
            pass
    
    processed = 0
    
    # Walk files (excluding backup/hidden)
    for md_file in vault.rglob("*.md"):
        path_str = str(md_file)
        if any(x in path_str for x in ['.obsidian', '.trash', '_backup', 'templates']):
            continue
        
        try:
            with open(md_file, 'r') as f:
                content = f.read()
            
            # Parse frontmatter
            try:
                post = frontmatter.loads(content)
                title = post.metadata.get('title', md_file.stem)
                body = post.content
            except:
                title = md_file.stem
                body = content
            
            # Determine type
            rel_path = str(md_file.relative_to(vault))
            doc_type = 'note'
            if 'Characters' in rel_path:
                doc_type = 'character'
            elif 'Towns' in rel_path:
                doc_type = 'location'
            elif 'Chapters' in rel_path:
                doc_type = 'chapter'
            elif 'Worldbuilding' in rel_path:
                doc_type = 'worldbuilding'
            
            # Create document node
            with driver.session() as session:
                session.run("""
                    MERGE (d:Document {path: $path})
                    SET d.title = $title, d.type = $type, d.content = $content,
                        d.relative_path = $rel_path, d.full_length = $length
                """, {
                    'path': path_str, 'title': title, 'type': doc_type,
                    'content': body[:5000], 'rel_path': rel_path, 'length': len(body)
                })
                
                # Extract known characters
                for char in KNOWN_CHARACTERS:
                    if char in body:
                        session.run("""
                            MERGE (c:Character {name: $name})
                            WITH c
                            MATCH (d:Document {path: $doc_path})
                            MERGE (d)-[:MENTIONS]->(c)
                        """, name=char, doc_path=path_str)
                
                # Extract elements
                for elem in ['Earth', 'Fire', 'Water', 'Wind', 'Spirit']:
                    if elem in body:
                        session.run("""
                            MERGE (e:Element {name: $name})
                            WITH e
                            MATCH (d:Document {path: $doc_path})
                            MERGE (d)-[:MENTIONS]->(e)
                        """, name=elem, doc_path=path_str)
            
            processed += 1
            if processed % 5 == 0:
                print(f"  Processed {processed} files...")
                
        except Exception as e:
            print(f"  ⚠️ Error: {e}")
    
    # Summary
    with driver.session() as session:
        docs = session.run("MATCH (d:Document) RETURN count(d)").single()[0]
        chars = session.run("MATCH (c:Character) RETURN count(c)").single()[0]
        locs = session.run("MATCH (l:Location) RETURN count(l)").single()[0]
        elems = session.run("MATCH (e:Element) RETURN count(e)").single()[0]
        
        print(f"\n✅ Indexing complete!")
        print(f"   Documents: {docs}")
        print(f"   Characters: {chars}")
        print(f"   Locations: {locs}")
        print(f"   Elements: {elems}")
    
    driver.close()


if __name__ == "__main__":
    index_vault()
