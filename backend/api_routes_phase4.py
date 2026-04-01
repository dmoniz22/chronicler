# Phase 4 API Routes - add to api.py
from datetime import datetime
import frontmatter

class CreateDocRequest(BaseModel):
    title: str
    content: str
    doc_type: str = "note"
    frontmatter: dict = {}

class UpdateDocRequest(BaseModel):
    content: str
    append: bool = False

@app.post("/documents/create")
async def api_create_doc(request: CreateDocRequest):
    folder_map = {"character": "Characters", "location": "Towns", 
                  "chapter": "Book 1 The Awakening Spark/Chapters",
                  "worldbuilding": "Worldbuilding", "series-meta": "Series", "note": "."}
    folder = folder_map.get(request.doc_type, ".")
    safe = "".join(c for c in request.title if c.isalnum() or c in " -_").strip()
    filepath = Path(VAULT_PATH) / folder / f"{safe}.md"
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    fm = {"title": request.title, "date_created": datetime.now().isoformat(), 
          "type": request.doc_type, **request.frontmatter}
    post = frontmatter.Post(request.content, **fm)
    with open(filepath, 'w') as f:
        f.write(frontmatter.dumps(post))
    
    with driver.session() as session:
        session.run("MERGE (d:Document {path: $path}) SET d.title=$t,d.type=$ty,d.content=$c",
                   path=str(filepath), t=request.title, ty=request.doc_type, c=request.content[:8000])
    return {"success": True, "path": str(filepath)}

@app.get("/sync/status")
async def api_sync_status():
    vault = Path(VAULT_PATH)
    fs_files = set(str(f) for f in vault.rglob("*.md") if '.obsidian' not in str(f))
    with driver.session() as session:
        neo_files = set(r['path'] for r in session.run("MATCH (d:Document) RETURN d.path as path"))
    return {"total_files": len(fs_files), "indexed": len(neo_files), 
            "synced": fs_files == neo_files, "missing": list(fs_files - neo_files)[:5]}
