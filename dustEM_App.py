import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import os
import subprocess
import pandas as pd
from pathlib import Path
import io
# Configuration de la page
st.set_page_config(
    page_title="DustEM Interface",
    page_icon="🌌",
    layout="wide"
)
# Fonctions utilitaires
def test(file, grain_dict):
    """Mise à jour du fichier GRAIN.DAT avec les paramètres du dictionnaire"""
    nouvelles_lignes = []
    
    with open(file, "r") as f:
        lignes = f.readlines()
    
    for ligne in lignes:
        if ligne[0] == "#":
            nouvelles_lignes.append(ligne)
        elif ligne[0] == "s":
            nouvelles_lignes.append(ligne)
    
    for i in grain_dict:
        if i == "G0":
            nouvelles_lignes.append(grain_dict["G0"])
        else:
            nouvelles_lignes.append(grain_dict[i])
    
    with open(file, "w") as f:
        f.writelines(nouvelles_lignes)


def save_data_test(data, name_set, global_test):
    """Sauvegarde des données SED dans un dictionnaire"""
    data_out = {}
    
    data_out["wl"] = data[:, 0]
    
    for i in range(0, np.shape(data)[-1]):
        if i == np.shape(data)[-1] - 1:
            data_out["sed_tot"] = data[:, i]
        else:
            pop = "pop" + str(i)
            data_out[pop] = data[:, i]
    
    global_test[name_set] = data_out
    
    return global_test


def plot_result(data_dict, scalex="log", scaley="log", xlim=[0.1, 1000], ylim=[1e-22, 1e-18], title="SED Result"):
    """Génération du graphique SED"""
    wl = data_dict["wl"]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for i in data_dict:
        if i == "wl":
            continue
        elif i == "sed_tot":
            ax.plot(wl, data_dict[i], label=i, linewidth=2)
        else:
            ax.plot(wl, data_dict[i], alpha=0.6)
    
    ax.set_yscale(scaley)
    ax.set_xscale(scalex)
    ax.set_title(title)
    ax.set_xlabel("Wavelength (µm)")
    ax.set_ylabel("Intensity")
    
    ax.set_ylim(ylim)
    ax.set_xlim(xlim)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    return fig

def get_path(file):
    home = Path.home()
    matches = list(home.rglob(file))

    if not matches:
        raise FileNotFoundError(f"{file} non trouvé")

    # Prendre le premier trouvé
    find_dustem = matches[0]

    # Récupérer le dossier contenant dustem
    repos = find_dustem.parent

    # Aller dans le parent de dustem_repos
    parent_dir = repos.parent

    #print("dustem trouvé dans :", dustem_repos)
    #print("Parent :", parent_dir)
    return repos, parent_dir
    


# Titre de l'application
st.title("DustEM - Interface")
st.markdown("---")
st.markdown("""#### Prérequis : 
- Pour pouvoir utiliser cette application vous devez avoir la denrière version stable de **dustEM**. 
""")
# Input pour le repository
if 'repos' not in st.session_state:
    st.session_state.repos = {}
    repos_app, parent_repos_app = get_path("dustEM_App.py")
    st.session_state.repos["repos_app"] = repos_app
    st.session_state.repos["parent_repos_app"] = parent_repos_app
    st.session_state.repos["State"] = False


try : 
    dustem_path, parent_dustem_path = get_path("dustem")
    st.success(f"dustem a été localisé : {dustem_path}")

    st.session_state.repos["dustem_path"] = dustem_path
    st.session_state.repos["parent_dustem_path"] = parent_dustem_path
    st.link_button("user guide", url="https://www.ias.u-psud.fr/DUSTEM/dustem_doc.pdf" )
    st.session_state.repos["State"] = True


except : 
    st.warning("Le code dustEM n'est pas présent dans votre PC veulliez le télécharger avant de continuer")

    st.text_input("Repertorie dans lequel telecharger DustEM :", value=st.session_state.repos["repos_app"])

    with st.spinner("On recupère le code dustEM sur internet...", show_time=True):
        if st.button("download dustEM", type="primary"):
            os.chdir(st.session_state.repos["repos_app"] )
            subprocess.run(["./dowload_dustem.sh"])
        
            dustem_path, parent_dustem_path = get_path("dustem")
            st.session_state.repos["dustem_path"] = dustem_path
            st.session_state.repos["parent_dustem_path"] = parent_dustem_path
            st.success("Download complet")

            st.rerun()







