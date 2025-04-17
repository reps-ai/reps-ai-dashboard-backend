import re
from typing import List, Dict, Optional

def parse_transcript_block(block: str) -> List[Dict[str, str]]:
    """
    Parse a transcript block (with 'Agent:' and 'User:' markers) into a list of utterances.
    Each utterance is a dict with 'speaker' and 'text'.
    """
    if not block or not isinstance(block, str):
        return []
    # Split on Agent: or User: (case-insensitive), keep the delimiter
    parts = re.split(r'(Agent:|User:)', block)
    transcript = []
    current_speaker = None
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if part in ("Agent:", "User:"):
            # Map 'Agent:' to 'agent', 'User:' to 'customer'
            current_speaker = "agent" if part == "Agent:" else "customer"
        else:
            if current_speaker:
                transcript.append({
                    "speaker": current_speaker,
                    "text": part
                })
    return transcript 