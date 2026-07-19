import pandas as pd
import numpy as np
import os

DOSSIER_SCRIPT = os.path.dirname(os.path.abspath(__file__))
DOSSIER_TRAITE = '03_donnees_trimmed'
DOSSIER_SORTIE='04_donnees_tensor'
NOM_FICHIER = 'Curlbiceps_20260714_132222_train_trimmed.csv'

FICHIER_ENTREE = os.path.join(DOSSIER_TRAITE, NOM_FICHIER)

nom_sans_extension = os.path.splitext(NOM_FICHIER)[0]
nom_fichier_sortieX = f"{nom_sans_extension}_tensorX.npy"
FICHIER_SORTIE_X = os.path.join(DOSSIER_SCRIPT, DOSSIER_SORTIE, nom_fichier_sortieX)

nom_fichier_sortieY = f"{nom_sans_extension}_tensorY.npy"
FICHIER_SORTIE_Y = os.path.join(DOSSIER_SCRIPT, DOSSIER_SORTIE, nom_fichier_sortieY)


FREQUENCE = 50.0  
TAILLE_FENETRE_SEC = 4.0      # W_L = 2 secondes
CHEVAUCHEMENT_POURCENT = 0.8  # 80% overlap
ETIQUETTE_EXERCICE = 1        # Classe cible

if not os.path.exists(FICHIER_ENTREE):
    print(f"Fichier {FICHIER_ENTREE} introuvable.")
    exit()

df = pd.read_csv(FICHIER_ENTREE)
colonnes_capteurs = ['Acc_X', 'Acc_Y', 'Acc_Z', 'Gyr_X', 'Gyr_Y', 'Gyr_Z']
donnees_brutes = df[colonnes_capteurs].values 

taille_fenetre_pts = int(TAILLE_FENETRE_SEC * FREQUENCE) # 100 points
pas_avancement_pts = int(taille_fenetre_pts * (1.0 - CHEVAUCHEMENT_POURCENT)) # 20 points

print(f"Dimensions d'une fenêtre : {taille_fenetre_pts} points ({TAILLE_FENETRE_SEC}s)")
print(f"Avancement (Shift step)  : {pas_avancement_pts} points ({pas_avancement_pts/FREQUENCE}s)")

X = [] 
Y = [] 

for debut in range(0, len(donnees_brutes) - taille_fenetre_pts + 1, pas_avancement_pts):
    fin = debut + taille_fenetre_pts
    fenetre = donnees_brutes[debut:fin, :]
    X.append(fenetre)
    Y.append(ETIQUETTE_EXERCICE) 

X_tensor = np.array(X)
Y_tensor = np.array(Y)

print(" Restructuration terminée !")
print(f" Forme du Tenseur 3D (X) : {X_tensor.shape}")
print(f"Forme du Vecteur Labels (Y) : {Y_tensor.shape}")

np.save(FICHIER_SORTIE_X, X_tensor)
np.save(FICHIER_SORTIE_Y, Y_tensor)
print(f"Données prêtes pour l'entraînement !")