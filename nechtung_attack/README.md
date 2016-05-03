# Description

TODO

# Solution

Une petite recherche sur google sur "nechtung" retourne "oracle de nechtung". On est donc probablement sur une padding oracle attack (surtout dans la catégorie crypto...)
En se promenant sur le (mini) site, on remarque un cookie nommé secret_data contenant une chaine base64.
L'idée est alors de s'attaquer à cette chaine via une padding oracle afin de la déchiffrer.

les premiers tests avec Padbuster ne sont pas concluants :

```
/tmp/padbuster.pl http://localhost:8080/ "Sko0Tlc2RlTzxjFbx1QFR3TE9TmDyMcEBLVpMWu6tKzVF_CgoT4gcMY060rikuBlbNcA0xwIHklOykJ3RHZoOZeYwiHFS2Ya" -cookies "secret_data=Sko0Tlc2RlTzxjFbx1QFR3TE9TmDyMcEBLVpMWu6tKzVF_CgoT4gcMY060rikuBlbNcA0xwIHklOykJ3RHZoOZeYwiHFS2Ya" 8 -encoding 4

INFO: The original request returned the following
[+] Status: 200
[+] Location: N/A
[+] Content Length: 16

INFO: Starting PadBuster Decrypt Mode
*** Starting Block 1 of 8 ***

INFO: No error string was provided...starting response analysis
```

En mode -veryverbose, padbuster affiche l'erreur en question :
```
+-------------------------------------------+
| PadBuster - v0.3.3                        |
| Brian Holyfield - Gotham Digital Science  |
| labs@gdssecurity.com                      |
+-------------------------------------------+
Request:
GET
http://localhost:8080/

secret_data=Sko0Tlc2RlTzxjFbx1QFR3TE9TmDyMcEBLVpMWu6tKzVF_CgoT4gcMY060rikuBlbNcA0xwIHklOykJ3RHZoOZeYwiHFS2Ya
Response Content:
Attack detected.

INFO: The original request returned the following
[+] Status: 200
[+] Location: N/A
[+] Content Length: 16

[+] Response: Attack detected.

INFO: Starting PadBuster Decrypt Mode
*** Starting Block 1 of 8 ***

Request:
GET
http://localhost:8080/

secret_data=AAAAAAAAAP_zxjFbx1QFRw
Response Content:
Attack detected.
INFO: No error string was provided...starting response analysis
```

L'outil est détecté ("Attack detected."). Il faut donc soit le modifier pour le rendre plus discret, soit changer de méthode.
Ce qui pousse a utiliser la (formidable) librairie python-paddingoracle : https://mwielgoszewski.github.io/python-paddingoracle/.

La seconde solution est d'essayer de patcher Padbuster en changeant le user agent à la ligne 641 :
```
$lwp = LWP::UserAgent->new(env_proxy => 1,
                           agent => "FOOBAR",
                           keep_alive => 1,
                           timeout => 30,
			    		   requests_redirectable => [],
                          );
```

On relance l'outil :

```
+-------------------------------------------+
| PadBuster - v0.3.3                        |
| Brian Holyfield - Gotham Digital Science  |
| labs@gdssecurity.com                      |
+-------------------------------------------+

INFO: The original request returned the following
[+] Status: 200
[+] Location: N/A
[+] Content Length: 12

[BLABLABLA]

-------------------------------------------------------
** Finished ***

[+] Decrypted value (ASCII): {"username": "Guest", "flag": "BZHCTF{ORACLE_PADDING_IS_FUN}"}

[+] Decrypted value (HEX): 7B22757365726E616D65223A20224775657374222C2022666C6167223A2022425A484354467B4F5241434C455F50414444494E475F49535F46554E7D227D0202

[+] Decrypted value (Base64): eyJ1c2VybmFtZSI6ICJHdWVzdCIsICJmbGFnIjogIkJaSENURntPUkFDTEVfUEFERElOR19JU19GVU59In0CAg==

-------------------------------------------------------
```

FLAG : BZHCTF{ORACLE_PADDING_IS_FUN}