#!/usr/bin/env python3
"""
Idea Forge - Content generation system for Chronicler
Generates towns, characters, plot ideas, magic techniques based on your world
"""

import os
import random
from typing import List, Dict
from neo4j import GraphDatabase

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
DEFAULT_MODEL = "openchat/openchat-7b"  # Free model for generation


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

    def generate_town_names(self, element: str = None, location_type: str = "town", count: int = 5) -> List[Dict]:
        """Generate town names based on element affinity."""
        results = []

        # Get context from existing towns in vault
        with self.driver.session() as session:
            existing = session.run("""
                MATCH (l:Location)<-[:MENTIONS]-(d:Document)
                WHERE l.name CONTAINS $type OR d.title CONTAINS 'Town' OR d.title CONTAINS 'City'
                RETURN l.name as name LIMIT 20
            """, {"type": location_type}).data()
            existing_names = [r["name"] for r in existing]

        elements = [element] if element else list(self.ELEMENT_PREFIXES.keys())

        for _ in range(count):
            elem = random.choice(elements)
            prefix = random.choice(self.ELEMENT_PREFIXES[elem])
            suffix = random.choice(self.LOCATION_SUFFIXES[location_type])

            # Combine creatively
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
        """Generate a brief description for a generated town."""
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
