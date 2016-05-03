from bottle import route, run, template, request, static_file
import time
import random
import base64
import zipfile
from StringIO import StringIO
import os, sys

SECRET = "FOOBARBAZG" # Timestamp length

@route('/')
@route('/home.py')
def hello():
    return '''
<h1>SuperCipher</h1>
<h2>Chiffrer :</h2>
<form action="/home.py/secret.zip" method="post" enctype="multipart/form-data">
  Select a file: <input type="file" name="upload" />
  <input type="submit" value="cipher" />
</form>
<br />
<h2>Dechiffrer</h2>
<form action="/home.py/uncipher" method="post" enctype="multipart/form-data">
  Password: <input type="password" name="key" />
  Select a file: <input type="file" name="upload" />
  <input type="submit" value="uncipher" />
</form>
'''

@route('/home.py/secret.zip', method='POST')
def cipher():
    seed = int(time.time()) # Secure seed
    random.seed(seed)
    upload = request.files.get('upload')
    upload_content = upload.file.read()
    content_size = len(upload_content)
    mask = ''.join([chr(random.randint(1,255)) for _ in xrange(content_size)])
    cipher = ''.join(chr(ord(a)^ord(b)) for a,b in zip(mask, upload_content))
    b64_cipher = base64.b64encode(cipher)
    key = ''.join([chr(ord(a)^ord(b)) for a,b in zip(SECRET, str(seed))])
    b64_key = base64.b64encode(key)

    # Compression
    secret = StringIO()
    zf = zipfile.ZipFile(secret, mode='w')
    zf.writestr('secret', b64_cipher)
    zf.writestr('key', b64_key)
    zf.close()
    secret.seek(0)
    return secret

@route('/home.py/uncipher', method='POST')
def cipher():
    key = request.forms.get('key')
    upload = request.files.get('upload')
    try:
        enc_key = base64.b64decode(key)
        key = int(''.join([chr(ord(a)^ord(b)) for a,b in zip(enc_key, SECRET)]))
        random.seed(int(key))
        upload_content = base64.b64decode(upload.file.read())
        content_size = len(upload_content)
        mask = ''.join([chr(random.randint(1,255)) for _ in xrange(content_size)])
        plain = ''.join(chr(ord(a)^ord(b)) for a,b in zip(mask, upload_content))
        return plain
    except:
        return "Uncipher error."

@route('/<filename:path>')
def download(filename):
    return static_file(filename, 
                       root=os.path.join(os.path.dirname(sys.argv[0])), 
                       download=filename)

run(host='0.0.0.0', port=8080)
