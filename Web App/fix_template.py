import re

with open('templates/studio.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the broken STUDIO_DATA script section
pattern = r'(<script>\s*\n\s*//\s*Set each field individually.*?</script>)'
match = re.search(pattern, content, re.DOTALL)

if not match:
    # Try another pattern
    pattern = r'(<script>\s*\n\s*window\.STUDIO_DATA.*?</script>)'
    match = re.search(pattern, content, re.DOTALL)

if match:
    old_section = match.group(0)
    print(f"Found section ({len(old_section)} chars)")
    
    # Replace with a clean JSON approach that avoids Jinja/JS brace conflicts
    new_section = '''<script id="studioJSON" type="application/json">
{
    "designId": {{ design.id }},
    "faceUrls": {{ face_urls | tojson }},
    "roomType": {{ design.room_type | tojson }},
    "style": {{ design.style | tojson }},
    "aiOutput": {{ ai_output | tojson }},
    "placements": {{ placements | tojson }},
    "csrfToken": {{ csrf_token() | tojson }}
}
</script>
<script>
    try {
        window.STUDIO_DATA = JSON.parse(document.getElementById('studioJSON').textContent);
    } catch(e) {
        console.error('[Studio] Failed to parse STUDIO_DATA JSON:', e);
        window.STUDIO_DATA = { designId: 0, faceUrls: {}, roomType: 'living_room', style: 'modern', aiOutput: {}, placements: [], csrfToken: '' };
    }
    console.log('[Studio] faceUrls:', JSON.stringify(window.STUDIO_DATA.faceUrls));
</script>'''
    
    content = content.replace(old_section, new_section)
    with open('templates/studio.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: Replaced with JSON approach")
else:
    print("ERROR: Could not find STUDIO_DATA script section")
    for i, line in enumerate(content.split('\n')):
        if 'STUDIO_DATA' in line or 'studioData' in line.lower():
            print(f"L{i+1}: {line.strip()}")
