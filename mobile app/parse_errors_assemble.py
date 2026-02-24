import sys

lines = open('build_log_assemble.txt', encoding='utf-16le').readlines()
with open('errors_only_assemble.txt', 'w', encoding='utf-8') as f:
    for line in lines:
        if 'e: ' in line or 'Unresolved reference' in line or 'Type mismatch' in line:
            f.write(line.strip() + '\n')
