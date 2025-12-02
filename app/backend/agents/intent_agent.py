import json
from app.core.state import State
from datetime import datetime, timedelta
from langgrpah.prebuilt import create_react_agent

def intent_agent(state: State = {}):
    today = datetime.now().date()
    thirty_days_ago = today - timedelta(days=30)

    safety_prompt = """
        First, you MUST perform a Safety Classification on the user message.

        Check if the content contains any of the following:
        - Sexual / pornographic content
        - Violence or threats
        - Hate speech, racism, slurs, harassment
        - Criminal intent (drugs, hacking, fraud, weapons, explosives)
        - Self-harm or suicide
        - Strong profanity
        - Any harmful or antisocial content

        If ANY of these categories match:
            Immediately return ONLY this JSON:
            {
                "intent": "unsafe_content_detected",
                "needs_clarification": True,
                "missing_information": "",
                "findings": "User content flagged as unsafe: <CATEGORY>"
            }
        Do NOT proceed to intent detection.
    """
