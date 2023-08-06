#!/usr/bin/env python
import re
import sys

def parse(text):
    No = '([0-9]{1,5}-?[A|B|C|D]?\s)'
    CD = '([N|S|W|E|Nw|Sw|Ne|Se|West|South|North|East]\.?\s)?'  # cardinal direction
    street_main = '(([A-Z][a-z\&]*|[0-9]{1,3}(St|Nd|Rd|Th))\s?)'
    street_minor = '([A-Z][a-z\&]+\s)?'

    suffix = '('
    suffix += 'Avenue|avenue|Ave|ave|'
    suffix += 'Road|road|Rd|rd|'
    suffix += 'Street|street|St|st|'
    suffix += 'Way|way|'
    suffix += 'Drive|drive|Dr|dr|'
    suffix += 'Lane|lane|Ln|ln|'
    suffix += 'Boulevard|boulevard|Blvd|blvd'
    suffix += 'Highway|highway|Hwy|hwy|'
    suffix += 'Parkway|parkway|Pkwy|pkwy'
    suffix += ')?\.?'

    pattern = '(' + No + CD + street_main + street_minor + suffix + ')'
    
    matches = re.findall(pattern, text)

    if matches:
        return [m[0] for m in matches]
    else:
        return matches

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('not enough parameters')
    else:
        address = parse(sys.argv[1])
        for i in address:
            print(i)
