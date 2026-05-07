#!/usr/bin/env python3
"""Obsidian Memory Sync"""

import os
from datetime import datetime

VAULT = "/root/.obsidian"

def save_note(folder: str, title: str, content: str):
    """Save a note to Obsidian vault"""
    filepath = f"{VAULT}/{folder}/{title}_{datetime.now().strftime('%Y%m%d')}.md"
    with open(filepath, 'w') as f:
        f.write(f"# {title}\n\n{content}")
    print(f"✅ Saved: {filepath}")
    return filepath

def save_change(title: str, content: str):
    """Save important change"""
    return save_note("Changes", title, content)

def save_memory(content: str, topic: str = "General"):
    """Save to memory"""
    return save_note("Memory", topic, content)

def read_notes(folder: str = "Memory", limit: int = 5):
    """Read recent notes"""
    path = f"{VAULT}/{folder}"
    files = sorted(os.listdir(path), reverse=True)[:limit]
    notes = []
    for f in files:
        if f.endswith('.md'):
            with open(f"{path}/{f}", 'r') as file:
                notes.append(file.read())
    return notes

if __name__ == "__main__":
    # Test
    save_change("Test Change", "This is a test note from OpenClaw")
    print("✅ Obsidian memory ready!")
