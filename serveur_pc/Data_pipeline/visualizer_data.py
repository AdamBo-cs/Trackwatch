import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# --- 1. CONFIGURATION ---
DOSSIER_SCRIPT = os.path.dirname(os.path.abspath(__file__))

# Remplace par le nom exact du dossier où se trouvent tes fichiers
NOM_DOSSIER = '03_donnees_trimmed' 
# Remplace par le nom de ton fichier CSV
NOM_FICHIER = 'Curlbiceps_20260729_132928_trimmed.csv'

CHEMIN_COMPLET = os.path.join(DOSSIER_SCRIPT, NOM_DOSSIER, NOM_FICHIER)

# --- 2. CHARGEMENT DES DONNÉES ---
if not os.path.exists(CHEMIN_COMPLET):
    print(f" Erreur : Le fichier {CHEMIN_COMPLET} n'existe pas.")
    exit()

print(f"Chargement de {NOM_FICHIER}...")
df = pd.read_csv(CHEMIN_COMPLET)

# Calcul de la Magnitude (Norme L2) pour l'accéléromètre et le gyroscope
df['Magnitude_Acc'] = np.sqrt(df['Acc_X']**2 + df['Acc_Y']**2 + df['Acc_Z']**2)
df['Magnitude_Gyr'] = np.sqrt(df['Gyr_X']**2 + df['Gyr_Y']**2 + df['Gyr_Z']**2)

# --- 3. AFFICHAGE (MATPLOTLIB) ---
# On crée une très grande fenêtre avec 8 graphiques
fig, axes = plt.subplots(8, 1, figsize=(14, 16), sharex=True)
fig.canvas.manager.set_window_title(f'Visualisation Complète - {NOM_FICHIER}')

# Liste des données à afficher : (Nom de la colonne, Couleur, Titre)
graphiques = [
    ('Acc_X', '#e74c3c', 'Accélération X'),
    ('Acc_Y', '#2ecc71', 'Accélération Y'),
    ('Acc_Z', '#3498db', 'Accélération Z'),
    ('Gyr_X', '#f39c12', 'Gyroscope X'),
    ('Gyr_Y', '#9b59b6', 'Gyroscope Y'),
    ('Gyr_Z', '#1abc9c', 'Gyroscope Z'),
    ('Magnitude_Acc', '#c0392b', 'Magnitude Accélération (Globale)'),
    ('Magnitude_Gyr', '#8e44ad', 'Magnitude Gyroscope (Globale)')
]

# On parcourt nos 8 axes et nos 8 configurations pour les dessiner automatiquement
for ax, (colonne, couleur, titre) in zip(axes, graphiques):
    ax.plot(df['Temps_s'], df[colonne], color=couleur, linewidth=1.5)
    
    # Petite astuce : on met le titre à l'intérieur du graphique pour gagner de la place
    ax.text(0.01, 0.85, titre, transform=ax.transAxes, fontsize=10, fontweight='bold', 
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=2))
            
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # On cache les labels Y pour ne pas surcharger l'écran, on garde juste les valeurs
    ax.set_ylabel("") 

# On ne met le label "Temps" que sur le tout dernier graphique en bas
axes[-1].set_xlabel("Temps (secondes)", fontsize=12, fontweight='bold')

plt.tight_layout()
print("Affichage des courbes.")
plt.show()