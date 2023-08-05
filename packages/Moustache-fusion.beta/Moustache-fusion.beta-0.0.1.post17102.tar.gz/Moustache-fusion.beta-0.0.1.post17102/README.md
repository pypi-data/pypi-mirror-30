# Moustache-fusion (skittlespy)

"Moustache-fusion" (ex- skittlespy) est un module de fusion PDF.

## Installation

### Docker 
TODO

### Ubuntu

Sur une distribution Ubuntu 16.04 LTS, voici la procédure à suivre :

```bash
apt update -y
apt install -y curl pdftk poppler-utils pdfgrep

curl https://bootstrap.pypa.io/get-pip.py | python3

pip3 install moustache-fusion
```

## Utilisation de l'API

### Fichier de configuration JSON

Ce fichier contient la liste des balises à rechercher et les fichiers annexes à insérer.
Un certain nombre d'options sont également disponibles.

annexes : (array) tableau contenant chaque annexe.  
Une annexe est définie par la liste suivante :
+ name : (string) nom du fichier contenant l'annexe
+ pattern : (string) nom de la balise à trouver pour insérer le fichier contenant l'annexe

options : contient la liste des options disponibles. Cette liste est optionnelle.  
+ nopagenumbering : (bool, false par défaut) dévalide la numérotation des pages des annexes
  
exemple de fichier :
```json
{
    "annexes":[
        {
            "name": "annexe1.pdf",
            "pattern": "BALISE1"
        },
        {
            "name": "annexe2.pdf",
            "pattern": "BALISE2"
        }
    ],
    "options":
    {
        "nopagenumbering": false
    }
}

```