st.markdown("---")


# Interface Streamlit
# ==================

# Sidebar pour la configuration globale
if st.session_state.repos["State"] : 
    st.header("Configuration")


    repository = st.text_input(
        "Chemin du repository DustEM",
        value=st.session_state.repos["parent_dustem_path"],
        help="Chemin complet vers le dossier DustEM",
        placeholder="/home/vfleury/Bureau/CYPRESS/DustEM/dustem4.3_web/"
    )

# Initialisation des chemins
if st.session_state.repos["State"] : 
    if repository:
        src = os.path.join(repository, "src")
        output = os.path.join(repository, "out")
        data = os.path.join(repository, "data")
        sed = os.path.join(output, "SED.RES")
        grain_file = os.path.join(data, "GRAIN.DAT")
        
        # Vérification des chemins
        paths_valid = all([
            os.path.exists(repository),
            os.path.exists(src),
            os.path.exists(data)
        ])
        
        if paths_valid:
            st.success("✅ Repository valide")
        else:
            st.error("❌ Repository invalide")
            st.error("Le chemin du repository n'est pas valide. Vérifiez les dossiers src/ et data/")
            st.stop()
else : 
    st.error("Veuillez d'abord télécharger le code dustEM")
st.markdown("---")

# Session state pour stocker les tests
if 'dict_ligne' not in st.session_state:
    st.session_state.dict_ligne = {}

if 'results' not in st.session_state:
    st.session_state.results = {}

# Section principale : Configuration des tests
st.header("Configuration des tests")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Nouveau test")
    test_name = st.text_input(
        "Nom du test",
        value="",
        placeholder="Ex: test_1",
        help="Donnez un nom unique à votre test"
    )

with col2:
    st.subheader("Tests existants")
    if st.session_state.dict_ligne:
        st.write(f"**{len(st.session_state.dict_ligne)} test(s) configuré(s):**")
        for name in st.session_state.dict_ligne.keys():
            st.write(f"- {name}")
    else:
        st.info("Aucun test configuré")

st.markdown("---")

