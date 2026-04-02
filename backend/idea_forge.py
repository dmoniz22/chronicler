#!/usr/bin/env python3
"""
Idea Forge - Content generation system for Chronicler
Generates towns, characters, plot ideas, magic techniques based on your world
Uses AI for intelligent content generation.
"""

import os
import random
import json
from typing import List, Dict
from neo4j import GraphDatabase

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

# Load .env file for this project
try:
    from dotenv import load_dotenv
    load_dotenv('/home/dmoniz/projects/chronicler/.env')
    print("📖 Loaded .env file")
except ImportError:
    print("⚠️ python-dotenv not installed, skipping .env loading")
except Exception as e:
    print(f"⚠️ Could not load .env: {e}")

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
DEFAULT_MODEL = "openrouter/qwen/qwen3.5-35b-a3b"  # Use your primary model
FALLBACK_MODEL = "moldavid/chatgpt-4o-mini-2024-07-18"  # Fallback if needed

class IdeaForge:
    """Generate creative content for the Etheria Chronicles."""

    # Base naming conventions from vault
    ELEMENT_PREFIXES = {
        "Fire": ["Pyro", "Cinder", "Ember", "Flame", "Ash", "Ignis", "Blaze", "Sear", "Kindle", "Forge"],
        "Water": ["Aqua", "Marin", "Tide", "Mist", "River", "Ocean", "Brine", "Foam", "Deep", "Flow"],
        "Earth": ["Terra", "Stone", "Granite", "Clay", "Marl", "Quarry", "Mason", "Rock", "Ridge", "Ore"],
        "Wind": ["Aero", "Gale", "Zephyr", "Breeze", "Sky", "Cloud", "Strato", "Vent", "Whisper", "Gust"],
        "Spirit": ["Lumina", "Ethereal", "Soul", "Spirit", "Aura", "Essence", "Inner", "Vital", "Psyche", "Animus"]
    }

    LOCATION_SUFFIXES = {
        "city": ["thar", "ion", "don", "ia", "gate", "watch", "hold", "spire", "ara", "mere"],
        "town": ["reach", "wood", "haven", "hold", "vale", "brook", "ford", "wick", "stead", "bury"],
        "village": ["lyn", "shire", "ton", "ham", "by", "ley", "thorpe", "wick", "stead", "green"]
    }

    def __init__(self, driver):
        self.driver = driver
    
    def _call_ai(self, prompt: str, model: str = None) -> str:
        """Call OpenRouter AI for content generation."""
        if not OPENROUTER_API_KEY:
            return None
        
        if not HAS_HTTPX:
            return None
        
        model = model or DEFAULT_MODEL
        
        try:
            response = httpx.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a creative writing assistant for a fantasy novel world called Etheria. Generate creative, coherent, and thematically appropriate content."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.7,
                },
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"AI call failed: {e}")
            return None
    
    def _get_world_context(self) -> str:
        """Get current world state from Neo4j for AI context."""
        with self.driver.session() as session:
            # Get existing characters
            char_result = session.run("MATCH (c:Character) RETURN c.name as name LIMIT 20")
            characters = [r["name"] for r in char_result]
            
            # Get existing locations
            loc_result = session.run("MATCH (l:Location) RETURN l.name as name LIMIT 20")
            locations = [r["name"] for r in loc_result]
            
            # Get elements
            elem_result = session.run("MATCH (e:Element) RETURN e.name as name")
            elements = [r["name"] for r in elem_result]
            
            return f"""Existing characters: {', '.join(characters[:10]) if characters else 'None'}\n"
Existing locations: {', '.join(locations[:10]) if locations else 'None'}\n"
Elements in world: {', '.join(elements)}"""

    def generate_town_names(self, element: str = None, location_type: str = "town", count: int = 5) -> List[Dict]:
        """Generate town names based on element affinity using AI."""
        results = []
        
        # Get world context
        context = self._get_world_context()
        
        # Use AI to generate coherent names
        prompt = f"""Generate {count} unique fantasy town names for a fantasy world called Etheria. Each name should be appropriate for a {location_type} and optionally reflect the '{element}' element if provided.

Context (existing content to avoid duplicates):
{context}

Rules:
- Make names sound cohesive with each other
- Avoid duplicating existing names
- Return ONLY a JSON array of objects with "name" and "element" fields
- Example: [{{"name": "Cinderhold", "element": "Fire"}}, ...]

Generate {count} names:"""
        
        ai_response = self._call_ai(prompt)
        
        if ai_response:
            try:
                # Try to parse as JSON
                ai_names = json.loads(ai_response)
                for name_info in ai_names[:count]:
                    results.append({
                        "name": name_info.get("name", f"{random.choice(self.ELEMENT_PREFIXES.get(element, ['Stone']))}{random.choice(self.LOCATION_SUFFIXES.get(location_type, ['ton']))}"),
                        "element": name_info.get("element") or element or random.choice(list(self.ELEMENT_PREFIXES.keys())),
                        "type": location_type,
                        "suggested_description": "Generate description using AI for consistency with world setting"
                    })
                if results:
                    return results
            except:
                pass  # Fall back to traditional method
        
        # Fallback to traditional generation
        return self._generate_town_names_traditional(element, location_type, count)

    def _generate_town_names_traditional(self, element: str = None, location_type: str = "town", count: int = 5) -> List[Dict]:
        """Traditional generation method if AI fails."""
        results = []
        elements = [element] if element else list(self.ELEMENT_PREFIXES.keys())

        for _ in range(count):
            elem = random.choice(elements)
            prefix = random.choice(self.ELEMENT_PREFIXES[elem])
            suffix = random.choice(self.LOCATION_SUFFIXES[location_type])

            patterns = [
                f"{prefix}{suffix}",
                f"{prefix}{random.choice(self.LOCATION_SUFFIXES[location_type])}",
                f"{prefix} {location_type.title()}",
                f"{random.choice(['Old', 'New', 'High', 'Low', 'North', 'South', 'East', 'West'])} {prefix}{suffix}",
            ]
            name = random.choice(patterns)

            results.append({
                "name": name,
                "element": elem,
                "type": location_type,
                "suggested_description": self._generate_town_description(elem, name, location_type)
            })
        return results
    
    def _generate_town_description(self, element: str, name: str, loc_type: str) -> str:
        """Generate AI-powered town description."""
        context = self._get_world_context()
        prompt = f"""Write a single-paragraph description of the fantasy town '{name}' in the world of Etheria.
This town is aligned with the '{element}' element.

Context (for consistency):
{context}

Write 2-3 sentences describing what makes this town unique and its connection to the {element} element."""
        
        ai_desc = self._call_ai(prompt)
        if ai_desc:
            return ai_desc.strip()
        
        # Fallback to traditional descriptions
        descriptions = {
            "Fire": [
                f"A {loc_type} built around volcanic vents, famous for glassblowing and smithing.",
                f"Warm climate, constant smell of woodsmoke, Fire elementalists trained here.",
                f"Industrial center powered by magma channels running beneath streets."
            ],
            "Water": [
                f"Canals crisscross this {loc_type}, boats the main transport method.",
                f"Built on stilts over marshland, famous for healing springs.",
                f"Port {loc_type} where three rivers meet, fish markets line the docks."
            ],
            "Earth": [
                f"Carved into cliff face, terraced farms surround it.",
                f"Stone buildings with foundations older than the Citadel itself.",
                f"Mining {loc_type}, crystal veins visible in walls of homes."
            ],
            "Wind": [
                f"High altitude {loc_type}, bridges sway between towers.",
                f"Open architecture, no walls block the constant breeze.",
                f"Messengers and couriers trained here. Flags signal weather."
            ],
            "Spirit": [
                f"Quiet {loc_type}, many meditation gardens, contemplative citizens.",
                f"Site of ancient spiritual pilgrimage, temples to all elements.",
                f"Scholars study here, libraries famous throughout the realm."
            ]
        }
        return random.choice(descriptions.get(element, ["A typical settlement."]))

    def generate_character_ideas(self, element: str = None, role: str = None, count: int = 3) -> List[Dict]:
        """Generate character concepts."""
        results = []
        elements = [element] if element else list(self.ELEMENT_PREFIXES.keys())
        roles = [role] if role else ["ally", "mentor", "rival", "antagonist", "neutral"]

        # Name components
        first_parts = ["Al", "El", "Ca", "Sy", "Ve", "Tho", "Mar", "Ign", "Zeph", "Lyr", "Bri", "Cor", "Fae", "Nyx", "Ori"]
        second_parts = ["atha", "ora", "el", "ius", "on", "ia", "en", "ys", "ael", "is", "an", "el", "ine", "os"]

        traits_by_element = {
            "Fire": ["passionate", "impulsive", "creative", "temperamental", "energetic"],
            "Water": ["adaptable", "empathetic", "mysterious", "calm", "flowing"],
            "Earth": ["steadfast", "practical", "stubborn", "reliable", "grounded"],
            "Wind": ["free-spirited", "intellectual", "restless", "sharp", "unpredictable"],
            "Spirit": ["contemplative", "connective", "balanced", "intuitive", "serene"]
        }

        for _ in range(count):
            elem = random.choice(elements)
            char_role = random.choice(roles)

            # Generate name
            name = random.choice(first_parts) + random.choice(second_parts)
            if random.random() > 0.7:
                name += " " + random.choice([
                    "of " + random.choice(["the Hills", "the Vale", "Stonebridge", "Windmere", "Silverbrook"]),
                    random.choice(["the Bold", "the Wise", "the Young", "the Elder"])
                ])

            # Generate traits
            traits = random.sample(traits_by_element.get(elem, ["balanced"]), 2)

            # Generate concept based on role
            concepts = {
                "ally": [
                    f"A {elem.lower()} elementalist who mentors younger adepts.",
                    f"Former Citadel student who left to pursue {elem.lower()} arts independently.",
                    f"Traveling merchant with hidden {elem.lower()} abilities.",
                    f"Town blacksmith who secretly practices {elem.lower()} forging."
                ],
                "mentor": [
                    f"Master {elem} elementalist who runs an unconventional training school.",
                    f"Elder who discovered a lost {elem.lower()} technique during travels.",
                    f"Head of the {elem} House at the Citadel. Strict but fair.",
                    f"Retired adventurer with knowledge of multi-elemental combinations."
