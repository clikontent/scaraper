import re
from datetime import datetime

def clean(text):
    if not text:
        return None
    return re.sub(r"\s+", " ", text).strip()

def to_iso(dt=None):
    if not dt:
        return datetime.utcnow().isoformat()
    return datetime.utcnow().isoformat()
