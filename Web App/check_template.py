with open('templates/studio.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Write lines 204-225 to see the new content
with open('debug_lines.txt', 'w', encoding='utf-8') as f:
    for i in range(203, min(230, len(lines))):
        f.write(f"L{i+1}: {lines[i]}")

with open('debug_lines.txt', 'r', encoding='utf-8') as f:
    print(f.read())
