import pandas as pd
import numpy as np
import os
from sklearn.decomposition import PCA 

# Configuration des dossiers (Étape 3 du Pipeline)
# On s'attend à lire les fichiers qui ont été rognés par le STAC (Étape 2)
DOSSIER_ENTREE = '03_data_STAC'
DOSSIER_SORTIE = '04_data_ACP'

# Création des dossiers si nécessaire
os.makedirs(DOSSIER_ENTREE, exist_ok=True)
os.makedirs(DOSSIER_SORTIE, exist_ok=True)

def appliquer_acp(nom_fichier):
    chemin_entree = os.path.join(DOSSIER_ENTREE, nom_fichier)
    nom_sans_extension = os.path.splitext(nom_fichier)[0]
    
    # On modifie le nom pour indiquer que l'ACP a été appliquée
    nom_fichier_sortie = f"{nom_sans_extension}_acp.csv"
    chemin_sortie = os.path.join(DOSSIER_SORTIE, nom_fichier_sortie)

    # Vérification : si le fichier existe déjà, on saute
    if os.path.exists(chemin_sortie):
        print(f"⏩ ACP déjà appliquée, on saute : {nom_fichier_sortie}")
        return

    print(f"📐 Calcul de l'ACP sur : {nom_fichier}...")
    df = pd.read_csv(chemin_entree)

    # 1. Préparation et Centrage de l'Accéléromètre
    acc_data = df[['Acc_X', 'Acc_Y', 'Acc_Z']].values
    acc_centered = acc_data - np.mean(acc_data, axis=0) # Centrage local sur le fichier STAC
    
    # Calcul de l'ACP Accéléromètre
    pca_acc = PCA(n_components=3)
    acc_pca = pca_acc.fit_transform(acc_centered)
    
    # 2. Préparation et Centrage du Gyroscope
    gyr_data = df[['Gyr_X', 'Gyr_Y', 'Gyr_Z']].values
    gyr_centered = gyr_data - np.mean(gyr_data, axis=0) # Centrage local sur le fichier STAC
    
    # Calcul de l'ACP Gyroscope
    pca_gyr = PCA(n_components=3)
    gyr_pca = pca_gyr.fit_transform(gyr_centered)

    # Sauvegarde : On conserve les données de base et on ajoute les axes ACP
    df['Acc_PC1'] = acc_pca[:, 0]
    df['Acc_PC2'] = acc_pca[:, 1]
    df['Acc_PC3'] = acc_pca[:, 2]
    
    df['Gyr_PC1'] = gyr_pca[:, 0]
    df['Gyr_PC2'] = gyr_pca[:, 1]
    df['Gyr_PC3'] = gyr_pca[:, 2]

    df.to_csv(chemin_sortie, index=False)
    print(f"✅ Généré avec succès : {nom_fichier_sortie}")

if __name__ == "__main__":
    fichiers_csv = [f for f in os.listdir(DOSSIER_ENTREE) if f.endswith('.csv')]

    if not fichiers_csv:
        print(f"⚠️ Aucun fichier CSV trouvé dans '{DOSSIER_ENTREE}'.")
        print("Pensez à exécuter votre script STAC d'abord pour remplir ce dossier !")
    else:
        for fichier in fichiers_csv:
            try:
                appliquer_acp(fichier)
            except Exception as e:
                print(f"❌ Erreur sur {fichier} : {e}")
        print("🎉 ACP appliquée sur tous les fichiers avec succès !")