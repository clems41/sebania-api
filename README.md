# SEBANIA


## Fonctionnement

Ce projet fonctionne avec une base de données Postgres pour sauvegarder l'ensemble des données utilisateurs.
Pour fonctionner, il est découpé en plusieurs briques (visibles dans le `docker-compose.yaml`) :
- db : instance PostgreSQL 17 permettant de stocker l'ensemble des données utilisateurs
- api : serveur API permettant de récupérer et de sauvegarder de la donnée de la base de données de manière compréhensible pour le besoin de l'application mobile
- background_tasks : script qui exécute les tâches de fonds de manière asynchrone sans impacter les performances de l'API, comme le traitement des messages vocaux.
- testcases : exécution des tests de l'application pour vérifier la non régression. Utile uniquement pour la CI de ce projet.

## Démarrer le projet

### Pré-requis

**Docker**

Pour fonctionner, ce projet nécessite l'installation de Docker et Docker Compose. [Documentation](https://docs.docker.com/engine/install/).

**Serveur SMTP : Mailtrap**

Pour fonctionner, l'API utilise un serveur SMTP pour envoyer des emails. Pour les phases de développement et les tests en local, il est recommandé d'utiliser MailTrap.
C'est un outil qui met à disposition un serveur SMTP sans envoyer les emails. Ainsi, on peut vérifier que nos emails seraient bien envoyées et valider leur format sans jamais rien envoyer à personne.

Pour faire fonctionner MailTrap, il suffit de se créer un compte sur leur [site](https://mailtrap.io/). Vous pourrez ensuite récupérer un `username` et un `password` pour vous connecter au serveur SMTP.

**Dropbox**

Pour sauvegarder les vocaux, on utilise Dropbox. Pour que cela fonctionne avec l'API, il faut configurer des variables d'environnements spécifiques :
- <DROPBOX_REFRESH_TOKEN> : token pour générer l'`access_token` utile à chaque requête vers Dropbox. Les `access_token` ont des durées de vie limitée, il faut les régénérer régulièrement, c'est pour cela qu'on utilise la mécanique de `refresh_token`.
Suivre ce [tuto](https://django-storages.readthedocs.io/en/latest/backends/dropbox.html#get-authorization-code) pour le récupérer.
Il faut au préalable récupérer un `access_token` depuis son compte Dropbox.
- <DROPBOX_SECRET> : `app_secret` à récupérer depuis son compte Dropbox
- <DROPBOX_KEY> : `app_key` à récupérer depuis son compte Dropbox

**Mistral**

Pour faire fonctionner la brique `background_tasks`, nous avons besoin d'une clé API Mistral (`<MISTRAL_API_KEY>`) pour faire appel à leur LLM, utile à l'analyse des vocaux.

Cette clé peut être obtenue après s'être créé un compte, sur la page [Clés API](https://console.mistral.ai/api-keys).

**Variables d'environnement**

Pour que l'API puisse fonctionner avec Postgres mais également d'autres services externes, il est important de configurer des variables d'environnement.

Pour ce faire, créer un fichier ``.env`` et copier le contenu suivant dedans :
```dotenv
COMPOSE_BAKE=true
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
DROPBOX_REFRESH_TOKEN=<DROPBOX_REFRESH_TOKEN>
DROPBOX_SECRET=<DROPBOX_SECRET>
DROPBOX_KEY=<DROPBOX_KEY>
WHISPER_MODEL=turbo
WHISPER_MODEL_DIRECTORY="/tmp/whisper_models/"
MISTRAL_MODEL="mistral-large-latest"
MISTRAL_API_KEY=<MISTRAL_API_KEY>
MISTRAL_MODEL_TEMPERATURE=0
```

Remplacez les valeurs `<MAIL_TRAP_USERNAME>` et `<MAIL_TRAP_PASSWORD>` par les identifiants récupérés à la section [Mailtrap](#pré-requis).
Remplacez les valeurs `<DROPBOX_REFRESH_TOKEN>`, `<DROPBOX_SECRET>` et `<DROPBOX_KEY>` par les identifiants récupérés à la section [Dropbox](#pré-requis).
Remplacez la valeur `<MISTRAL_API_KEY>` par la clé récupérée à la section [Mistral](#pré-requis).

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

Pour le moment, il existe 2 rôles dans l'application :
- `RESPONSABLE` : rôle de l'utilisateur qui va s'enregister depuis l'endpoint dédié en précisant les informations de sa ferme ainsi que celles de ses employés
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
