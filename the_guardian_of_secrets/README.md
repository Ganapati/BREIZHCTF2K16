# Description

TODO

# Solution

L'épreuve demande une chaine en entrée, dans le cas d'une chaine vide, elle retourne :

```
You found my secret lair, but you'll never find my key.
My crypto is so strong, i'll give you the cipher : lRekwWbrLTwwbEGeKYEeZKMRXkVd8YdTqkrELxjVswRnp/UX
```

La chaine "lRekwWbrLTwwbEGeKYEeZKMRXkVd8YdTqkrELxjVswRnp/UX" doit contenir le flag.
Un base64 -d de cette chaine ne renvoi rien d'exploitable (My crypto is so strong, i'll give you the cipher), il faut donc trouver un moyen de la déchiffrer

Dans le cas de l'envoi d'une chaine non-base64, le seveur répond 
```
Can't you read a fracking input format ???
```

Ce qui nous donne le format d'entrée attendu.

Dans le cas où on envoi une chaine valide, le serveur renvoi une chaine en base64 et illisible une fois décodée.

En variant la longueur du message d'entrée, on remarque que la sortie à toujours la même taille que l'entrée, ce qui exclu le chiffrement par blocs.

De plus, pour une même chaine en entrée, la réponse est toujours la même, ce qui implique un chiffrement avec une clef fixe.

Une clef fixe et un chiffrement par flux fait penser à du RC4.
L'attaque classique sur ce type d'algo est la récupération de keystream (surtout avec une entrée contrôlable et une sortie récupérable)

![RC4](https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Wep-crypt-alt.svg/305px-Wep-crypt-alt.svg.png)
 
```
CIPHER = PLAINTEXT xor KEYSTREAM
```

Avec KEYSTREAM généré a partir de la clef et l'IV.

On contrôle PLAINTEXT, CIPHER et on a un message SECRET a déchiffrer. L'algo devient alors :
```
FLAG = CIPHER xor PLAINTEXT xor SECRET
```

Avec xortool :
```
~/s/B/t/chall ❯❯❯ xortool-xor -f /tmp/01 -f /tmp/02 -f /tmp/03
BZHCTF{KEYSTREAM_IS_EASIER_THAN_KEY}s�O�I-
```

FLAG : BZHCTF{KEYSTREAM_IS_EASIER_THAN_KEY}