# Formulaire de configuration des paramètres
if test_name:
    st.subheader(f"Paramètres pour: **{test_name}**")
    
    # Paramètre G0
    st.markdown("### Paramètre G0")
    G0_input = st.text_input(
        "Valeur G0",
        value="1e5",
        help="Intensité du champ de radiation (en unités Habing)"
    )
    
    st.markdown("---")
    
    # Section populations
    st.markdown("### Populations de grains")
    
    # Nombre de populations
    n_pops = st.number_input(
        "Nombre de populations",
        min_value=1,
        max_value=5,
        value=2,
        help="Nombre de populations de grains différentes"
    )
    
    populations = {}
    
    for pop_idx in range(1, n_pops + 1):
        with st.expander(f"Population {pop_idx}", expanded=(pop_idx == 1)):
            st.markdown(f"#### Population {pop_idx}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                grain_type = st.text_input(
                    "Grain type",
                    value="CM20",
                    key=f"grain_type_{pop_idx}_{test_name}",
                    help="Type de grain (ex: CM20, aSil, PAH)"
                )
                
                nsize = st.number_input(
                    "nsize",
                    value=25,
                    min_value=1,
                    key=f"nsize_{pop_idx}_{test_name}",
                    help="Nombre de tailles de grains"
                )
                
                type_keyword = st.selectbox(
                    "Type keywords",
                    options=["plaw-chrg-ed", "logn","logn-chrq", "plaw-ed", "plaw-chrg"],
                    key=f"type_keyword_{pop_idx}_{test_name}",
                    help="Type de distribution de taille"
                )
            
            with col2:
                mdust_mh = st.text_input(
                    "Mdust/MH",
                    value="0.170E-02" if pop_idx == 1 else "0.630E-03",
                    key=f"mdust_{pop_idx}_{test_name}",
                    help="Rapport de masse poussière/hydrogène"
                )
                
                rho = st.text_input(
                    "rho (g/cm³)",
                    value="1.600E+00" if pop_idx == 1 else "1.570E+00",
                    key=f"rho_{pop_idx}_{test_name}",
                    help="Densité des grains"
                )
                
                amin = st.text_input(
                    "amin (cm)",
                    value="0.400E-07" if pop_idx == 1 else "0.500E-07",
                    key=f"amin_{pop_idx}_{test_name}",
                    help="Taille minimale des grains"
                )
            
            with col3:
                amax = st.text_input(
                    "amax (cm)",
                    value="4900.00E-07",
                    key=f"amax_{pop_idx}_{test_name}",
                    help="Taille maximale des grains"
                )
                
                alpha_a0 = st.text_input(
                    "alpha/a0",
                    value="-5.00E-00" if pop_idx == 1 else "7.00E-07",
                    key=f"alpha_{pop_idx}_{test_name}",
                    help="Pente de la distribution en loi de puissance ou a0 pour lognormale"
                )
            
            # Paramètres supplémentaires selon le type
            if "ed" in type_keyword or "chrg" in type_keyword:
                st.markdown("**Paramètres ED/CHRG**")
                col4, col5, col6 = st.columns(3)
                
                with col4:
                    at = st.text_input(
                        "at",
                        value="10.00E-07",
                        key=f"at_{pop_idx}_{test_name}",
                        help="Taille de transition"
                    )
                
                with col5:
                    ac = st.text_input(
                        "ac",
                        value="50.0E-07",
                        key=f"ac_{pop_idx}_{test_name}",
                        help="Taille caractéristique"
                    )
                
                with col6:
                    gamma = st.text_input(
                        "gamma",
                        value="1.00E+0",
                        key=f"gamma_{pop_idx}_{test_name}",
                        help="Paramètre gamma"
                    )
                
                # Construction de la ligne pour cette population
                if "ed" in type_keyword:
                    pop_line = f"{grain_type}\t{nsize}\t{type_keyword}\t{mdust_mh}\t{rho}\t{amin}\t{amax}\t{alpha_a0}\t{at}\t{ac}\t{gamma}"
                else:
                    pop_line = f"{grain_type}\t{nsize}\t{type_keyword}\t{mdust_mh}\t{rho}\t{amin}\t{amax}\t{alpha_a0}"
            else:
                # Pour logn ou plaw simple
                pop_line = f"{grain_type}\t{nsize}\t{type_keyword}\t{mdust_mh}\t{rho}\t{amin}\t{amax}\t{alpha_a0}\t1.00E+00"
            
            populations[f"pop{pop_idx}"] = pop_line + "\n"
    
    
    # Boutons d'action
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("💾 Sauvegarder test", type="primary", use_container_width=True):
            # Créer le dictionnaire pour ce test
            test_config = {
                "G0": G0_input + "\n"
            }
            test_config.update(populations)
            
            st.session_state.dict_ligne[test_name] = test_config
            st.success(f"✅ Test '{test_name}' sauvegardé!")
            st.rerun()
    
    with col2:
        if test_name in st.session_state.dict_ligne:
            if st.button("🗑️ Supprimer", use_container_width=True):
                del st.session_state.dict_ligne[test_name]
                if test_name in st.session_state.results:
                    del st.session_state.results[test_name]
                st.success(f"Test '{test_name}' supprimé")
                st.rerun()

# Section d'exécution
st.markdown("---")
st.header("Exécution des simulations")

if st.session_state.dict_ligne:
    test_to_run = st.selectbox(
        "Sélectionner un test à exécuter",
        options=list(st.session_state.dict_ligne.keys())
    )
    
    if st.button("Lancer la simulation", type="primary", use_container_width=False):
        with st.spinner(f"Exécution de {test_to_run}..."):
            try:
                # Mise à jour du fichier GRAIN.DAT
                test(grain_file, st.session_state.dict_ligne[test_to_run])
                
                # Exécution de DustEM
                os.chdir(src)
                result = subprocess.run(['./dustem'], capture_output=True, text=True)
                
                st.code(result.stdout, language="text")
                
                if result.returncode == 0:
                    # Lecture des résultats
                    data = np.loadtxt(sed, skiprows=9)
                    st.session_state.results = save_data_test(
                        data=data,
                        name_set=test_to_run,
                        global_test=st.session_state.results
                    )
                    st.success("✅ Simulation terminée avec succès!")
                else:
                    st.error(f"❌ Erreur lors de l'exécution: {result.stderr}")
                    
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")

