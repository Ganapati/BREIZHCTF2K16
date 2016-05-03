from bottle import route, run, request, response
from Crypto.Cipher import DES
import base64
import random
import string
import json

class PaddingError(Exception):
    pass

KEY = "!SECRET!"
FLAG = "BZHCTF{ORACLE_PADDING_IS_FUN}"

def cipher(clear, key, IV):
    pad_len = 8 - len(clear) % 8 # length of padding
    padding = chr(pad_len) * pad_len # PKCS5 padding content
    clear += padding
    cipher = DES.new( key, DES.MODE_CBC, IV )
    return base64.urlsafe_b64encode(IV + cipher.encrypt(clear))

def uncipher(cipher, key):
    cipher += '=' * (-len(cipher) % 4)
    b64_decoded = base64.urlsafe_b64decode(cipher)
    uncipher = DES.new( key, DES.MODE_CBC, b64_decoded[:8] )
    clear = uncipher.decrypt(b64_decoded)
    padding = clear[-1]
    # Check padding
    if not all(c in padding for c in clear[-ord(padding):]):
        raise PaddingError()
    return clear[8:-ord(padding)]

@route('/')
def page(data=None):
    IV = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    json_data = json.dumps({'username': 'Guest', 'flag': FLAG})
    data = cipher(json_data, KEY, IV)
    if request.get_cookie("secret_data"):
        secret_data = request.get_cookie("secret_data")
        try:
            try:
                if "libwww-perl" in request.headers.get('User-Agent'): # Anti Padbuster simple
                    response.set_header('Set-Cookie', 'secret_data=%s' % data)
                    return "Attack detected."
                plain = uncipher(secret_data, KEY)
                data = json.loads(plain)
                print data
                return "Hello %s." % data['username']
            except PaddingError:
                response.set_header('Set-Cookie', 'secret_data=%s' % data)
                return "Padding error."
        except:
            response.set_header('Set-Cookie', 'secret_data=%s' % data)
            return "Secret value error."
    else:
        response.set_header('Set-Cookie', 'secret_data=%s' % data)
        return '<a href="/">Enter website</a>'

if __name__ == "__main__":
    run(host='0.0.0.0', port=8080)
