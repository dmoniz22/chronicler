#!/usr/bin/env python3
"""
Phase 4: Two-Way Sync Module for Chronicler
Standalone module for sync functionality
"""

import os
import frontmatter
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from neo4j import GraphDatabase

VAULT_PATH = "/home/dmoniz/Documents/obsidian/Obsidian/Etheria/The Ehteria Chronicles"
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "chronicler123"


class VaultSync:
    """Two-way sync between Obsidian vault and Neo4j"""
    
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    def create_document(self, title: str, content: str, doc_type: str = "note", 
                       frontmatter_data: dict = None) -> dict:
        """Create a new document in the vault and index it."""
        folder_map = {
            "character": "Characters",
            "location": "Towns",
            "chapter": "Book 1 The Awakening Spark/Chapters",
            "worldbuilding": "Worldbuilding",
            "series-meta": "Series",
            "note": "."
        }
        folder = folder_map.get(doc_type, ".")
        
        # Create safe filename
        safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()
        filename = f"{safe_title}.md"
        filepath = Path(VAULT_PATH) / folder / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Build frontmatter
        fm = {
            "title": title,
            "date_created": datetime.now().isoformat(),
            "type": doc_type,
            **(frontmatter_data or {})
        }
        
        # Write to filesystem
        post = frontmatter.Post(content, **fm)
        with open(filepath, 'w') as f:
            f.write(frontmatter.dumps(post))
        
        # Index in Neo4j
        with self.driver.session() as session:
            session.run("""
                MERGE (d:Document {path: $path})
                SET d.title = $title, d.type = $type, d.content = $content,
                    d.relative_path = $rel_path, d.full_length = $length
            """, {
                'path': str(filepath),
                'title': title,
                'type': doc_type,
                'content': content[:8000],
                'rel_path': str(filepath.relative_to(Path(VAULT_PATH))),
                'length': len(content)
            })
        
        return {"success": True, "path": str(filepath), "title": title}
    
    def update_document(self, doc_path: str, content: str, append: bool = False) -> dict:
        """Update an existing document."""
        full_path = Path(doc_path)
        if not full_path.exists():
            raise FileNotFoundError(f"Document not found: {doc_path}")
        
        # Read existing
        with open(full_path, 'r') as f:
            existing = f.read()
        
        try:
            post = frontmatter.loads(existing)
            metadata, old_content = post.metadata, post.content
        except:
            metadata, old_content = {}, existing
        
        # Update content
        new_content = old_content + "\n\n" + content if append else content
        metadata['date_modified'] = datetime.now().isoformat()
        
        # Write back
        post = frontmatter.Post(new_content, **metadata)
        with open(full_path, 'w') as f:
            f.write(frontmatter.dumps(post))
        
        # Update Neo4j
        with self.driver.session() as session:
            session.run("""
                MATCH (d:Document {path: $path})
                SET d.content = $content, d.full_length = $length
            """, {'path': doc_path, 'content': new_content[:8000], 'length': len(new_content)})
        
        return {"success": True, "path": doc_path}
    
    def get_sync_status(self) -> dict:
        """Check sync status between vault and Neo4j."""
        vault = Path(VAULT_PATH)
        fs_files = {}
        
        # Scan filesystem
        for md_file in vault.rglob("*.md"):
            if any(x in str(md_file) for x in ['.obsidian', '.trash', '_backup']):
                continue
            stat = md_file.stat()
            fs_files[str(md_file)] = {'size': stat.st_size}
        
        # Get Neo4j state
        with self.driver.session() as session:
            result = session.run("MATCH (d:Document) RETURN d.path as path, d.full_length as length")
            neo_files = {r['path']: r['length'] for r in result}
        
        # Find differences
        only_in_fs = [p for p in fs_files if p not in neo_files]
        only_in_neo = [p for p in neo_files if p not in fs_files]
        
        return {
            "filesystem_count": len(fs_files),
            "neo4j_count": len(neo_files),
            "only_in_filesystem": only_in_fs[:5],
            "only_in_neo4j": only_in_neo[:5],
            "synced": len(fs_files) == len(neo_files),
            "ready": True
        }
    
    def close(self):
        self.driver.close()


# Simple test
if __name__ == "__main__":
    sync = VaultSync()
    status = sync.get_sync_status()
    print("Sync Status:", status)
    sync.close()
