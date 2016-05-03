#!/usr/bin/env python
 
import socket
import base64


TCP_IP = '0.0.0.0'
TCP_PORT = 1337
BUFFER_SIZE = 1024
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


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))

b64_flag = base64.b64encode(rc4crypt(FLAG))

while 1:
  s.listen(1)
  conn, addr = s.accept()
  data = conn.recv(BUFFER_SIZE)
  if not data or data == "\n" or data == "\r\n":
    conn.send("You found my secret lair, but you'll never find my key.\n My crypto is so strong, i'll give you the cipher : %s" % b64_flag) 
    conn.close()
  try:
    conn.send("Your secret is safe with me : %s" % base64.b64encode(rc4crypt(base64.b64decode(data))))
  except TypeError:
    conn.send("Can't you read a fracking input format ???")
    conn.close()
  except:
    conn.send("Mess with the best, die like the rest.")
    conn.close()