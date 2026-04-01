# MODEL_PLAN.md — Chronicler

## Central Policy Reference
See the canonical model strategy at:
`/home/dmoniz/.openclaw/workspace-coding/MODEL_PLAN.md`

## Per-Repo Defaults
- **Primary model:** `openrouter/qwen/qwen3.5-35b-a3b`
- **Fallbacks (in order):**
  1. `openrouter/minimax-m2`
  2. `openrouter/kimi-k2.5`
  3. `openrouter/mimi-v2`
- **Switching policy:** priority (prefer primary; fallback if unavailable)

## Project-Specific Notes
- Chronicler's AI features (idea generation, character chat) use Ollama or OpenRouter at runtime
- This plan governs development assistance model choice, not the user-facing AI
- User-facing AI model config should be managed in the app's own settings/env
- For complex Obsidian sync debugging or Neo4j query issues, consider Claude Sonnet 4.5

## How to Update
1. Edit this file with new primary/fallback choices
2. Commit and push
3. Central policy remains unchanged unless you also update the workspace MODEL_PLAN.md
