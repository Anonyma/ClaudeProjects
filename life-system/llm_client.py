"""
LLM Client for Life Management System

Uses Claude (Anthropic) for intelligent responses.
Set ANTHROPIC_API_KEY env var to enable.
"""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Check if Anthropic is available
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("anthropic package not installed - LLM features disabled")


class LLMClient:
    def __init__(self):
        self.api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        self.enabled = bool(self.api_key) and ANTHROPIC_AVAILABLE
        self.client = None

        if self.enabled:
            self.client = anthropic.Anthropic(api_key=self.api_key)
            logger.info("LLM client initialized with Claude")
        else:
            if not self.api_key:
                logger.info("ANTHROPIC_API_KEY not set - LLM features disabled")

    async def generate_reflection_feedback(
        self,
        reflection: dict,
        user_context: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate personalized feedback on a reflection.
        Returns None if LLM is not available.
        """
        if not self.enabled:
            return None

        # Build prompt from reflection data
        reflection_summary = []
        if reflection.get("accomplishments"):
            reflection_summary.append(f"Accomplishments: {', '.join(reflection['accomplishments'])}")
        if reflection.get("overall_mood"):
            reflection_summary.append(f"Mood: {reflection['overall_mood']}")
        if reflection.get("energy_pattern"):
            reflection_summary.append(f"Energy: {reflection['energy_pattern']}")
        if reflection.get("focus_quality"):
            reflection_summary.append(f"Focus: {reflection['focus_quality']}/5")
        if reflection.get("struggled_with"):
            reflection_summary.append(f"Struggles: {', '.join(reflection['struggled_with'])}")
        if reflection.get("wins"):
            reflection_summary.append(f"Win: {reflection['wins']}")
        if reflection.get("one_thing_tomorrow"):
            reflection_summary.append(f"Tomorrow's focus: {reflection['one_thing_tomorrow']}")

        system_prompt = """You are a supportive, practical life coach.
Your style is 60% practical advice, 25% direct accountability, 15% gentle inquiry.
Keep responses brief (2-3 sentences max). Be warm but not cheesy.
Focus on patterns and actionable insights."""

        if user_context:
            system_prompt += f"\n\nUser context: {user_context}"

        user_message = f"End of day reflection:\n{chr(10).join(reflection_summary)}\n\nGive brief, personalized feedback."

        try:
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",  # Fast and cheap for quick feedback
                max_tokens=150,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return None

    async def generate_morning_insight(
        self,
        recent_reflections: list,
        today_calendar: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate a personalized morning insight based on recent patterns.
        """
        if not self.enabled:
            return None

        if not recent_reflections:
            return None

        # Summarize recent patterns
        moods = [r.get("overall_mood") for r in recent_reflections if r.get("overall_mood")]
        focus_scores = [r.get("focus_quality") for r in recent_reflections if r.get("focus_quality")]
        struggles = []
        for r in recent_reflections:
            struggles.extend(r.get("struggled_with", []))

        context = f"""Recent patterns (last {len(recent_reflections)} days):
- Moods: {', '.join(moods) if moods else 'no data'}
- Focus avg: {sum(focus_scores)/len(focus_scores):.1f}/5 if focus_scores else 'no data'
- Common struggles: {', '.join(set(struggles)[:3]) if struggles else 'none noted'}"""

        if today_calendar:
            context += f"\n\nToday's calendar: {today_calendar}"

        try:
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=100,
                system="You're a brief, practical morning coach. One actionable insight only.",
                messages=[{"role": "user", "content": f"{context}\n\nOne quick insight for today:"}]
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return None

    async def chat(self, message: str, context: Optional[str] = None) -> Optional[str]:
        """
        General chat with the LLM for freeform conversations.
        """
        if not self.enabled:
            return None

        system = """You are Z's life management assistant. Be practical, direct, and brief.
You help with productivity, accountability, and life organization.
Keep responses concise - you're in a Telegram chat, not writing essays."""

        if context:
            system += f"\n\nContext about Z: {context}"

        try:
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=200,
                system=system,
                messages=[{"role": "user", "content": message}]
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return None


# Singleton instance
_llm_client = None

def get_llm_client() -> LLMClient:
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
