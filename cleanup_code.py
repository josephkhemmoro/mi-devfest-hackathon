#!/usr/bin/env python3
import os
import re
from pathlib import Path

def remove_comments_from_python(content):
    lines = content.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('#') and not stripped.startswith('#!'):
            continue
        if stripped.startswith('"""') and stripped.endswith('"""') and len(stripped) > 6:
            continue
        if stripped == '"""':
            continue
        cleaned_lines.append(line)
    
    result = '\n'.join(cleaned_lines)
    result = re.sub(r'"""[^"]*"""', '', result, flags=re.DOTALL)
    result = re.sub(r"'''[^']*'''", '', result, flags=re.DOTALL)
    return result

def remove_comments_from_tsx(content):
    result = re.sub(r'//[^\n]*', '', content)
    result = re.sub(r'/\*.*?\*/', '', result, flags=re.DOTALL)
    result = re.sub(r'{/\*.*?\*/}', '', result, flags=re.DOTALL)
    return result

def clean_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if filepath.endswith('.py'):
            cleaned = remove_comments_from_python(content)
        elif filepath.endswith(('.tsx', '.ts', '.jsx', '.js')):
            cleaned = remove_comments_from_tsx(content)
        else:
            return
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        
        print(f"✓ Cleaned: {filepath}")
    except Exception as e:
        print(f"✗ Error cleaning {filepath}: {e}")

def main():
    base_dir = Path(__file__).parent
    
    python_files = list(base_dir.glob('backend/**/*.py'))
    ts_files = list(base_dir.glob('frontend/src/**/*.tsx')) + list(base_dir.glob('frontend/src/**/*.ts'))
    
    all_files = python_files + ts_files
    
    print(f"Found {len(all_files)} files to clean")
    print(f"  - {len(python_files)} Python files")
    print(f"  - {len(ts_files)} TypeScript/TSX files")
    print()
    
    for filepath in all_files:
        if 'node_modules' in str(filepath) or '__pycache__' in str(filepath):
            continue
        clean_file(str(filepath))
    
    print(f"\nCompleted cleaning {len(all_files)} files")

if __name__ == "__main__":
    main()
