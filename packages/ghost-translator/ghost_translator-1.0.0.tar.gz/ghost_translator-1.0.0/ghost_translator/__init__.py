#!/usr/bin/env python

import re
import os
import json
import sys
import operator
from glob import glob
from termcolor import colored

def merge_dicts(x, y):
    z = x.copy()
    z.update( (k, y[k]) for k in x.keys() & y.keys() )
    return z

def find_translations(file):
    p1 = re.compile(r'\{\{\s*t\s*["\'](.*?)["\']\s*\}\}')
    p2 = re.compile(r'\(\s*t\s*["\'](.*?)["\']\s*\)')

    filename = "default.hbs"
    textfile = open(file, 'r')
    filetext = textfile.read()
    textfile.close()

    m1 = re.findall(p1, filetext)
    m2 = re.findall(p2, filetext)
    return m1+m2

def main():

    hbs_files = glob('*.hbs')
    if len(hbs_files) == 0:
        print(colored("Found no .hbs files. This command must be run from a theme folder","yellow"))
        sys.exit(0)

    # Find all keys in .hbs files
    ignore_dirs = ['node_modules','.git']
    matches = []
    for root, dirs, files in os.walk("."):
        if any(x in root for x in ignore_dirs):
            continue
        for file in files:
            if file.endswith(".hbs"):
                path = root+'/'+file
                file_matches = find_translations(path)
                matches += file_matches

    if len(matches) == 0:
        print(colored("Found no translations for this theme",yellow))
        sys.exit(0)


    matches = list(set(matches))
    translation_files = glob('locales/*.json')

    # If no translations are already present, make one
    if len(translation_files) == 0:
        translations = { e:e for e in matches }

        # Store file
        with open('locales/en.json', 'w') as f:
            json.dump(translations, f, indent=4, sort_keys=True)



    # If they are merge the existing files and the new keys


    for file in translation_files:
        found = { e:"" for e in matches }
        # Open file
        with open(file, 'r') as f:
            existing = json.load(f)

        print(file)
        for t in list(set(found.keys()) - set(existing.keys())):
            print(" - "+colored(t, 'yellow'))

        for t in list(set(existing.keys()) - set(found.keys())):
            print(" - "+colored(t, 'red'))

        translations = merge_dicts(found,existing)

        with open(file, 'w') as f:
            json.dump(translations, f, indent=4, sort_keys=True)
