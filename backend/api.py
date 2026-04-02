#!/usr/bin/env python3
"""
Chronicler API - FastAPI backend for the Etheria Writing Companion
"""

import os
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from neo4j import GraphDatabase

# Configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "chronicler123"
VAULT_PATH = "/home/dmoniz/Documents/obsidian/Obsidian/Etheria/The Ehteria Chronicles"

app = FastAPI(title="Chronicler API", version="0.1.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# === Models ===


class Document(BaseModel):
    path: str
    title: str
    type: str
    relative_path: str
    content: str
    full_length: int


class Character(BaseModel):
    name: str
    mentioned_in: List[str] = []


class Location(BaseModel):
    name: str
    mentioned_in: List[str] = []


class Element(BaseModel):
    name: str


class SearchResult(BaseModel):
    type: str
    title: str
    path: str
    preview: str


# === API Routes ===


@app.get("/")
async def root():
    return {"message": "Chronicler API - Etheria Writing Companion", "version": "0.1.0"}


@app.get("/documents", response_model=List[Document])
async def get_documents(doc_type: Optional[str] = None):
    """Get all documents, optionally filtered by type."""
    with driver.session() as session:
        if doc_type:
            result = session.run(
                "MATCH (d:Document {type: $type}) RETURN d.path as path, d.title as title, d.type as type, d.relative_path as relative_path, d.content as content, d.full_length as full_length",
                {"type": doc_type},
            )
        else:
            result = session.run(
                "MATCH (d:Document) RETURN d.path as path, d.title as title, d.type as type, d.relative_path as relative_path, d.content as content, d.full_length as full_length"
            )
        return [dict(record) for record in result]


@app.get("/documents/{document_id:path}")
async def get_document(document_id: str):
    """Get a specific document by path. Reads full content from filesystem."""
    from urllib.parse import unquote_plus

    # Decode URL-encoded characters
    # unquote_plus handles both %20 and + as spaces
    decoded_path = unquote_plus(document_id)
    # Only prepend / if not already present (avoid //home/... when %2F decoded)
    path = decoded_path if decoded_path.startswith("/") else "/" + decoded_path

    # Get metadata from Neo4j
    with driver.session() as session:
        result = session.run(
            "MATCH (d:Document {path: $path}) RETURN d", {"path": path}
        )
        record = result.single()
        if not record:
            raise HTTPException(status_code=404, detail="Document not found")
        doc = dict(record["d"])

    # Read full content from filesystem (vault is source of truth)
    file_path = Path(path)
    if file_path.exists():
        try:
            raw = file_path.read_text()
            post = frontmatter.loads(raw)
            doc["content"] = post.content
            doc["frontmatter"] = post.metadata
            doc["full_length"] = len(post.content)
        except Exception:
            doc["content"] = file_path.read_text()
            doc["frontmatter"] = {}
            doc["full_length"] = len(doc["content"])

    return doc


@app.get("/characters", response_model=List[Character])
async def get_characters():
    """Get all characters."""
    with driver.session() as session:
        result = session.run("""
            MATCH (c:Character)
            OPTIONAL MATCH (d:Document)-[:MENTIONS]->(c)
            WITH c, collect(DISTINCT d.title) as docs
            RETURN c.name as name, docs as mentioned_in
            ORDER BY size(docs) DESC
        """)
        return [dict(record) for record in result]


@app.get("/locations", response_model=List[Location])
async def get_locations():
    """Get all locations."""
    with driver.session() as session:
        result = session.run("""
            MATCH (l:Location)
            OPTIONAL MATCH (d:Document)-[:MENTIONS]->(l)
            WITH l, collect(DISTINCT d.title) as docs
            RETURN l.name as name, docs as mentioned_in
            ORDER BY size(docs) DESC
        """)
        return [dict(record) for record in result]


@app.get("/elements", response_model=List[Element])
async def get_elements():
    """Get all elements."""
    with driver.session() as session:
        result = session.run("MATCH (e:Element) RETURN e.name as name")
        return [dict(record) for record in result]


@app.get("/search")
async def search(q: str, limit: int = 10):
    """Search documents by title or content."""
    with driver.session() as session:
        result = session.run(
            """
            MATCH (d:Document)
            WHERE d.title CONTAINS $query OR d.content CONTAINS $query
            RETURN d.title as title, d.path as path, 
                   substring(d.content, 0, 200) as preview
            LIMIT $limit
        """,
            {"query": q, "limit": limit},
        )
        return [dict(record) for record in result]


@app.get("/entity/{entity_type}/{entity_name}")
async def get_entity(entity_type: str, entity_name: str):
    """Get all documents mentioning a specific entity."""
    with driver.session() as session:
        if entity_type == "character":
            result = session.run(
                """
                MATCH (c:Character {name: $name})<-[:MENTIONS]-(d:Document)
                RETURN d.title as title, d.path as path, d.content as content
            """,
                {"name": entity_name},
            )
        elif entity_type == "location":
            result = session.run(
                """
                MATCH (l:Location {name: $name})<-[:MENTIONS]-(d:Document)
                RETURN d.title as title, d.path as path, d.content as content
            """,
                {"name": entity_name},
            )
        elif entity_type == "element":
            result = session.run(
                """
                MATCH (e:Element {name: $name})<-[:MENTIONS]-(d:Document)
                RETURN d.title as title, d.path as path, d.content as content
            """,
                {"name": entity_name},
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid entity type")
        return [dict(record) for record in result]


@app.get("/stats")
async def get_stats():
    """Get knowledge graph statistics."""
    with driver.session() as session:
        docs = session.run("MATCH (d:Document) RETURN count(d) as count").single()
        chars = session.run("MATCH (c:Character) RETURN count(c) as count").single()
        locs = session.run("MATCH (l:Location) RETURN count(l) as count").single()
        elems = session.run("MATCH (e:Element) RETURN count(e) as count").single()

        return {
            "documents": docs["count"],
            "characters": chars["count"],
            "locations": locs["count"],
            "elements": elems["count"],
        }


# === Possession Chamber (Phase 2) ===

import sys

sys.path.insert(0, "/home/dmoniz/projects/chronicler/backend")
from possession import get_possession_engine, CharacterContext

# Initialize possession engine
possession_engine = get_possession_engine(driver)


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    character: str
    response: str


@app.get("/possession/characters")
async def get_available_characters():
    """Get list of characters available for possession."""
    # Return hardcoded list of well-known characters with detailed profiles
    return {
        "characters": [
            {
                "name": "Alatha",
                "description": "Protagonist. Multi-elementalist from Westmarch. Restless, impulsive, hiding her true power.",
                "status": "ready",
                "affinity": "All Five Elements",
            },
            {
                "name": "Fidomar",
                "description": "Alatha's best friend. Earth elementalist. Steady, loyal, the voice of reason.",
                "status": "ready",
                "affinity": "Earth",
            },
            {
                "name": "Elora",
                "description": "Alatha's best friend. Wind elementalist. Playful, perceptive, quick-witted.",
                "status": "ready",
                "affinity": "Wind",
            },
        ]
    }


@app.post("/possession/{character_name}/chat", response_model=ChatResponse)
async def chat_with_character(character_name: str, request: ChatRequest):
    """Chat with a possessed character."""
    try:
        response = await possession_engine.chat(
            character_name=character_name,
            user_message=request.message,
            session_id=request.session_id,
        )
        return ChatResponse(character=character_name, response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@app.post("/possession/{character_name}/clear")
async def clear_character_chat(character_name: str, session_id: str = "default"):
    """Clear chat history for a character."""
    possession_engine.clear_history(character_name, session_id)
    return {"message": f"Chat history cleared for {character_name}"}


@app.get("/possession/{character_name}/context")
async def get_character_context(character_name: str):
    """Get context documents for a character."""
    context_builder = CharacterContext(driver)
    return context_builder.get_character_info(character_name)


# === Background Tasks ===


# === Idea Forge (Phase 3) ===
from idea_forge_v2 import get_idea_forge

# Initialize Idea Forge
idea_forge = get_idea_forge(driver)


@app.get("/idea-forge/towns")
async def generate_towns(element: str = None, count: int = 3):
    """Generate town/city ideas."""
    results = idea_forge.generate_towns(element=element, count=count)
    return {"towns": results}


@app.get("/idea-forge/characters")
async def generate_characters(element: str = None, role: str = None, count: int = 3):
    """Generate character ideas."""
    results = idea_forge.generate_characters(element=element, role=role, count=count)
    return {"characters": results}


@app.get("/idea-forge/magic-techniques")
async def generate_techniques(
    element: str = None, difficulty: str = None, count: int = 3
):
    """Generate magic technique ideas."""
    results = idea_forge.generate_magic_techniques(
        element=element, difficulty=difficulty, count=count
    )
    return {"techniques": results}


@app.get("/idea-forge/plot-seeds")
async def generate_plots(element: str = None, count: int = 3):
    """Generate plot seed ideas."""
    results = idea_forge.generate_plot_seeds(element=element, count=count)
    return {"plots": results}


# === Phase 4: Two-Way Sync ===
import frontmatter
from datetime import datetime


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
    """Create new document in vault and index in Neo4j."""
    try:
        folder_map = {
            "character": "Characters",
            "location": "Towns",
            "chapter": "Book 1 The Awakening Spark/Chapters",
            "worldbuilding": "Worldbuilding",
            "series-meta": "Series",
            "note": ".",
        }
        folder = folder_map.get(request.doc_type, ".")
        safe_title = "".join(
            c for c in request.title if c.isalnum() or c in " -_"
        ).strip()
        filepath = Path(VAULT_PATH) / folder / f"{safe_title}.md"
        filepath.parent.mkdir(parents=True, exist_ok=True)

        fm = {
            "title": request.title,
            "date_created": datetime.now().isoformat(),
            "type": request.doc_type,
            **request.frontmatter,
        }

        post = frontmatter.Post(request.content, **fm)
        filepath.write_text(frontmatter.dumps(post))

        with driver.session() as session:
            session.run(
                """
                MERGE (d:Document {path: $path})
                SET d.title=$title, d.type=$type, d.content=$content,
                    d.relative_path=$rel_path, d.full_length=$length
            """,
                {
                    "path": str(filepath),
                    "title": request.title,
                    "type": request.doc_type,
                    "content": request.content[:8000],
                    "rel_path": str(filepath.relative_to(Path(VAULT_PATH))),
                    "length": len(request.content),
                },
            )

        return {"success": True, "path": str(filepath), "title": request.title}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/documents/{doc_path:path}/update")
async def api_update_doc(doc_path: str, request: UpdateDocRequest):
    """Update existing document."""
    try:
        full_path = Path(doc_path)
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="Document not found")

        existing = full_path.read_text()
        try:
            post = frontmatter.loads(existing)
            metadata, old_content = post.metadata, post.content
        except:
            metadata, old_content = {}, existing

        new_content = (
            old_content + "\n\n" + request.content
            if request.append
            else request.content
        )
        metadata["date_modified"] = datetime.now().isoformat()

        post = frontmatter.Post(new_content, **metadata)
        full_path.write_text(frontmatter.dumps(post))

        with driver.session() as session:
            session.run(
                """
                MATCH (d:Document {path: $path})
                SET d.content=$content, d.full_length=$length
            """,
                {
                    "path": doc_path,
                    "content": new_content[:8000],
                    "length": len(new_content),
                },
            )

        return {"success": True, "message": "Document updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sync/status")
async def api_sync_status():
    """Check sync status between vault and Neo4j."""
    try:
        vault = Path(VAULT_PATH)
        fs_files = set(
            str(f)
            for f in vault.rglob("*.md")
            if ".obsidian" not in str(f)
            and ".trash" not in str(f)
            and "_backup" not in str(f)
        )

        with driver.session() as session:
            result = session.run(
                "MATCH (d:Document) RETURN d.path as path, d.full_length as length"
            )
            neo_files = {r["path"]: r["length"] for r in result}

        only_in_fs = [p for p in fs_files if p not in neo_files]
        only_in_neo = [p for p in neo_files if p not in fs_files]
        divergent = [
            p
            for p in fs_files
            if p in neo_files and Path(p).stat().st_size != neo_files.get(p, 0)
        ]

        return {
            "filesystem_count": len(fs_files),
            "neo4j_count": len(neo_files),
            "only_in_filesystem": only_in_fs[:5],
            "only_in_neo4j": only_in_neo[:5],
            "size_divergent": divergent[:5],
            "in_sync": len(only_in_fs) == 0
            and len(only_in_neo) == 0
            and len(divergent) == 0,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sync/reindex")
async def api_reindex():
    """Re-index vault to Neo4j."""
    import subprocess

    try:
        result = subprocess.run(
            ["python", "scripts/index_vault_v3.py"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd="/home/dmoniz/projects/chronicler",
        )
        return {"success": result.returncode == 0, "output": result.stdout[-1000:]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8004)


# === Settings ===
import os as _os

ENV_PATH = "/home/dmoniz/projects/chronicler/.env"


class SettingsRequest(BaseModel):
    provider: str = "openrouter"
    openrouter_api_key: str = ""
    openrouter_model: str = "openai/gpt-4o-mini"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "gemma3:12b"


@app.get("/settings")
async def get_settings():
    """Read current settings from .env."""
    settings = {
        "provider": "openrouter",
        "openrouter_api_key": "",
        "openrouter_model": "openai/gpt-4o-mini",
        "ollama_url": "http://localhost:11434",
        "ollama_model": "gemma3:12b",
    }
    if Path(ENV_PATH).exists():
        for line in Path(ENV_PATH).read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key == "OPENROUTER_API_KEY":
                    settings["openrouter_api_key"] = value
                elif key == "OPENROUTER_MODEL":
                    settings["openrouter_model"] = value
                elif key == "AI_PROVIDER":
                    settings["provider"] = value
                elif key == "OLLAMA_URL":
                    settings["ollama_url"] = value
                elif key == "OLLAMA_MODEL":
                    settings["ollama_model"] = value
    # Mask the API key for display
    if settings["openrouter_api_key"]:
        key = settings["openrouter_api_key"]
        settings["openrouter_api_key_masked"] = (
            key[:8] + "..." + key[-4:] if len(key) > 12 else "***"
        )
    else:
        settings["openrouter_api_key_masked"] = ""
    return settings


@app.post("/settings")
async def save_settings(req: SettingsRequest):
    """Write settings to .env."""
    env_keys = {
        "AI_PROVIDER": req.provider,
        "OPENROUTER_API_KEY": req.openrouter_api_key,
        "OPENROUTER_MODEL": req.openrouter_model,
        "OLLAMA_URL": req.ollama_url,
        "OLLAMA_MODEL": req.ollama_model,
    }
    lines = []
    seen = set()
    if Path(ENV_PATH).exists():
        for line in Path(ENV_PATH).read_text().splitlines():
            stripped = line.strip()
            if stripped.startswith("#") or not stripped:
                lines.append(line)
            elif "=" in stripped:
                key = stripped.split("=", 1)[0].strip()
                if key in env_keys:
                    lines.append(f"{key}={env_keys[key]}")
                    seen.add(key)
                else:
                    lines.append(line)
            else:
                lines.append(line)
    for key, value in env_keys.items():
        if key not in seen:
            lines.append(f"{key}={value}")
    Path(ENV_PATH).write_text("\n".join(lines) + "\n")
    # Reload env for modules that use it
    for key, value in env_keys.items():
        _os.environ[key] = value
    return {"success": True, "message": "Settings saved"}


@app.get("/settings/models")
async def list_models():
    """List available models for the configured provider."""
    provider = _os.environ.get("AI_PROVIDER", "openrouter")
    if provider == "ollama":
        from ai_client import list_ollama_models

        ollama_url = _os.environ.get("OLLAMA_URL", "http://localhost:11434")
        models = await list_ollama_models(ollama_url)
        return {
            "provider": "ollama",
            "models": [{"id": m, "name": m, "cost": "Free"} for m in models],
        }
    else:
        return {
            "provider": "openrouter",
            "models": [
                {"id": "openai/gpt-4o-mini", "name": "GPT-4o Mini", "cost": "Low"},
                {"id": "openai/gpt-4o", "name": "GPT-4o", "cost": "Medium"},
                {
                    "id": "anthropic/claude-3.5-sonnet",
                    "name": "Claude 3.5 Sonnet",
                    "cost": "Medium",
                },
                {
                    "id": "google/gemini-pro-1.5",
                    "name": "Gemini Pro 1.5",
                    "cost": "Medium",
                },
                {
                    "id": "meta-llama/llama-3.1-405b-instruct",
                    "name": "Llama 3.1 405B",
                    "cost": "Medium",
                },
                {
                    "id": "meta-llama/llama-3.1-70b-instruct",
                    "name": "Llama 3.1 70B",
                    "cost": "Low",
                },
                {
                    "id": "mistralai/mistral-large",
                    "name": "Mistral Large",
                    "cost": "Medium",
                },
                {
                    "id": "mistralai/mistral-small",
                    "name": "Mistral Small",
                    "cost": "Low",
                },
                {"id": "deepseek/deepseek-chat", "name": "DeepSeek V3", "cost": "Low"},
            ],
        }


@app.post("/settings/test")
async def test_api_connection():
    """Test the configured AI provider."""
    from ai_client import test_provider

    return await test_provider()


# === AI Idea Forge ===


class AIGenerateRequest(BaseModel):
    category: str  # towns, characters, magic, plots
    prompt: str = ""
    element: str = ""
    count: int = 3


@app.post("/idea-forge/ai-generate")
async def ai_generate_ideas(req: AIGenerateRequest):
    """Generate ideas using AI with context from the vault."""
    from ai_client import call_ai, get_settings as _get_ai_settings
    import json as _json

    ai_settings = _get_ai_settings()
    provider = ai_settings["provider"]

    # Build world context from Neo4j
    with driver.session() as session:
        chars = session.run(
            "MATCH (c:Character) RETURN c.name as name ORDER BY c.name"
        ).data()
        locs = session.run(
            "MATCH (l:Location) RETURN l.name as name ORDER BY l.name"
        ).data()
        elems = session.run(
            "MATCH (e:Element) RETURN e.name as name ORDER BY e.name"
        ).data()
        docs = session.run(
            "MATCH (d:Document) RETURN d.title as title, d.content as content LIMIT 5"
        ).data()

    char_names = ", ".join(c["name"] for c in chars) or "None yet"
    loc_names = ", ".join(l["name"] for l in locs) or "None yet"
    elem_names = (
        ", ".join(e["name"] for e in elems) or "Earth, Fire, Water, Wind, Spirit"
    )
    doc_samples = "\n\n".join(
        f"--- {d['title']} ---\n{(d['content'] or '')[:500]}" for d in docs
    )

    category_prompts = {
        "towns": f"""Generate {req.count} unique fantasy town/city ideas for the world of Etheria.
Each should have: a name, which element it's aligned with, its type (city/town/village), and a vivid 2-3 sentence description.
Make the names cohesive with the existing world. Return as JSON array: [{{"name":"...","element":"...","type":"...","description":"..."}},...]""",
        "characters": f"""Generate {req.count} unique character concepts for the world of Etheria.
Each should have: a name, element affinity, role (ally/mentor/rival/antagonist/neutral), 2 personality traits, and a 1-2 sentence concept description.
Avoid duplicating existing characters. Return as JSON array: [{{"name":"...","element":"...","role":"...","traits":["...","..."],"concept":"..."}},...]""",
        "magic": f"""Generate {req.count} unique magic techniques for the world of Etheria's elemental system.
Each should have: a name, element, difficulty (basic/intermediate/advanced/master), and a 2-3 sentence description of what it does and how it feels to use.
Return as JSON array: [{{"name":"...","element":"...","difficulty":"...","description":"..."}},...]""",
        "plots": f"""Generate {req.count} unique plot seeds or story hooks for the world of Etheria.
Each should have: the plot description (2-3 sentences), primary element involved, and type (minor/major/campaign/side quest).
Build on existing characters and locations. Return as JSON array: [{{"plot":"...","element":"...","type":"..."}},...]""",
    }

    system_prompt = f"""You are a creative writing assistant for a fantasy novel series called "The Etheria Chronicles".
The world has five elements: Earth, Fire, Water, Wind, and Spirit. Elementalists can control these elements.
The Citadel is the main institution training elementalists, organized into five Houses.

EXISTING CHARACTERS: {char_names}
EXISTING LOCATIONS: {loc_names}
ELEMENTS: {elem_names}

SAMPLE DOCUMENTS FROM THE VAULT:
{doc_samples[:2000]}

Generate content that is consistent with this world, avoids duplicating existing names, and feels cohesive.
Return ONLY valid JSON, no markdown fences or explanation."""

    user_prompt = category_prompts.get(req.category, category_prompts["plots"])
    if req.prompt:
        user_prompt += f"\n\nAdditional direction from the author: {req.prompt}"
    if req.element:
        user_prompt += f"\n\nFocus on the {req.element} element."

    model_name = (
        ai_settings.get("ollama_model", "")
        if provider == "ollama"
        else ai_settings.get("openrouter_model", "")
    )

    try:
        content = await call_ai(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.8,
            max_tokens=1500,
        )

        clean = content.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1] if "\n" in clean else clean[3:]
        if clean.endswith("```"):
            clean = clean[:-3]
        clean = clean.strip()

        ideas = _json.loads(clean)
        return {
            "ideas": ideas,
            "category": req.category,
            "model": model_name,
            "provider": provider,
        }
    except _json.JSONDecodeError:
        return {
            "ideas": [],
            "category": req.category,
            "raw_response": content,
            "error": "Failed to parse JSON from AI response",
            "provider": provider,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
