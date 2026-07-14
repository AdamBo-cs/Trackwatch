import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.signal import butter, filtfilt
import os

# Configuration des dossiers
DOSSIER_ENTREE = 'donnees_brutes'
DOSSIER_SORTIE = 'donnees_traitees'

# Création du dossier de sortie s'il n'existe pas
os.makedirs(DOSSIER_SORTIE, exist_ok=True)

NOM_FICHIER = 'Curlbiceps_20260714_132222.csv'
CHEMIN_ENTREE = os.path.join(DOSSIER_ENTREE, NOM_FICHIER)

FREQUENCE_CIBLE = 50.0 
FREQUENCE_COUPURE_FILTRE = 10.0 

if not os.path.exists(CHEMIN_ENTREE):
    print(f" Fichier {CHEMIN_ENTREE} introuvable.")
    exit()

print(f" Lecture des données depuis {CHEMIN_ENTREE}...")
df = pd.read_csv(CHEMIN_ENTREE)

# Séparation des capteurs et conversion du temps pour commencer à 0 (en secondes)
t0 = df['Timestamp'].min()
df_acc = df[df['SensorType'] == 1].copy()
df_gyro = df[df['SensorType'] == 4].copy()

df_acc['Time_s'] = (df_acc['Timestamp'] - t0) / 1000.0
df_gyro['Time_s'] = (df_gyro['Timestamp'] - t0) / 1000.0

print(f" Interpolation à {FREQUENCE_CIBLE} Hz...")
t_max = min(df_acc['Time_s'].max(), df_gyro['Time_s'].max())

temps_parfait = np.arange(0, t_max, 1.0 / FREQUENCE_CIBLE)

def interpoler_capteur(df_capteur, temps_cible):
    """Prend des données irrégulières et les aligne sur la grille de temps parfaite"""
    # interp1d crée une fonction mathématique à partir de nos points réels
    f_x = interp1d(df_capteur['Time_s'], df_capteur['X'], kind='linear', fill_value="extrapolate")
    f_y = interp1d(df_capteur['Time_s'], df_capteur['Y'], kind='linear', fill_value="extrapolate")
    f_z = interp1d(df_capteur['Time_s'], df_capteur['Z'], kind='linear', fill_value="extrapolate")
    
    # On demande à la fonction de deviner les valeurs sur notre temps parfait
    return f_x(temps_cible), f_y(temps_cible), f_z(temps_cible)

acc_x, acc_y, acc_z = interpoler_capteur(df_acc, temps_parfait)
gyr_x, gyr_y, gyr_z = interpoler_capteur(df_gyro, temps_parfait)

print(f" Filtrage passe-bas à {FREQUENCE_COUPURE_FILTRE} Hz...")

def filtrer_signal(donnees, freq_coupure, freq_echantillonnage):
    """Lisse la courbe en supprimant le bruit haute fréquence"""
    nyquist = 0.5 * freq_echantillonnage
    normal_cutoff = freq_coupure / nyquist
    # Création du filtre d'ordre 4
    b, a = butter(4, normal_cutoff, btype='low', analog=False)
    # filtfilt applique le filtre dans un sens, puis dans l'autre (pour éviter de décaler le temps)
    return filtfilt(b, a, donnees)

acc_x_filtre = filtrer_signal(acc_x, FREQUENCE_COUPURE_FILTRE, FREQUENCE_CIBLE)
acc_y_filtre = filtrer_signal(acc_y, FREQUENCE_COUPURE_FILTRE, FREQUENCE_CIBLE)
acc_z_filtre = filtrer_signal(acc_z, FREQUENCE_COUPURE_FILTRE, FREQUENCE_CIBLE)

# Récupérer le nom sans le .csv (ex: "A_1")
nom_sans_extension = os.path.splitext(NOM_FICHIER)[0]
nom_fichier_sortie = f"{nom_sans_extension}_train.csv"
CHEMIN_SORTIE = os.path.join(DOSSIER_SORTIE, nom_fichier_sortie)

# 1. On crée le fichier pour l'entrainement
df_propre = pd.DataFrame({
    'Temps_s': temps_parfait,
    'Acc_X': acc_x_filtre, 'Acc_Y': acc_y_filtre, 'Acc_Z': acc_z_filtre,
    'Gyr_X': gyr_x, 'Gyr_Y': gyr_y, 'Gyr_Z': gyr_z # Souvent, on filtre moins le gyro car il a moins de bruit mécanique
})

df_propre.to_csv(CHEMIN_SORTIE, index=False)
print(f" Fichier '{CHEMIN_SORTIE}' généré avec succès !")

# 2. Affichage visuel pour comparer l'Avant / Après
plt.figure(figsize=(12, 6))
plt.title("L'Axe Z de l'Accéléromètre : Avant vs Après Filtrage")

# La courbe brute (irrégulière et bruitée)
plt.plot(df_acc['Time_s'], df_acc['Z'], label='Données Brutes (Bruitées)', color='#bdc3c7', alpha=0.8, linewidth=1)

# La courbe traitée (alignée et lissée)
plt.plot(temps_parfait, acc_z_filtre, label=f'Données Lissées (Filtre {FREQUENCE_COUPURE_FILTRE}Hz)', color='#e74c3c', linewidth=2.5)

plt.xlabel('Temps (s)')
plt.ylabel('Accélération (m/s²)')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()