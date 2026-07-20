import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

# Configuration des dossiers
DOSSIER_ENTREE = 'donnees_brutes'

# Création du dossier de sortie s'il n'existe pas

NOM_FICHIER = 'Pecfly_20260717_110250.csv'
CHEMIN_ENTREE = os.path.join(DOSSIER_ENTREE, NOM_FICHIER)


if not os.path.exists(CHEMIN_ENTREE):
    print(f"Erreur : Fichier {NOM_FICHIER} introuvable")
    sys.exit()

print(f"Analyse du fichier {NOM_FICHIER} en cours...")

# 1. Lecture du fichier CSV grâce à Pandas
# Pandas transforme le fichier texte en un magnifique tableau de données
df = pd.read_csv(CHEMIN_ENTREE)

# 2. Séparation des données
# On crée deux tableaux séparés : un pour l'accéléromètre (Type 1) et un pour le gyro (Type 4)
df_acc = df[df['SensorType'] == 1].copy()
df_gyro = df[df['SensorType'] == 4].copy()

# 3. Conversion du temps
# Au lieu d'avoir un Timestamp de 1691529764453, on soustrait le tout premier Timestamp 
# à toutes les lignes pour que le graphique commence à 0 seconde.
temps_depart = df['Timestamp'].min()
df_acc['Temps_s'] = (df_acc['Timestamp'] - temps_depart) / 1000.0
df_gyro['Temps_s'] = (df_gyro['Timestamp'] - temps_depart) / 1000.0

# 4. Création de la figure 
# subplots(2, 1) : 2 lignes, 1 colonne.
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
fig.canvas.manager.set_window_title(f'TrackWatch - {NOM_FICHIER}')

# Graphique 1 : accéléromètre
ax1.plot(df_acc['Temps_s'], df_acc['X'], label='Axe X (Gauche/Droite)', color='#e74c3c', linewidth=1.5)
ax1.plot(df_acc['Temps_s'], df_acc['Y'], label='Axe Y (Avant/Arrière)', color='#2ecc71', linewidth=1.5)
ax1.plot(df_acc['Temps_s'], df_acc['Z'], label='Axe Z (Haut/Bas)', color='#3498db', linewidth=1.5)

ax1.set_title('Accéléromètre (m/s²)', fontsize=14, fontweight='bold', color='#333333')
ax1.set_ylabel('Accélération', fontsize=12)
ax1.legend(loc='upper right')
ax1.grid(True, linestyle='--', alpha=0.7)
ax1.set_facecolor('#f8f9fa')

# Graphique 2 : gyroscope
ax2.plot(df_gyro['Temps_s'], df_gyro['X'], label='Axe X (Inclinaison vertical)', color='#e74c3c', linewidth=1.5)
ax2.plot(df_gyro['Temps_s'], df_gyro['Y'], label='Axe Y (Roulis)', color='#2ecc71', linewidth=1.5)
ax2.plot(df_gyro['Temps_s'], df_gyro['Z'], label='Axe Z (Rotation horizontale)', color='#3498db', linewidth=1.5)

ax2.set_title('Gyroscope (rad/s)', fontsize=14, fontweight='bold', color='#333333')
ax2.set_xlabel('Temps écoulé (secondes)', fontsize=12)
ax2.set_ylabel('Vitesse de rotation', fontsize=12)
ax2.legend(loc='upper right')
ax2.grid(True, linestyle='--', alpha=0.7)
ax2.set_facecolor('#f8f9fa')

# 5. Ajustement esthétique et affichage
plt.tight_layout() # Empêche les textes de se chevaucher
plt.show() # Ouvre la fenêtre interactive