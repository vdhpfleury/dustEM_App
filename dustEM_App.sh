#!/bin/bash

################################################################################
# Script de configuration et lancement de l'environnement dustEM
# Version robuste avec gestion d'erreurs complète
################################################################################

set -o pipefail  # Propage les erreurs dans les pipes

# Couleurs pour les messages
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m' # No Color

# Variables globales
readonly SCRIPT_NAME="$(basename "$0")"
readonly PROJECT_NAME="dustEM"
readonly VENV_NAME="env_dustEM"
readonly PYTHON_MIN_VERSION="3.8"
readonly REQUIREMENTS_FILE="requirements.txt"
readonly APP_FILE="dustEM_App.py"

# Compteur d'erreurs
ERROR_COUNT=0

################################################################################
# Fonctions utilitaires
################################################################################

log_info() {
    echo -e "${GREEN}[INFO]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERREUR]${NC} $*" >&2
    ((ERROR_COUNT++))
}

exit_on_error() {
    local exit_code=$1
    local message=$2
    if [[ $exit_code -ne 0 ]]; then
        log_error "$message (code: $exit_code)"
        exit "$exit_code"
    fi
}

prompt_yes_no() {
    local prompt="$1"
    local response
    while true; do
        read -rp "$prompt [o/N] " response
        case "${response,,}" in
            o|oui|y|yes) return 0 ;;
            n|non|no|"") return 1 ;;
            *) echo "Veuillez répondre par 'o' ou 'n'." ;;
        esac
    done
}

################################################################################
# Vérification et installation de Python
################################################################################

check_python_version() {
    local version=$1
    local major minor
    
    # Extraction de la version majeure et mineure
    if [[ $version =~ Python[[:space:]]([0-9]+)\.([0-9]+) ]]; then
        major="${BASH_REMATCH[1]}"
        minor="${BASH_REMATCH[2]}"
        
        # Comparaison de version
        if [[ $major -eq 3 ]] && [[ $minor -ge 8 ]]; then
            return 0
        fi
    fi
    return 1
}

test_python() {
    log_info "Vérification de Python3..."
    
    if command -v python3 >/dev/null 2>&1; then
        local py_version
        py_version=$(python3 --version 2>&1)
        
        if check_python_version "$py_version"; then
            log_info "Python détecté: $py_version"
            return 0
        else
            log_warn "Version Python inadéquate: $py_version"
            log_warn "Version minimale requise: Python $PYTHON_MIN_VERSION"
        fi
    else
        log_warn "Python3 n'est pas installé"
    fi
    
    # Proposition d'installation
    if prompt_yes_no "Voulez-vous installer/mettre à jour Python3 ?"; then
        install_python
    else
        log_error "Python3 est requis pour continuer"
        exit 1
    fi
}

install_python() {
    log_info "Installation de Python3 et des dépendances..."
    
    # Vérification des privilèges sudo
    if ! sudo -n true 2>/dev/null; then
        log_info "Droits administrateur requis pour l'installation"
    fi
    
    # Mise à jour des dépôts
    sudo apt update || exit_on_error $? "Échec de la mise à jour des dépôts"
    
    # Installation de Python3, venv et pip
    sudo apt install -y python3 python3-venv python3-pip || \
        exit_on_error $? "Échec de l'installation de Python3"
    
    log_info "Python3 installé avec succès"
    
    # Vérification post-installation
    if ! command -v python3 >/dev/null 2>&1; then
        log_error "Python3 n'est toujours pas disponible après installation"
        exit 1
    fi
}

################################################################################
# Création et gestion de l'environnement virtuel
################################################################################

get_desktop_path() {
    local desktop_path
    
    # Tentative avec xdg-user-dir
    if command -v xdg-user-dir >/dev/null 2>&1; then
        desktop_path=$(xdg-user-dir DESKTOP 2>/dev/null)
        if [[ -d "$desktop_path" ]]; then
            echo "$desktop_path"
            return 0
        fi
    fi
    
    # Fallback: chemins courants
    local fallback_paths=(
        "$HOME/Bureau"
        "$HOME/Desktop"
        "$HOME"
    )
    
    for path in "${fallback_paths[@]}"; do
        if [[ -d "$path" ]]; then
            echo "$path"
            return 0
        fi
    done
    
    log_error "Impossible de trouver le répertoire Bureau"
    return 1
}

create_project_structure() {
    log_info "Configuration de l'environnement de projet..."
    
    # Détermination du chemin du Bureau
    local desktop_path
    desktop_path=$(get_desktop_path) || exit 1
    
    log_info "Répertoire cible: $desktop_path"
    
    # Création du répertoire projet
    local project_path="$desktop_path/$PROJECT_NAME"
    mkdir -p "$project_path" || exit_on_error $? "Échec de création du répertoire $project_path"
    
    cd "$project_path" || exit_on_error $? "Impossible d'accéder à $project_path"
    
    log_info "Répertoire de travail: $(pwd)"
    
    # Export du chemin pour les autres fonctions
    export PROJECT_PATH="$project_path"
}

check_existing_venv() {
    if [[ -d "$VENV_NAME" ]]; then
        log_info "Environnement virtuel existant détecté: $VENV_NAME"
        
        # Vérification de la validité de l'environnement
        if [[ -f "$VENV_NAME/bin/activate" ]] && [[ -f "$VENV_NAME/bin/python3" ]]; then
            log_info "L'environnement virtuel semble valide"
            return 0
        else
            log_warn "L'environnement virtuel est corrompu"
            if prompt_yes_no "Voulez-vous le recréer ?"; then
                rm -rf "$VENV_NAME"
                return 1
            else
                exit_on_error 1 "Environnement virtuel invalide"
            fi
        fi
    fi
    return 1
}

