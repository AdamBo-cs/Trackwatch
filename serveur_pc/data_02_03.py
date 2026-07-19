import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# --- CONFIGURATION ---
DOSSIER_SCRIPT = os.path.dirname(os.path.abspath(__file__))
NOM_FICHIER = 'Pecfly_20260717_110002_train.csv'

# On colle le nom du dossier et du fichier à ce chemin absolu
FICHIER_ENTREE = os.path.join(DOSSIER_SCRIPT, '02_donnees_traitees', NOM_FICHIER)

FREQUENCE = 50.0  # 50 Hz

# Renommage automatique : remplace l'extension ou ajoute _trimmed
nom_sans_extension = os.path.splitext(NOM_FICHIER)[0]
nom_fichier_sortie = f"{nom_sans_extension}_trimmed.csv"
FICHIER_SORTIE = os.path.join(DOSSIER_SCRIPT, '03_donnees_trimmed', nom_fichier_sortie)

# Paramètres de l'Algorithme (Template Matching)
TAILLE_FENETRE_SEC = 3.0  
PAS_GLISSEMENT_SEC = 0.1  
SEUIL_PERIODICITE = 0.85
SEUIL_ENERGIE_MIN = 0.5 # Pour éviter l'amplification du bruit au repos

# --- 1. CHARGEMENT ET PRÉPARATION ---
if not os.path.exists(FICHIER_ENTREE):
    print(f"Fichier {FICHIER_ENTREE} introuvable.")
    print("Vérifiez le nom ou l'emplacement du fichier.")
    exit()

df = pd.read_csv(FICHIER_ENTREE)

# Calcul de la Norme L2 (Magnitude) pour rendre l'analyse invariante à l'orientation
df['Magnitude_Acc'] = np.sqrt(df['Acc_X']**2 + df['Acc_Y']**2 + df['Acc_Z']**2)
df['Magnitude_Gyr'] = np.sqrt(df['Gyr_X']**2 + df['Gyr_Y']**2 + df['Gyr_Z']**2)

# --- 2. L'ALGORITHME DE TEMPLATE MATCHING DISJOINT ---
taille_fenetre_pts = int(TAILLE_FENETRE_SEC * FREQUENCE)
pas_glissement_pts = int(PAS_GLISSEMENT_SEC * FREQUENCE)
total_pts = len(df)

temps_stac = []
scores_stac = []

print(f"Lecture de : {NOM_FICHIER}")
print("Calcul par Template Matching (Fenêtres disjointes) en cours...")

def calculer_score_disjoint(signal, idx_ref):
    """Calcule le score max de Pearson avec toutes les fenêtres disjointes du fichier."""
    # 1. Extraction du tampon (Template)
    W_ref = signal[idx_ref : idx_ref + taille_fenetre_pts]
    
    # NOISE GATE : Si on est au repos (faible énergie), on force à 0
    if np.var(W_ref) < SEUIL_ENERGIE_MIN:
        return 0.0
        
    # Centrage (Soustraction de la moyenne locale mu_ref)
    W_ref_centree = W_ref - np.mean(W_ref)
    energie_ref = np.sum(W_ref_centree**2)
    
    # Évite la division par zéro mathématique
    if energie_ref == 0:
        return 0.0
        
    max_pearson = 0.0
    
    # 2. Scan du reste du fichier (en respectant la règle d'intersection nulle)
    for idx_test in range(0, total_pts - taille_fenetre_pts, pas_glissement_pts):
        
        # RÈGLE D'EXCLUSION : La fenêtre de test ne doit pas toucher le tampon (W_ref) !
        # Elle doit être soit entièrement avant, soit entièrement après.
        if (idx_test + taille_fenetre_pts <= idx_ref) or (idx_test >= idx_ref + taille_fenetre_pts):
            
            W_test = signal[idx_test : idx_test + taille_fenetre_pts]
            
            # Centrage (Soustraction de la moyenne locale mu_test)
            W_test_centree = W_test - np.mean(W_test)
            energie_test = np.sum(W_test_centree**2)
            
            if energie_test == 0:
                continue
            
            # Formule du Score de Pearson (Covariance / Produit des écarts-types)
            covariance = np.sum(W_ref_centree * W_test_centree)
            pearson = covariance / np.sqrt(energie_ref * energie_test)
            
            if pearson > max_pearson:
                max_pearson = pearson
                
    return max_pearson

