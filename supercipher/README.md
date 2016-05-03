# Description

TODO

# Solution

En jouant un peu avec l'épreuve, on se rend compte que c'est un service de chiffrement :
On envoit un fichier et en retour on obtient un ZIP contenant le cipher et la clef.

Le fichier flag.zip ne contient evidemment pas la clef et il faut la récupérer pour retrouver le plain du cipher donné.

En utilisant l'appli, on se rend compte d'un /home.py dans l'url. un accès à home.pyc permet de récupérer le python précompilé qu'il suffit de passer dans uncompyle2 pour avoir une source exploitable.

la partie cipher est la suivante :
```
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
```

Avec SECRET = "FOOBARBAZG" (en début de fichier).
Malheureusement, le fichier key étant vide, la variable SECRET ne sert ici à rien et ne permet pas de retrouver la clef de chiffrement.

Par contre, en analysant la source, on se rend compte que le masque (qui est xor avec le plain) est généré avec random.randint(1,255).
Pour retrouver le mask (et récupérer le plain), il faut donc être en capacité de récupérer le seed utilisé, puis générer assez de randint(1,255).

le seed est initialisé à la ligne :
```
seed = int(time.time()) # Secure seed
```

Le timestamp de création du fichier permettant de savoir "a peu près" quand le script l'a généré permet de retrouver le seed utilisé.

On se retrouve a faire une boucle de bruteforce (attention, l'heure du serveur est un peu différente +/- 2h).
```
import base64
import random

cipher = base64.b64decode("o32ah1OGBeng8GgLBTD8ikGTcis=")
for key in range(1452168000, 1452186000):
    try:
        random.seed(key)
        content_size = len(cipher)
        mask = ''.join([chr(random.randint(1,255)) for _ in xrange(content_size)])
        plain = ''.join(chr(ord(a)^ord(b)) for a,b in zip(mask, cipher))
        print repr(plain)
    except:
        pass
```

FLAG = FLAG{EASYCRYPTOPWN}