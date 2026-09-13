"""Normalize explicitly named AA thinking settings, not provider capabilities."""
import re

def thinking_level(name):
    # Effort is an AA parenthetical qualifier. 'Qwen3.8 Max' is a model
    # product name, not evidence of a max thinking setting.
    text = ' '.join(re.findall(r'\(([^)]*)\)', name)).lower()
    # Non-reasoning takes precedence over e.g. 'Non-reasoning, High Effort'.
    if re.search(r'non[- ]reasoning|no reasoning', text):
        return 'none'
    if re.search(r'\b(xhigh|extra[- ]high)\b', text):
        return 'xhigh'
    for level in ('max', 'high', 'medium', 'low', 'minimal'):
        if re.search(r'\b' + level + r'\b', text):
            return level
    if re.search(r'\b(reasoning|thinking)\b', text):
        return 'unspecified'
    return 'unspecified'

THINKING_STYLES = {
    'none': ('s', 'No reasoning'),
    'minimal': ('1', 'Minimal'),
    'low': ('v', 'Low'),
    'medium': ('D', 'Medium'),
    'high': ('^', 'High'),
    'xhigh': ('P', 'Extra high'),
    'max': ('*', 'Max'),
    'unspecified': ('o', 'Unknown/unspecified'),
}
