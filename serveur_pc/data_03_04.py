import pandas as pd
import numpy as np
import os
import json

# --- CONFIGURATION DES DOSSIERS ---
DOSSIER_SCRIPT = os.path.dirname(os.path.abspath(__file__))
DOSSIER_ENTREE = os.path.join(DOSSIER_SCRIPT, '03_donnees_trimmed')
DOSSIER_SORTIE = os.path.join(DOSSIER_SCRIPT, '04_donnees_tensor')

# Création du dossier de sortie s'il n'existe pas
os.makedirs(DOSSIER_SORTIE, exist_ok=True)

# --- PARAMÈTRES DU FENÊTRAGE ---
FREQUENCE = 50.0  
TAILLE_FENETRE_SEC = 4.0      # W_L = 4 secondes
CHEVAUCHEMENT_POURCENT = 0.8  # 80% overlap

taille_fenetre_pts = int(TAILLE_FENETRE_SEC * FREQUENCE) # 200 points
pas_avancement_pts = int(taille_fenetre_pts * (1.0 - CHEVAUCHEMENT_POURCENT)) # 40 points

print(f" Dimensions d'une fenêtre : {taille_fenetre_pts} points ({TAILLE_FENETRE_SEC}s)")
print(f" Avancement (Shift step)  : {pas_avancement_pts} points ({pas_avancement_pts/FREQUENCE}s)\n")


X_global = [] 
Y_global = [] 

# Dictionnaire pour mémoriser quelle étiquette correspond à quel numéro

dictionnaire_classes = {}
id_classe_actuelle = 0

# lecture des fichiers
if not os.path.exists(DOSSIER_ENTREE):
    print(f" Erreur : Le dossier {DOSSIER_ENTREE} n'existe pas.")
    exit()

fichiers_csv = [f for f in os.listdir(DOSSIER_ENTREE) if f.endswith('.csv')]

if not fichiers_csv:
    print(f" Aucun fichier CSV trouvé dans {DOSSIER_ENTREE}.")
    exit()

print(f" Construction du Dataset à partir de {len(fichiers_csv)} fichiers...\n")

for fichier in fichiers_csv:
    # 1. Extraction de l'étiquette
    label_texte = fichier.split('_')[0]
    
    if label_texte not in dictionnaire_classes:
        dictionnaire_classes[label_texte] = id_classe_actuelle
        id_classe_actuelle += 1
        
    numero_classe = dictionnaire_classes[label_texte]
    
    # 2. Chargement des données
    chemin_entree = os.path.join(DOSSIER_ENTREE, fichier)
    df = pd.read_csv(chemin_entree)
    
    colonnes_capteurs = ['Acc_X', 'Acc_Y', 'Acc_Z', 'Gyr_X', 'Gyr_Y', 'Gyr_Z']
    donnees_brutes = df[colonnes_capteurs].values 
    
    # 3. Découpage en fenêtres glissantes
    compteur_fenetres = 0
    for debut in range(0, len(donnees_brutes) - taille_fenetre_pts + 1, pas_avancement_pts):
        fin = debut + taille_fenetre_pts
        fenetre = donnees_brutes[debut:fin, :]
        
        X_global.append(fenetre)
        Y_global.append(numero_classe)
        compteur_fenetres += 1
        
    print(f" {fichier} -> Classe '{label_texte}' (ID: {numero_classe}) -> {compteur_fenetres} fenêtres extraites.")

# --- CONVERSION ET SAUVEGARDE ---
# On transforme nos listes Python en Tenseurs mathématiques ultra-rapides
X_tensor = np.array(X_global)
Y_tensor = np.array(Y_global)

print(" Restructuration du Dataset terminée !")
print(f" Forme du Tenseur 3D (X) : {X_tensor.shape}")
print(f" Forme du Vecteur Labels (Y) : {Y_tensor.shape}")

# Sauvegarde des données
np.save(os.path.join(DOSSIER_SORTIE, 'X_dataset.npy'), X_tensor)
np.save(os.path.join(DOSSIER_SORTIE, 'Y_dataset.npy'), Y_tensor)

# Sauvegarde du dictionnaire 
chemin_dictionnaire = os.path.join(DOSSIER_SORTIE, 'classes_map.json')
with open(chemin_dictionnaire, 'w', encoding='utf-8') as f:
    json.dump(dictionnaire_classes, f, indent=4)

print(f" Fichiers X_dataset.npy, Y_dataset.npy et classes_map.json sauvegardés dans '{DOSSIER_SORTIE}' !")