create_venv() {
    log_info "Création de l'environnement virtuel: $VENV_NAME"
    
    python3 -m venv "$VENV_NAME" || \
        exit_on_error $? "Échec de création de l'environnement virtuel"
    
    log_info "Environnement virtuel créé avec succès"
}

activate_venv() {
    local activate_script="$VENV_NAME/bin/activate"
    
    if [[ ! -f "$activate_script" ]]; then
        log_error "Script d'activation introuvable: $activate_script"
        exit 1
    fi
    
    # shellcheck disable=SC1090
    source "$activate_script" || \
        exit_on_error $? "Échec de l'activation de l'environnement virtuel"
    
    log_info "Environnement virtuel activé"
    log_info "Python utilisé: $(which python3)"
}

install_requirements() {
    log_info "Installation des dépendances Python..."
    
    # Vérification du fichier requirements.txt
    if [[ ! -f "$REQUIREMENTS_FILE" ]]; then
        log_warn "Fichier $REQUIREMENTS_FILE introuvable dans $(pwd)"
        
        if prompt_yes_no "Voulez-vous créer un fichier requirements.txt de base ?"; then
            create_default_requirements
        else
            log_warn "Installation des dépendances ignorée"
            return 0
        fi
    fi
    
    # Mise à jour de pip
    log_info "Mise à jour de pip..."
    python3 -m pip install --upgrade pip || \
        log_warn "Échec de mise à jour de pip (non critique)"
    
    # Installation des requirements
    log_info "Installation depuis $REQUIREMENTS_FILE..."
    pip install -r "$REQUIREMENTS_FILE" || \
        exit_on_error $? "Échec de l'installation des dépendances"
    
    log_info "Dépendances installées avec succès"
}

create_default_requirements() {
    log_info "Création d'un fichier requirements.txt par défaut..."
    
    cat > "$REQUIREMENTS_FILE" << 'EOF'
# Dépendances pour dustEM
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
EOF
    
    log_info "Fichier $REQUIREMENTS_FILE créé"
}

setup_environment() {
    create_project_structure
    
    if ! check_existing_venv; then
        create_venv
    fi
    
    activate_venv
    install_requirements
}

################################################################################
# Lancement de l'application
################################################################################

check_app_file() {
    cd ~
    repos_app=$(find . -type f -name dustEM_App.py)
    dir_app=$(dirname $repos_app)
    cd $dir_app

    if [ -n $repos_app ]; then
        log_info "Fichier trouvé ici : $dir_app"
    fi

    if [[ ! -f "$APP_FILE" ]]; then
        log_error "Fichier application introuvable: $APP_FILE"
        log_info "Recherche dans le répertoire actuel: $(pwd)"
        log_info "Fichiers présents:"
        ls -la
        
        if prompt_yes_no "Voulez-vous créer un fichier $APP_FILE de démonstration ?"; then
            create_demo_app
        else
            exit 1
        fi
    fi
}

create_demo_app() {
    log_info "Création d'une application Streamlit de démonstration..."
    
    cat > "$APP_FILE" << 'EOF'
import streamlit as st

st.set_page_config(page_title="dustEM", page_icon="🌟")

st.title("🌟 Application dustEM")
st.write("Bienvenue dans l'application dustEM!")

st.info("Ceci est une application de démonstration. Remplacez ce fichier par votre application réelle.")

if st.button("Test"):
    st.success("L'environnement fonctionne correctement!")
    st.balloons()
EOF
    
    log_info "Fichier $APP_FILE créé"
}



run_dustem() {
    log_info "Lancement de l'application dustEM..."
    
    check_app_file
    
    # Vérification que streamlit est installé
    if ! command -v streamlit >/dev/null 2>&1; then
        log_error "Streamlit n'est pas installé"
        if prompt_yes_no "Voulez-vous l'installer maintenant ?"; then
            pip install streamlit || exit_on_error $? "Échec de l'installation de Streamlit"
        else
            exit 1
        fi
    fi
    
    log_info "Démarrage de Streamlit..."
    log_info "Appuyez sur Ctrl+C pour arrêter l'application"
    echo ""
    
    streamlit run "$APP_FILE" || log_error "L'application s'est terminée avec des erreurs"
}

################################################################################
# Fonction principale
################################################################################

show_summary() {
    echo ""
    echo "=========================================="
    echo "  Résumé de la configuration"
    echo "=========================================="
    echo "Projet:              $PROJECT_NAME"
    echo "Répertoire:          $PROJECT_PATH"
    echo "Environnement:       $VENV_NAME"
    echo "Python:              $(python3 --version 2>&1)"
    echo "Application:         $APP_FILE"
    echo "=========================================="
    echo ""
}

cleanup_on_exit() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]] || [[ $ERROR_COUNT -gt 0 ]]; then
        echo ""
        log_error "Le script s'est terminé avec des erreurs (code: $exit_code, erreurs: $ERROR_COUNT)"
    else
        log_info "Script terminé avec succès"
    fi
}

main() {
    trap cleanup_on_exit EXIT
    
    echo "=========================================="
    echo "  Configuration de l'environnement dustEM"
    echo "=========================================="
    echo ""
    
    test_python
    setup_environment
    show_summary
    run_dustem
}

# Point d'entrée
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
