#!/usr/bin/env python3
import glob, json, os

files = [f for f in glob.glob('**/dockerfile', recursive=True)]
files.sort()
matrix = []
for f in files:
    dirpath = os.path.dirname(f)
    name = dirpath.replace('./','').lstrip('.')
    if name == '':
        name = 'root'
    name = name.replace('/','-')
    matrix.append({ 'path': f, 'name': name })
print(json.dumps(matrix))