# Section de visualisation
st.markdown("---")
st.header("Visualisation des résultats")

if st.session_state.results:
    # Mode de visualisation
    viz_mode = st.radio(
        "Mode de visualisation",
        options=["Simulation unique", "Comparaison multiple"],
        horizontal=True,
        help="Choisissez d'afficher une seule simulation ou de comparer plusieurs"
    )
    
    st.markdown("---")
    
    if viz_mode == "Simulation unique":
        # ========== MODE SIMULATION UNIQUE ==========
        result_to_plot = st.selectbox(
            "Sélectionner un résultat à visualiser",
            options=list(st.session_state.results.keys())
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            scale_x = st.selectbox("Échelle X", options=["log", "linear"], index=0)
            xlim_min = st.number_input("X min", value=0.1)
            xlim_max = st.number_input("X max", value=1000.0)
        
        with col2:
            scale_y = st.selectbox("Échelle Y", options=["log", "linear"], index=0)
            ylim_min = st.number_input("Y min", value=1e-22, format="%.2e")
            ylim_max = st.number_input("Y max", value=1e-18, format="%.2e")
        with col3 : 
            graphe_title_solo = st.text_input("graphe_title", value="title")
        
        fig = plot_result(
            data_dict=st.session_state.results[result_to_plot],
            scalex=scale_x,
            scaley=scale_y,
            xlim=[xlim_min, xlim_max],
            ylim=[ylim_min, ylim_max],
            title=f"{graphe_title_solo}"
        )
        st.pyplot(fig)
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)  # Revenir au début du buffer

        st.download_button(
            label="💾 Télécharger le graphique PNG",
            data=buf,
            file_name=f"{result_to_plot}_graph.png",
            mime="image/png"
        )

            
        # Option de téléchargement
        st.download_button(
            label="💾 Télécharger les données CSV",
            data=pd.DataFrame(st.session_state.results[result_to_plot]).to_csv(index=False),
            file_name=f"{result_to_plot}_data.csv",
            mime="text/csv"
        )
    
    else:
        # ========== MODE COMPARAISON MULTIPLE ==========
        st.subheader("Sélection des simulations à comparer")
        
        # Sélection multiple des résultats
        results_to_compare = st.multiselect(
            "Choisir les résultats à comparer",
            options=list(st.session_state.results.keys()),
            default=list(st.session_state.results.keys())[:min(3, len(st.session_state.results))],
            help="Sélectionnez 2 ou plusieurs simulations pour les comparer"
        )
        
        if len(results_to_compare) < 2:
            st.warning("Veuillez sélectionner au moins 2 simulations pour la comparaison")
        else:
            st.info(f"{len(results_to_compare)} simulation(s) sélectionnée(s): {', '.join(results_to_compare)}")
            
            # Options de visualisation
            st.markdown("**Échelles et limites**")

            col1, col2, col3 = st.columns(3)

            with col1:
                scale_x = st.selectbox("Échelle X", options=["log", "linear"], index=0, key="compare_scale_x")
                xlim_min = st.number_input("X min", value=0.1, key="compare_xlim_min")
                xlim_max = st.number_input("X max", value=1000.0, key="compare_xlim_max")
            
            with col2:
                scale_y = st.selectbox("Échelle Y", options=["log", "linear"], index=0, key="compare_scale_y")
                ylim_min = st.number_input("Y min", value=1e-22, format="%.2e", key="compare_ylim_min")
                ylim_max = st.number_input("Y max", value=1e-18, format="%.2e", key="compare_ylim_max")
            
            with col3:
                st.markdown("**Options d'affichage**")
                graph_title = st.text_input("titre du graphe", value="", placeholder="Graph title")
                show_populations = st.checkbox(
                    "Afficher les populations", 
                    value=False, 
                    help="Afficher les contributions de chaque population en pointillés"
                )
                #show_legend = st.checkbox("Afficher la légende", value=True)
                show_grid = st.checkbox("Grille", value=True)
            
            #if st.button("📊 Comparer les simulations", type="primary"):
            # Création du graphique de comparaison
            fig, ax = plt.subplots(figsize=(14, 8))
                
            # Palette de couleurs distinctes
            colors = plt.cm.tab10(np.linspace(0, 1, len(results_to_compare)))
                
            # Tracer chaque simulation
            for idx, result_name in enumerate(results_to_compare):
                data_dict = st.session_state.results[result_name]
                wl = data_dict["wl"]
                color = colors[idx]
                    
                # Tracer le SED total avec une ligne épaisse
                ax.plot(
                    wl, 
                    data_dict["sed_tot"], 
                    label=f"{result_name}",
                    linewidth=2.5,
                    color=color,
                    zorder=10
                )
                    
                # Tracer les populations si demandé
                if show_populations:
                    for key in data_dict:
                        if key.startswith("pop"):
                            ax.plot(
                                wl,
                                data_dict[key],
                                linestyle='--',
                                alpha=0.4,
                                color=color,
                                linewidth=1.2,
                                zorder=5
                            )
                
            # Configuration des axes
            ax.set_yscale(scale_y)
            ax.set_xscale(scale_x)
            ax.set_title(
                f"{graph_title}", 
                fontsize=16, 
                fontweight='bold',
                pad=20
            )
            ax.set_xlabel("Longueur d'onde (µm)", fontsize=13, fontweight='bold')
            ax.set_ylabel("Intensité", fontsize=13, fontweight='bold')
            ax.set_ylim([ylim_min, ylim_max])
            ax.set_xlim([xlim_min, xlim_max])
                
            if show_grid:
                ax.grid(True, alpha=0.5, linestyle='-', linewidth=0.8)
                
            if True: #show_legend:
                ax.legend(
                    loc='best', 
                    fontsize=10,
                    framealpha=0.9,
                    shadow=True,
                    borderpad=1
                )
                
            plt.tight_layout()
            st.pyplot(fig)
            
            buf2 = io.BytesIO()
            fig.savefig(buf2, format="png")
            buf2.seek(0)  # Revenir au début du buffer

            st.download_button(
                label="💾 Télécharger le graphique PNG",
                data=buf2,
                file_name=f"{graph_title}.png",
                mime="image/png"
            )

                
            # ========== TABLEAU RÉCAPITULATIF ==========
            st.subheader("Résumé des simulations")
                
            summary_data = []
            for result_name in results_to_compare:
                config = st.session_state.dict_ligne.get(result_name, {})
                G0 = config.get("G0", "N/A").strip()
                n_pops = len([k for k in config.keys() if k.startswith("pop")])
                    
                summary_data.append({
                    "Simulation": result_name,
                    "G0": G0,
                    "Nb populations": n_pops,
                    "Max SED": f"{np.max(st.session_state.results[result_name]['sed_tot']):.2e}"
                })
                
            df_summary = pd.DataFrame(summary_data)
            st.dataframe(df_summary, use_container_width=True)
                
            # ========== TÉLÉCHARGEMENT DES DONNÉES ==========
            st.markdown("---")
                
            # Créer un DataFrame combiné pour toutes les simulations
            combined_data = {"wavelength_um": st.session_state.results[results_to_compare[0]]["wl"]}
                
            for result_name in results_to_compare:
                # Ajouter le SED total
                combined_data[f"{result_name}_SED_total"] = st.session_state.results[result_name]["sed_tot"]
                    
                # Ajouter les populations si demandé
                if show_populations:
                    for key in st.session_state.results[result_name]:
                        if key.startswith("pop"):
                            combined_data[f"{result_name}_{key}"] = st.session_state.results[result_name][key]
                
            csv_data = pd.DataFrame(combined_data).to_csv(index=False)
                
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Téléchargement des données")

                
            with col2:
                st.download_button(
                    label="Télécharger données comparées (CSV)",
                    data=csv_data,
                    file_name=f"dustem_comparison_{len(results_to_compare)}_sims.csv",
                    mime="text/csv",
                    use_container_width=True,
                    type="primary"
                )
                
else:
    st.info("Aucun résultat disponible. Lancez d'abord une simulation.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    --- DustEM Interface ---
    </div>
    """,
    unsafe_allow_html=True
)