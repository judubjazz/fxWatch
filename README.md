# CONFIGURATIONS GÉNÉRALES
* on prend en consideration que python3 et pip sont déjà installés

##Dépandences
* Un fichier requierements.txt est disponible dans le répertoire [~/project_root/requierements.txt](requirements.txt)
* Sans environnement virtuel, l'instalation se fera au niveau root de python
* Pour isoler l'instalation des dépandences, il est possible de créer un environnement virtuel:
```bash
$ pip install virtualenvwrapper
...
$ export WORKON_HOME=~/Envs
$ mkdir -p $WORKON_HOME
$ source /usr/local/bin/virtualenvwrapper.sh
$ mkvirtualenv --python=`which python3` tp2
```
* Si nécessaire, instaler les dépandences en entrant dans le terminal:
```bash
$ workon tp2
(tp2)$ pip install --upgrade -r requirements.txt
```


##Base de données
* Doit être une base de données sqlite3 
* Doit être nommée db.db
* Doit être située dans le répertoire  [~/project_root/db](db) 
* Créer la base de données en entrant dans le terminal:
```bash
~/project_root/db $ sqlite3 db.db
```


##Configuration du email
* Doit être une adresse Gmail 
* Le mot de passe et le username doivent être configurés.
* Le mot de passe et le username sont configurés dans le fichier conf.txt situé dans le répertoire [~/project_root/conf.txt](conf.txt) .
* flask_mail doit être instalé.
* Pour instaler flask_mail, entrer dans le terminal:
```bash
$ pip install flask_mail
```

### RUN APP
* Pour exécuter l'application à partir du terminal flask_script doit être installer.
* Pour instaler flask_script, entrer dans le terminal:
```bash
$ pip install flask_script
```

* Pour exécuter l'application, entrer dans le terminal:
```bash
~/project_root $ python3 manage.py runserver
```

