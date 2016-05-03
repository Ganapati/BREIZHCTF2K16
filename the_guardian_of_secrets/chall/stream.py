#!/usr/bin/env python
 
import socket
import base64
import sys


SECRET_KEY = "!SECRET!!SECRET!"
FLAG = "BZHCTF{KEYSTREAM_IS_EASIER_THAN_KEY}"

def rc4crypt(data, key=None):
    if key is None:
      key = SECRET_KEY
    x = 0
    box = range(256)
    for i in range(256):
        x = (x + box[i] + ord(key[i % len(key)])) % 256
        box[i], box[x] = box[x], box[i]
    x = 0
    y = 0
    out = []
    for char in data:
        x = (x + 1) % 256
        y = (y + box[x]) % 256
        box[x], box[y] = box[y], box[x]
        out.append(chr(ord(char) ^ box[(box[x] + box[y]) % 256]))
    
    return ''.join(out)


b64_flag = base64.b64encode(rc4crypt(FLAG))

data = raw_input()
if not data or data == "\n" or data == "\r\n":
  print("You found my secret lair, but you'll never find my key.\n My crypto is so strong, i'll give you the cipher : %s" % b64_flag) 
  sys.exit(0)
try:
  print("Your secret is safe with me : %s" % base64.b64encode(rc4crypt(base64.b64decode(data))))
except TypeError:
  print("Can't you read a fracking input format ???")
except:
  print("Mess with the best, die like the rest.")