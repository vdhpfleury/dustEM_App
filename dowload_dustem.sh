#!/bin/bash

# Script d'installation et configuration de DustEM 4.3
# Ce script automatise le téléchargement, la configuration, la compilation et l'exécution de DustEM

set -e  # Arrêter le script en cas d'erreur

echo "=========================================="
echo "Vérificaiton de l'installation de DustEM 4.3"
echo "=========================================="


CURREN_REPOS=$(pwd)

cd ~
find_dustem=$(find . -type f -name "dustem" 2>/dev/null)

if [ -n "$find_dustem" ]; then
    echo "Les fichiers de dustem ont été localisé ici : "
    
    dustem_repos=$(dirname $find_dustem)
    cd "$dustem_repos/.."
    pwd
    echo ""

    echo "Ouverture de l'applicaiton"

    cd "./../.."

    pwd

    cd ~
    find_app=$(find -type f -name "dustEM_App.sh")
    dir_app=$(dirname $find_app)
    cd $dir_app

    ./dustEM_App.sh


else
    echo "Dossier DustEM non trouvé."
    echo ""
    
    cd ~
    find_app=$(find . -type f -name "dustEM_App.sh" 2>/dev/null)

    if [ -z "$find_app" ]; then
        echo "dustEM_App.sh non trouvé !"
        exit 1
    fi

    # Récupérer le dossier contenant le script
    dir_app=$(dirname "$find_app")
    dir_app=$(realpath "$dir_app")   # <-- transforme en chemin absolu

    echo "Répertoire du script : $dir_app"

    # Vérifier qu'il existe
    if [ ! -d "$dir_app" ]; then
        echo "Erreur : $dir_app n'existe pas"
        exit 1
    fi

    # Créer le sous-dossier dustEM_repos (absolu)
    dustem_repos="$dir_app/dustEM_repos"
    mkdir -p "$dustem_repos"

    # Aller dans ce dossier
    cd "$dustem_repos" || { echo "Impossible de cd dans $dustem_repos"; exit 1; }

    user_dir="$dustem_repos"

    echo "Travail dans le dossier : $user_dir"
    ls

    echo "=========================================="
    echo "Téléchargement code dustEM et décompressaion"
    echo "=========================================="

    DOWNLOAD_URL="https://www.ias.u-psud.fr/DUSTEM/dustem4.3_web.tar.gz"
    ARCHIVE_NAME="dustem4.3_web.tar.gz"

    wget $DOWNLOAD_URL
    echo "Décompression de l'archive..."
    tar -xzf "$ARCHIVE_NAME"


    if [ ! -d "oprop" ]; then
        echo "Erreur: Le répertoire dustem4.3web n'a pas été créé après décompression"
        exit 1
    fi

    #Définir le chemin absolu du repository
    DUSTEM_PATH=$user_dir


    echo "Repository DustEM installé dans: $DUSTEM_PATH"



    # Modificaiton du fichier DM_constant.f90
    echo ""
    echo "[2/4] Configuration du fichier DM_constant.f90..."

    CONSTANT_FILE="$DUSTEM_PATH/src/DM_constants.f90"

    if [ ! -f "$CONSTANT_FILE" ]; then
        echo "Erreur: Le fichier $CONSTANT_FILE n'existe pas"
        exit 1
    fi

    # Créer une sauvegarde du fichier original
    cp "$CONSTANT_FILE" "${CONSTANT_FILE}.backup"

    # Modifier la ligne 76 (variable path)
    sed -i "76s|.*|  CHARACTER (len=100)        :: data_path='$DUSTEM_PATH/'|" "$CONSTANT_FILE"

    # Modifier également la ligne 81 pour pointer vers le repository dustem4.3
    sed -i "81s|.*|  CHARACTER(len=100)         :: dir_PDR ='$DUSTEM_PATH/'|" "$CONSTANT_FILE"

    linge_76=$(sed -n '76p' $CONSTANT_FILE)
    ligne_81=$(sed -n '81p' $CONSTANT_FILE)
    echo "Fichier DM_constant.f90 modifié avec succès"
    echo "  - Ligne 76 (path): $ligne_76/"
    echo "  - Ligne 81 (dir_PDR): $ligne_81/"

    echo ""
    echo "[4/4] Vérification de l'installation"
    echo ""

    cd "$DUSTEM_PATH/src"

    repo=$(pwd)

    echo "repos actuel : $repo"

    make

    ls -l dustem

    chmod +x dustem

    ./dustem

    echo ""
    echo "L'installation s'est faite avec succès !"
    echo ""

fi