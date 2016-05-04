# Description

TODO

# Solution

Pour cette épreuve, chaque équipe a en sa possession une carte NFC (Mifare classic 1k).
Une borne avec un lecteur est à disposition, avec sur l'écran :
```
Welcome To Super Secure Wireless Zone
Waiting for card...
```

Une première lecture (avec un téléphone ou un des lecteurs a disposition) renvoi la chaine suivante :

```
guest:guest
```

En tentant de badger sur la borne a disposition pour résoudre le chall, l'écran indique :
```
Guest can't read flag
```

Il va donc falloir exploiter l'application sur la borne afin de trouver comment passer le mécanisme d'authentification.

Le premier test est donc d'essayer d'écrire :
```
admin:admin
```

Avec cette chaine, la borne renvoi :
```
Verification Failed
Token : '!#/)zW\\xa5\\xa7C\\x89J\\x0eJ\\x80\\x1f\\xc3'
```

Un token est généré avec les infos de la carte. Reste à comprendre comment...
Après quelques tests, on se rend compte que seule la partie apres le ":" est utilisée pour générer le token en question. On est face a une classique login:password.

Après une série de tests et en notant les chaines en entrée ainsi que les tokens correspondants, on peut déduire que le token en question est un hash md5 du mot de passe.
Autre détail qui a son importance, le md5 est présenté en RAW (et non pas hex).

Authentification et raw md5 font donc penser à la technique d'injection (une recherche google permet de trouver des articles ou posts sur ce sujet (https://news.ycombinator.com/item?id=1948308)).

le but est donc maintenant de réussir a générer un hash contenant une injection.
Soit on lance une boucle jusqu'à tomber sur un hash contenant 'or' (par exemple), soit on utilise la payload utilisée pour un précédent ctf (http://cvk.posthaven.com/sql-injection-with-raw-md5-hashes):

md5('129581926211651571912466741651878684928') == ?T0D??o#??'or'8.N=?

La dernière étape consiste à écrire dans la carte la chaine suivante :
```
admin:129581926211651571912466741651878684928
```

Lors du passage sur badge, la borne répond :
```
Welcome Admin !
Congratz !
```

Le dump du badge révèle alors que le flag a été écris sur la carte lors de la validation.

FLAG : BZHCTF{NEW_TECH_SAME_VULNZ}