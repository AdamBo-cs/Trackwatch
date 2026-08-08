import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import butter, filtfilt
import os

# Configuration des dossiers (Étape 1 du Pipeline)
DOSSIER_ENTREE = '01_data_brutes'
DOSSIER_SORTIE = '02_data_pretraitees'

# Création des dossiers si nécessaire
os.makedirs(DOSSIER_SORTIE, exist_ok=True)

FREQUENCE_CIBLE = 50.0 
FREQUENCE_COUPURE_FILTRE = 10.0 

def filtrer_signal(donnees, freq_coupure, freq_echantillonnage):
    """Filtre passe-bas pour éliminer le bruit haute fréquence."""
    nyquist = 0.5 * freq_echantillonnage
    normal_cutoff = freq_coupure / nyquist
    b, a = butter(4, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, donnees)

def traiter_fichier(nom_fichier):
    chemin_entree = os.path.join(DOSSIER_ENTREE, nom_fichier)
    nom_sans_extension = os.path.splitext(nom_fichier)[0]
    nom_fichier_sortie = f"{nom_sans_extension}_pretraite.csv"
    chemin_sortie = os.path.join(DOSSIER_SORTIE, nom_fichier_sortie)

    # Vérification : si le fichier existe déjà, on saute
    if os.path.exists(chemin_sortie):
        print(f"⏩ Déjà traité, on saute : {nom_fichier_sortie}")
        return

    print(f"⚙️ Traitement de : {nom_fichier}...")
    df = pd.read_csv(chemin_entree)

    # Séparation, résolution des divisions par zéro (groupby) et temps
    t0 = df['Timestamp'].min()
    df_acc = df[df['SensorType'] == 1].copy()
    df_gyro = df[df['SensorType'] == 4].copy()

    df_acc = df_acc.groupby('Timestamp', as_index=False).mean()
    df_gyro = df_gyro.groupby('Timestamp', as_index=False).mean()

    df_acc['Time_s'] = (df_acc['Timestamp'] - t0) / 1000.0
    df_gyro['Time_s'] = (df_gyro['Timestamp'] - t0) / 1000.0

    t_max = min(df_acc['Time_s'].max(), df_gyro['Time_s'].max())
    temps_parfait = np.arange(0, t_max, 1.0 / FREQUENCE_CIBLE)

    def interpoler_capteur(df_capteur, temps_cible):
        f_x = interp1d(df_capteur['Time_s'], df_capteur['X'], kind='linear', fill_value="extrapolate")
        f_y = interp1d(df_capteur['Time_s'], df_capteur['Y'], kind='linear', fill_value="extrapolate")
        f_z = interp1d(df_capteur['Time_s'], df_capteur['Z'], kind='linear', fill_value="extrapolate")
        return f_x(temps_cible), f_y(temps_cible), f_z(temps_cible)

    acc_x, acc_y, acc_z = interpoler_capteur(df_acc, temps_parfait)
    gyr_x, gyr_y, gyr_z = interpoler_capteur(df_gyro, temps_parfait)

    acc_x_filtre = filtrer_signal(acc_x, FREQUENCE_COUPURE_FILTRE, FREQUENCE_CIBLE)
    acc_y_filtre = filtrer_signal(acc_y, FREQUENCE_COUPURE_FILTRE, FREQUENCE_CIBLE)
    acc_z_filtre = filtrer_signal(acc_z, FREQUENCE_COUPURE_FILTRE, FREQUENCE_CIBLE)

    gyr_x_filtre = filtrer_signal(gyr_x, FREQUENCE_COUPURE_FILTRE, FREQUENCE_CIBLE)
    gyr_y_filtre = filtrer_signal(gyr_y, FREQUENCE_COUPURE_FILTRE, FREQUENCE_CIBLE)
    gyr_z_filtre = filtrer_signal(gyr_z, FREQUENCE_COUPURE_FILTRE, FREQUENCE_CIBLE)

    # Sauvegarde des données purement filtrées
    df_propre = pd.DataFrame({
        'Temps_s': temps_parfait,
        'Acc_X': acc_x_filtre, 'Acc_Y': acc_y_filtre, 'Acc_Z': acc_z_filtre,
        'Gyr_X': gyr_x_filtre, 'Gyr_Y': gyr_y_filtre, 'Gyr_Z': gyr_z_filtre
    })

    df_propre.to_csv(chemin_sortie, index=False)
    print(f"✅ Généré : {nom_fichier_sortie}")

if __name__ == "__main__":
    if not os.path.exists(DOSSIER_ENTREE):
        print(f"Le dossier {DOSSIER_ENTREE} n'existe pas. Créez-le et ajoutez des fichiers bruts.")
    else:
        fichiers_csv = [f for f in os.listdir(DOSSIER_ENTREE) if f.endswith('.csv')]
        if not fichiers_csv:
            print(f"Aucun fichier CSV trouvé dans {DOSSIER_ENTREE}")
        else:
            for fichier in fichiers_csv:
                try:
                    traiter_fichier(fichier)
                except Exception as e:
                    print(f"❌ Erreur sur {fichier} : {e}")
            print("🎉 Tous les fichiers bruts ont été pré-traités !")