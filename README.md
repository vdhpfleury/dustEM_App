## Regarder le **tuto video** pour l'utilisation de cette interface.

### Interface utilisateur pour dustEM : Tutorial CYPRESS
Cette interface permet de faire le tuto **dustEM** via une interface utilisateur sans avoir à jongler entre les fichiers.

L'installation de **dustEM** est possible directement via l'application.

Si vous avez deja installer **dustEM**, il vous suffit de rentré le repertoire dans le champs associé.

#### 1/ RDV sur github : 
- Télécharger l'archive du repos.
- Extraire les élements de l'archive
- Aller dans le dossier de l'archive

#### 2/ Changer les droits pour permettre l'execution des fichiers .sh : 
- chmod +x *.sh

#### 3/ Executer le fichier : dustEM_App.sh
- ./dustEM_App.sh
Le programme va crée un environnement virtuel de travail python dans lequel toutes les dependances seront installés

#### 4/ L'application s'est ouverte dans votre navigateur préféré
	- Elle a besoin du code dustEM et propose de le télécharger directement depuis la fênetre utilisateur en cliquant sur le bouton **download dustEM**
    - Télecharge dustEM, 
    - Execute le makefile 
    - Modifie le fichier DM_contants.f90
  - si l'execution c'est bien passé, le status change dans l'application 

#### 5/ Mon premier model d'émission
##### A/ Définir un nom au model que l'on veut faire
##### B/ Définir les paramètres du test puis sauvegarder le test
- Valeur du champ $G_0$
- Nombre de populaiton de poussière
  - Type
  - Taille
  - etc...
- Sauvegarder le modèle en appuyant sur le bouton correspondant 

##### 6/ Lancer la simulation avec le bouton 
- La sortie console est affiché directement dans l'application

#### 7/ Visualisation dynamique des résultats pour le modèle définit
- 2 modes de visualiations
  -  1 modele
  -  plusieur modèle

#### 8/ Possibilité de telecharger les données
- graphe
- .csv
