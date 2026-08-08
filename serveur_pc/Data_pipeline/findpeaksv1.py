import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# ==========================================
# ⚙️ 1. CONFIGURATION DU TEST
# ==========================================
DOSSIER_SCRIPT = os.path.dirname(os.path.abspath(__file__))
# Assure-toi de pointer vers le bon dossier (ex: donnees_trimmed ou donnees_traitees)
DOSSIER = '03_donnees_trimmed' 
FICHIER = 'Barbellrow_20260718_151903_trimmed.csv' # Remplace par ton fichier test

CHEMIN_COMPLET = os.path.join(DOSSIER_SCRIPT, DOSSIER, FICHIER)
FREQUENCE = 50.0

# Choix de la courbe à analyser ('Acc_X', 'Acc_Y', 'Acc_Z', 'Gyr_X', 'Magnitude_Acc', etc.)
COLONNE_CIBLE = 'Acc_X' 

# --- LES 3 PARAMÈTRES MAGIQUES (À ajuster selon l'exercice) ---
SEUIL_HAUTEUR = 3  # Le pic doit dépasser cette valeur absolue
DISTANCE_SEC = 1    # Temps minimum entre deux répétitions
CHUTE_MIN = 8        # De combien la courbe doit redescendre pour valider le pic (L'équivalent de la Proéminence)


# ==========================================
# 🧠 2. L'ALGORITHME CUSTOM (À traduire en Kotlin plus tard)
# ==========================================
def detecteur_pics_embarque(signal, seuil_hauteur, distance_pts, chute_min):
    """
    Algorithme O(N) ultra-léger pour microcontrôleur/montre.
    Parcourt le tableau une seule fois avec une machine à états.
    """
    pics = []
    max_val = -float('inf')
    max_pos = -1
    en_montee = True
    
    # On initialise loin dans le passé pour autoriser un pic dès le début
    dernier_pic_pos = -distance_pts 

    for i in range(1, len(signal)):
        val = signal[i]

        if en_montee:
            # On traque le sommet
            if val > max_val:
                max_val = val
                max_pos = i
            
            # Si le signal chute suffisamment par rapport au sommet trouvé
            elif val <= max_val - chute_min:
                en_montee = False # On arrête de chercher le sommet, on descend
                
                # Vérification des conditions pour valider le pic
                if max_val >= seuil_hauteur and (max_pos - dernier_pic_pos) >= distance_pts:
                    pics.append(max_pos)
                    dernier_pic_pos = max_pos
        else:
            # Si on est en train de descendre, on attend que le signal remonte 
            # pour se remettre en mode "recherche de sommet"
            if val > signal[i-1]: 
                en_montee = True
                max_val = val
                max_pos = i

    return pics


# ==========================================
# 📊 3. EXÉCUTION ET AFFICHAGE VISUEL
# ==========================================
if __name__ == "__main__":
    if not os.path.exists(CHEMIN_COMPLET):
        print(f"❌ Erreur : Fichier introuvable -> {CHEMIN_COMPLET}")
    else:
        df = pd.read_csv(CHEMIN_COMPLET)
        
        # Calcul des magnitudes au cas où on voudrait les utiliser
        if 'Magnitude_Acc' not in df.columns:
            df['Magnitude_Acc'] = np.sqrt(df['Acc_X']**2 + df['Acc_Y']**2 + df['Acc_Z']**2)
        if 'Magnitude_Gyr' not in df.columns:
            df['Magnitude_Gyr'] = np.sqrt(df['Gyr_X']**2 + df['Gyr_Y']**2 + df['Gyr_Z']**2)

        signal = df[COLONNE_CIBLE].values
        temps = df['Temps_s'].values
        
        # Conversion du paramètre temps en nombre de points
        distance_pts = int(DISTANCE_SEC * FREQUENCE)

        # Lancement de l'algorithme "Maison"
        index_pics = detecteur_pics_embarque(signal, SEUIL_HAUTEUR, distance_pts, CHUTE_MIN)
        nombre_reps = len(index_pics)

        # Résultat Console
        print("\n" + "="*40)
        print(f"Fichier analysé : {FICHIER}")
        print(f"Canal utilisé   : {COLONNE_CIBLE}")
        print(f"Répétitions     : {nombre_reps}")
        print("="*40 + "\n")

        # Affichage Matplotlib
        plt.figure(figsize=(12, 5))
        plt.title(f"Mise au point de l'algorithme - {COLONNE_CIBLE} ({nombre_reps} répétitions)")
        
        # La courbe
        plt.plot(temps, signal, label=f"Signal {COLONNE_CIBLE}", color="#3498db")
        
        # Les points trouvés (Croix rouges)
        temps_pics = temps[index_pics]
        valeurs_pics = signal[index_pics]
        plt.plot(temps_pics, valeurs_pics, "x", color="#e74c3c", markersize=12, markeredgewidth=3, label="Pics validés")
        
        # Les lignes d'aide (Seuil de hauteur)
        plt.axhline(y=SEUIL_HAUTEUR, color="green", linestyle="--", alpha=0.5, label=f"Seuil hauteur ({SEUIL_HAUTEUR})")

        plt.xlabel("Temps (s)")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.show()