# On fait glisser le tampon (Template) le long du fichier pour créer notre courbe de rythme
for debut in range(0, total_pts - taille_fenetre_pts, pas_glissement_pts):
    
    score_acc = calculer_score_disjoint(df['Magnitude_Acc'].values, debut)
    score_gyr = calculer_score_disjoint(df['Magnitude_Gyr'].values, debut)
    
    # SENSOR FUSION : On garde le capteur qui trouve le meilleur "jumeau"
    score_final = max(score_acc, score_gyr)
            
    # Le temps représenté est le centre de la fenêtre de 2s
    temps_stac.append(df['Temps_s'].iloc[debut + taille_fenetre_pts//2])
    scores_stac.append(score_final)

# --- 3. DÉTECTION DES POINTS FINAUX (ENDPOINT DETECTION) ---
scores_stac = np.array(scores_stac)
temps_stac = np.array(temps_stac)

# Chercher les moments au-dessus de la ligne verte
zones_actives = np.where(scores_stac > SEUIL_PERIODICITE)[0]

if len(zones_actives) > 0:
    debut_serie_sec = temps_stac[zones_actives[0]]
    fin_serie_sec = temps_stac[zones_actives[-1]]
    
    # Marge de sécurité (Padding) pour ne pas trancher des répétitions
    debut_serie_sec = max(0, debut_serie_sec - 0.5)
    fin_serie_sec = min(df['Temps_s'].max(), fin_serie_sec + 0.5)
    
    print(f"Coupure détectée : de {debut_serie_sec:.1f}s à {fin_serie_sec:.1f}s")
    
    # Création du dossier de sortie s'il n'existe pas
    os.makedirs(os.path.dirname(FICHIER_SORTIE), exist_ok=True)
    
    df_rogne = df[(df['Temps_s'] >= debut_serie_sec) & (df['Temps_s'] <= fin_serie_sec)]
    df_rogne.to_csv(FICHIER_SORTIE, index=False)
    print(f"Fichier sauvegardé : {nom_fichier_sortie}")
else:
    print("Aucune périodicité forte détectée.")
    debut_serie_sec, fin_serie_sec = 0, df['Temps_s'].max()

# --- 4. VISUALISATION ---
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
fig.canvas.manager.set_window_title(f'Template Matching - {nom_sans_extension}')

ax1.plot(df['Temps_s'], df['Magnitude_Acc'], color='#3498db')
ax1.axvline(x=debut_serie_sec, color='red', linestyle='--')
ax1.axvline(x=fin_serie_sec, color='red', linestyle='--')
ax1.set_title("Magnitude Accélération")

ax2.plot(df['Temps_s'], df['Magnitude_Gyr'], color='#2ecc71')
ax2.axvline(x=debut_serie_sec, color='red', linestyle='--')
ax2.axvline(x=fin_serie_sec, color='red', linestyle='--')
ax2.set_title("Magnitude Gyroscope")

ax3.plot(temps_stac, scores_stac, color='#e74c3c', linewidth=2, label="Score Pearson Fusionné")
ax3.axhline(y=SEUIL_PERIODICITE, color='green', linestyle=':', label="Threshold")
ax3.axvline(x=debut_serie_sec, color='red', linestyle='--')
ax3.axvline(x=fin_serie_sec, color='red', linestyle='--')
ax3.set_title("Score Périodicité unifié (Fenêtres disjointes)")
ax3.set_xlabel("Temps (s)")
ax3.legend()

plt.tight_layout()
plt.show()