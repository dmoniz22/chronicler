#!/usr/bin/env python3
"""
Idea Forge v2 - Content generators for Chronicler
"""

import random
from typing import List, Dict
from neo4j import GraphDatabase


class IdeaForge:
    def __init__(self, driver):
        self.driver = driver

    ELEMENTS = ["Fire", "Water", "Earth", "Wind", "Spirit"]

    # === TOWN GENERATOR ===
    def generate_towns(self, element: str = None, count: int = 3) -> List[Dict]:
        """Generate town/city ideas."""
        results = []
        elems = [element] if element else self.ELEMENTS

        prefixes = {
            "Fire": ["Cinder", "Ember", "Pyro", "Ash", "Forge", "Kindle", "Scorch"],
            "Water": ["Aqua", "Tide", "River", "Mist", "Deep", "Flow", "Ocean"],
            "Earth": ["Stone", "Terra", "Granite", "Quarry", "Clay", "Ridge", "Core"],
            "Wind": ["Zephyr", "Gale", "Breeze", "Sky", "Vent", "Whisper", "Strata"],
            "Spirit": ["Lumina", "Soul", "Aura", "Essence", "Psyche", "Ethereal", "Sage"]
        }
        suffixes = ["gate", "haven", "brook", "hold", "reach", "vale", "spire", "watch", "wood"]

        for _ in range(count):
            elem = random.choice(elems)
            name = random.choice(prefixes[elem]) + random.choice(suffixes)

            descriptions = {
                "Fire": f"{name} sits near volcanic vents. Heat rises through streets, glassblowers work day and night.",
                "Water": f"{name} sits where rivers meet. Canals replace roads, boats glide between buildings.",
                "Earth": f"{name} carved into cliff faces. Terraced farms climb upward, crystal mines run deep.",
                "Wind": f"High altitude {name}. Swaying rope bridges connect towers, messengers train here.",
                "Spirit": f"Quiet {name}. Meditation gardens, contemplative citizens, temples to all elements."
            }

            results.append({
                "name": name,
                "element": elem,
                "type": random.choice(["city", "town", "village"]),
                "description": descriptions[elem]
            })

        return results

    # === CHARACTER GENERATOR ===
    def generate_characters(self, element: str = None, role: str = None, count: int = 3) -> List[Dict]:
        """Generate character concepts."""
        results = []
        elems = [element] if element else self.ELEMENTS
        roles = [role] if role else ["ally", "mentor", "rival", "antagonist", "neutral"]

        first = ["Al", "El", "Ca", "Ve", "Ign", "Zeph", "Lyr", "Bri", "Cor", "Syl"]
        second = ["atha", "ora", "ius", "on", "el", "ys", "ael", "is", "ine", "os"]

        traits_by_elem = {
            "Fire": ["passionate", "impulsive", "energetic"],
            "Water": ["adaptable", "mysterious", "calm"],
            "Earth": ["steadfast", "practical", "reliable"],
            "Wind": ["intellectual", "restless", "unpredictable"],
            "Spirit": ["contemplative", "balanced", "intuitive"]
        }

        for _ in range(count):
            elem = random.choice(elems)
            traits = random.sample(traits_by_elem[elem], 2)

            results.append({
                "name": random.choice(first) + random.choice(second),
                "element": elem,
                "role": random.choice(roles),
                "traits": traits,
                "concept": f"A {', '.join(traits)} {elem.lower()} elementalist"
            })

        return results

    # === MAGIC TECHNIQUES ===
    def generate_magic_techniques(self, element: str = None, difficulty: str = None, count: int = 3) -> List[Dict]:
        """Generate technique ideas."""
        results = []
        elems = [element] if element else self.ELEMENTS
        diffs = [difficulty] if difficulty else ["basic", "intermediate", "advanced", "master"]

        technique_bases = {
            "Fire": ["Ignition", "Combustion", "Ember", "Flame", "Heat", "Ash", "Spark"],
            "Water": ["Mist", "Current", "Tide", "Wave", "Brine", "Flow", "Deep"],
            "Earth": ["Stone", "Crystal", "Quake", "Barrier", "Vein", "Core", "Shield"],
            "Wind": ["Gust", "Whisper", "Draft", "Cyclone", "Gale", "Zephyr", "Breeze"],
            "Spirit": ["Aura", "Essence", "Vital", "Soul", "Psyche", "Bind", "Harmony"]
        }

        types = ["Weave", "Bend", "Walk", "Form", "Sense", "Channel", "Mastery"]

        for _ in range(count):
            elem = random.choice(elems)
            diff = random.choice(diffs)

            base = random.choice(technique_bases[elem])
            tech_type = random.choice(types)
            name = f"{base} {tech_type}"

            # Detail based on difficulty
            if diff == "basic":
                detail = f"Simple {elem.lower()} manipulation. Foundation technique."
            elif diff == "intermediate":
                detail = f"Complex {elem.lower()} technique requiring control and focus."
            elif diff == "advanced":
                detail = f"Powerful {elem.lower()} application. Dangerous if misused."
            else:
                detail = f"Legendary {elem.lower()} mastery. Few achieve this level."

            results.append({
                "name": name,
                "element": elem,
                "difficulty": diff,
                "description": detail
            })

        return results

    # === PLOT SEEDS ===
    def generate_plot_seeds(self, element: str = None, count: int = 3) -> List[Dict]:
        """Generate plot hooks and story ideas."""
        results = []
        elems = [element] if element else self.ELEMENTS

        templates = [
            "A rogue {elem} elementalist has discovered forbidden {elem} techniques and is teaching them in secret.",
            "The {elem} House at the Citadel is in crisis - their elemental source has been corrupted.",
            "A {elem} settlement is under siege by {enemy} artifacts from the old wars.",
            "An ancient {elem} technique, thought lost, reappears in the form of a mysterious scroll.",
            "Two {elem} elementalists with opposing ideologies threaten war.",
            "A child shows impossible {elem} talent - mastering in days what takes years.",
            "The {elem} rituals have stopped working, and no one knows why.",
            "An exile returns with new {elem} knowledge that could change everything."
        ]

        for _ in range(count):
            elem = random.choice(elems)
            enemy = random.choice([e for e in self.ELEMENTS if e != elem])

            template = random.choice(templates)
            plot = template.format(elem=elem.lower(), enemy=enemy.lower())

            results.append({
                "plot": plot,
                "element": elem,
                "type": random.choice(["minor", "major", "campaign", "side quest"])
            })

        return results


# === API INTEGRATION ===
_idea_forge = None


def get_idea_forge(driver):
    global _idea_forge
    if _idea_forge is None:
        _idea_forge = IdeaForge(driver)
    return _idea_forge
