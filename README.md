# SEBANIA


## Fonctionnement

Ce projet fonctionne avec une base de données Postgres pour sauvegarder l'ensemble des données utilisateurs ainsi que les données relatives aux différents médias (films et séries).

## Démarrer le projet en local avec Docker

### Pré-requis

**Docker**

Pour fonctionner, ce projet nécessite l'installation de Docker et Docker Compose. [Documentation](https://docs.docker.com/engine/install/).

**Serveur SMTP : Mailtrap**

Pour fonctionner, l'API utilise un serveur SMTP pour envoyer des emails. Pour les phases de développement et les tests en local, il est recommandé d'utiliser MailTrap.
C'est un outil qui met à disposition un serveur SMTP sans envoyer les emails. Ainsi, on peut vérifier que nos emails seraient bien envoyées et valider leur format sans jamais rien envoyer à personne.

Pour faire fonctionner MailTrap, il suffit de se créer un compte sur leur [site](https://mailtrap.io/). Vous pourrez ensuite récupérer un `username` et un `password` pour vous connecter au serveur SMTP.

**Dropbox**

Pour sauvegarder les vocaux, on utilise un Dropbox. Pour que cela fonctionne avec l'API, il faut configurer des variables d'environnements spécifiques.

**Variables d'environnement**

Pour que l'API puisse fonctionner avec Postgres mais également d'autres services externes, il est important de configurer des variables d'environnement.

Pour ce faire, créer un fichier ``.env`` et copier le contenu suivant dedans :
```dotenv
DJANGO_SECRET_KEY=dev
DATABASE_NAME=sebania
DATABASE_USERNAME=sebania
DATABASE_PASSWORD=sebania
DATABASE_HOST=db
DATABASE_PORT=5432
SMTP_HOST=sandbox.smtp.mailtrap.io
SMTP_USERNAME=<MAIL_TRAP_USERNAME>
SMTP_PASSWORD=<MAIL_TRAP_PASSWORD>
SMTP_PORT=2525
DJANGO_SETTINGS_MODULE=sebania.settings.dev
DROPBOX_REFRESH_TOKEN=XXX
DROPBOX_SECRET=XXX
DROPBOX_KEY=XXX
```

Remplacez les valeurs `<MAIL_TRAP_USERNAME>` et `<MAIL_TRAP_PASSWORD>` par les identifiants récupérés à la section [Mailtrap](#pré-requis)

## Lancement

### Démarrer le projet en local avec Docker

Démarrez l'API avec la base de données PostgreSQL :
```bash
docker compose up api db -d --build
```

Cela peut prendre quelques minutes lors de la première compilation de l'image Docker.

Une fois démarrée, les logs de l'API seront disponibles via la commande :
```bash
docker compose logs api -f
```

Rendez-vous à la section [Authentification & Swagger](#authentification--swagger) pour découvrir les webservices disponibles.

Vous pouvez accès la base de données de l'API en utilisant n'importe quel gestionnaire de base de données (comme DBeaver) en vous connectant à l'url suivante `jdbc:postgresql://localhost:5432/sebania`.
Les identifiants sont ceux spécifiés dans le fichier `.env`.

### Création de la base de données pour le premier lancement

Lors du lancement de l'application pour la première fois, la base de données doit être créée et les données par défaut (cultures, activités, unités, etc.) doivent également être ajoutées à la base.

Lancez les commandes suivantes :
```bash
# création des tables
docker compose run api python manage.py migrate

# insertion des données par défaut
docker compose run api python manage.py loaddata activite_default culture_default type_parcelle unite auth_group methode_agricole
```

## Authentification & Swagger

### Authentification

**Rôles**

Pour le moment, il existe 2 rôles dans l'application: 
- `RESPONSABLE` : rôle de l'utilisateur qui va s'enregister depuis le endpoint dédié en précisant les informations de sa ferme ainsi que celles de ses employés
- `EMPLOYE` : rôle attribué aux utilisateurs créés automatiquement lors de l'inscription d'un responsable.

**Inscription**

Pour vous authentifier sur l'application, il y a 2 options :
- se créer un compte utilisateur comme n'importe quel utilisateur classique de l'application via l'endpoint [register](http://localhost:8000/api/v1/auth/register)
- se créer un compte Django `superuser` via la commande : `python manage.py createsuperuser`. Cette commande doit être executée directement depuis le conteneur de l'application. Attention, elle ne donne pas le rôle `Responsable` et a donc un usage limité.

### Swagger

L'API est désormais disponible via l'[URL](http://localhost:8000).  
Les webservices disponibles sont visibles via le [Swagger](http://localhost:8000/schema/swagger-ui/).  
La section Admin de Django est disponible sur l'url [Admin](http://localhost:8000/admin).  

L'API est protégé par un système de token JWT. Un endpoint ``api/v1/auth/token/access`` permet de récupérer un token JWT à partir du username et mot de passe (en request body) d'un utilisateur enregistré en base.
Ce token permet ensuite d'accéder à l'ensemble des endpoints sécurisés.
