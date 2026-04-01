#!/usr/bin/env python3
"""
Possession Chamber - Character embodiment system for Chronicler
"""

import os
from typing import List, Dict, Optional
from pydantic import BaseModel
from neo4j import GraphDatabase

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
DEFAULT_MODEL = "mistralai/mistral-small"  # Low cost, good for creative writing

class CharacterContext:
    """Builds context for a character from the vault."""
    
    def __init__(self, driver):
        self.driver = driver
    
    def get_character_info(self, character_name: str) -> Dict:
        """Fetch character details from Neo4j and vault files."""
        with self.driver.session() as session:
            # Get character mentions
            result = session.run("""
                MATCH (c:Character {name: $name})<-[:MENTIONS]-(d:Document)
                RETURN d.title as title, d.path as path, d.content as content
            """, {"name": character_name})
            
            documents = [dict(record) for record in result]
            
            # Try to find dedicated character file
            char_file = None
            for doc in documents:
                if character_name.lower() in doc["title"].lower() and "character" in doc["title"].lower():
                    char_file = doc
                    break
            
            return {
                "name": character_name,
                "documents": documents,
                "profile": char_file["content"] if char_file else "",
                "mentioned_count": len(documents)
            }


class PossessionEngine:
    """Core engine for character embodiment."""
    
    # Character persona templates
    PERSONA_TEMPLATES = {
        "Alatha": """You are Alatha, protagonist of The Elemental Citadel series.

BACKGROUND:
- New graduate of the Citadel with Spirit House training
- From rural Westmarch farming community
- Recently discovered you can control ALL five elements (Earth, Fire, Water, Wind, Spirit)
- This is considered impossible/impossible by Citadel teaching
- Currently trying to hide this ability while understanding it

PERSONALITY:
- Restless, energetic, impulsive
- Feels like an imposter among contemplative Spirit adepts
- Deeply loyal to friends (Fidomar, Elora)
- Struggles with hiding your true nature
- Farm-girl practicality mixed with newfound power
- Can be reckless when frustrated

VOICE:
- Youthful, occasionally formal when nervous (Spirit House training)
- Drops into rural dialect when emotional
- Asks questions, challenges assumptions
- Speaks with energy and movement

CURRENT STATE:
- Still processing the discovery at graduation
- Worried about the Enclave
- Uncertain about your assignment to Silverbrook
- Desperate to practice your abilities without being discovered

Respond in first person as Alatha. Be authentic to her voice and circumstances.""",
        
        "Fidomar": """You are Fidomar, Alatha's best friend and fellow Citadel graduate.

BACKGROUND:
- Earth elementalist, graduated alongside Alatha
- Assigned to Stonebridge
- Steady, grounded, reliable
- Known for his calm demeanor and physical strength
- Comes from a mountainous region

PERSONALITY:
- Rock-steady, calm under pressure
- The voice of reason to Alatha's impulsiveness
- Loyal to a fault
- Protective of friends
- Sometimes hides his own concerns to support others

VOICE:
- Measured, deliberate speech
- Occasionally dry humor
- Reassuring tone
- Speak in simple, direct terms

CURRENT STATE:
- Worried about Alatha after the convergence anomaly
- Wants to help her but doesn't know what she needs
- Planning to stay in touch despite assignments

Respond in first person as Fidomar. Be steady, supportive, grounded.""",
        
        "Elora": """You are Elora, Alatha's best female friend and fellow graduate.

BACKGROUND:
- Wind elementalist from Windmere
- Quick-witted, agile, independent
- Graduated with Alatha and Fidomar
- Notices details others miss
- Light on her feet, light with her words

PERSONALITY:
- Playful but perceptive
- Tends to make jokes when nervous
- Observant - picks up on things others miss
- Free-spirited but deeply cares for friends
- Sometimes uses humor to deflect serious conversations

VOICE:
- Quick, breezy delivery
- Playful teasing tone
- Occasional jumping between thoughts
- Laughter comes easily

CURRENT STATE:
- Excited about her assignment
- Sensed something was off with Alatha at graduation
- Planning to write frequently

Respond in first person as Elora. Be light, perceptive, playful but caring."""
    }
    
    def __init__(self, driver):
        self.driver = driver
        self.context_builder = CharacterContext(driver)
        self.chat_histories: Dict[str, List[Dict]] = {}
    
    def get_system_prompt(self, character_name: str) -> str:
        """Build system prompt for character embodiment."""
        # Check for known character template
        if character_name in self.PERSONA_TEMPLATES:
            return self.PERSONA_TEMPLATES[character_name]
        
        # Otherwise build from vault data
        char_info = self.context_builder.get_character_info(character_name)
        
        # Build generic prompt from documents
        docs_summary = "\n".join([
            f"- Mentioned in: {doc['title']}"
            for doc in char_info["documents"][:5]
        ])
        
        return f"""You are {character_name} from The Elemental Citadel fantasy series.

CHARACTER CONTEXT:
{char_info.get('profile', 'No detailed profile available.')}

APPEARANCES:
{docs_summary}

Respond in first person as this character. Stay true to their voice, personality, and worldview based on the source material. Be immersive and authentic."""
    
    async def chat(self, character_name: str, user_message: str, session_id: str = "default") -> str:
        """Process a chat message in character."""
        import aiohttp
        
        # Get or initialize chat history
        history_key = f"{session_id}_{character_name}"
        if history_key not in self.chat_histories:
            self.chat_histories[history_key] = []
        
        history = self.chat_histories[history_key]
        
        # Build system prompt
        system_prompt = self.get_system_prompt(character_name)
        
        # Build messages for OpenRouter
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add history (last 10 messages)
        for msg in history[-10:]:
            messages.append(msg)
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        # Call OpenRouter
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:8503",
                    "X-Title": "Chronicler - Etheria Writing Companion"
                },
                json={
                    "model": DEFAULT_MODEL,
                    "messages": messages,
                    "temperature": 0.8,
                    "max_tokens": 500
                }
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenRouter error: {error_text}")
                
                result = await response.json()
                assistant_message = result["choices"][0]["message"]["content"]
                
                # Store in history
                history.append({"role": "user", "content": user_message})
                history.append({"role": "assistant", "content": assistant_message})
                
                # Keep only last 20 messages
                self.chat_histories[history_key] = history[-20:]
                
                return assistant_message
    
    def clear_history(self, character_name: str, session_id: str = "default"):
        """Clear chat history for a character."""
        history_key = f"{session_id}_{character_name}"
        if history_key in self.chat_histories:
            del self.chat_histories[history_key]
    
    def get_available_characters(self) -> List[str]:
        """Get list of characters available for possession."""
        with self.driver.session() as session:
            result = session.run(
                "MATCH (c:Character) RETURN c.name as name ORDER BY c.name"
            )
            return [record["name"] for record in result]


# Global possession engine instance
_possession_engine = None

def get_possession_engine(driver):
    """Get or create possession engine singleton."""
    global _possession_engine
    if _possession_engine is None:
        _possession_engine = PossessionEngine(driver)
    return _possession_engine