import os
import re

emojis = [
    '🏎', '⚙', '📊', '⚡', '▶', '↺', '⬆', '🏁', '💨', '🔵', '🔄', '📂', '✓', '🏎️'
]

# Additional ones just in case
emojis += ['🏁', '🚗', '📉', '📈', '🚀', '🔥']

def remove_emojis_from_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        for e in emojis:
            # Also remove trailing space if it exists after the emoji
            content = content.replace(e + ' ', '')
            content = content.replace(e, '')
            
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Removed emojis from {filepath}")
    except Exception as e:
        print(f"Skipping {filepath}: {e}")

for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.py') or file.endswith('.md'):
            # Don't modify the script itself
            if file == 'remove_emojis.py':
                continue
            filepath = os.path.join(root, file)
            remove_emojis_from_file(filepath)

print("Done.")
