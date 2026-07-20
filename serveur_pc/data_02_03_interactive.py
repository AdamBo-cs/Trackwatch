import pandas as pd
import numpy as np
import pyqtgraph as pg
import os
import sys

DOSSIER_SCRIPT = os.path.dirname(os.path.abspath(__file__))
DOSSIER_ENTREE = os.path.join(DOSSIER_SCRIPT, '02_donnees_traitees')
DOSSIER_SORTIE = os.path.join(DOSSIER_SCRIPT, '03_donnees_trimmed')

os.makedirs(DOSSIER_SORTIE, exist_ok=True)

FREQUENCE = 50.0  
TAILLE_FENETRE_SEC = 4.0  
PAS_GLISSEMENT_SEC = 0.1  
SEUIL_PERIODICITE = 0.8
SEUIL_ENERGIE_MIN = 0.5 

def traiter_fichier_interactif(nom_fichier, app):
    chemin_entree = os.path.join(DOSSIER_ENTREE, nom_fichier)
    nom_sans_extension = os.path.splitext(nom_fichier)[0]
    
    if nom_sans_extension.endswith('_train'):
        nom_base = nom_sans_extension.replace('_train', '')
    else:
        nom_base = nom_sans_extension
        
    nom_fichier_sortie = f"{nom_base}_trimmed.csv"
    chemin_sortie = os.path.join(DOSSIER_SORTIE, nom_fichier_sortie)

    if os.path.exists(chemin_sortie):
        print(f"Déjà rogné, on saute : {nom_fichier_sortie}")
        return

    print(f"Chargement de : {nom_fichier}")
    df = pd.read_csv(chemin_entree)

    df['Magnitude_Acc'] = np.sqrt(df['Acc_X']**2 + df['Acc_Y']**2 + df['Acc_Z']**2)
    df['Magnitude_Gyr'] = np.sqrt(df['Gyr_X']**2 + df['Gyr_Y']**2 + df['Gyr_Z']**2)

    taille_fenetre_pts = int(TAILLE_FENETRE_SEC * FREQUENCE)
    pas_glissement_pts = int(PAS_GLISSEMENT_SEC * FREQUENCE)
    total_pts = len(df)

    temps_stac = []
    scores_stac = []

    print("Calcul de l'algorithme STAC (Veuillez patienter)...")

    def calculer_score_disjoint(signal, idx_ref):
        W_ref = signal[idx_ref : idx_ref + taille_fenetre_pts]
        if np.var(W_ref) < SEUIL_ENERGIE_MIN: return 0.0
            
        W_ref_centree = W_ref - np.mean(W_ref)
        energie_ref = np.sum(W_ref_centree**2)
        if energie_ref == 0: return 0.0
            
        max_pearson = 0.0
        for idx_test in range(0, total_pts - taille_fenetre_pts, pas_glissement_pts):
            if (idx_test + taille_fenetre_pts <= idx_ref) or (idx_test >= idx_ref + taille_fenetre_pts):
                W_test = signal[idx_test : idx_test + taille_fenetre_pts]
                W_test_centree = W_test - np.mean(W_test)
                energie_test = np.sum(W_test_centree**2)
                
                if energie_test == 0: continue
                
                covariance = np.sum(W_ref_centree * W_test_centree)
                pearson = covariance / np.sqrt(energie_ref * energie_test)
                if pearson > max_pearson:
                    max_pearson = pearson
        return max_pearson

    for debut in range(0, total_pts - taille_fenetre_pts, pas_glissement_pts):
        score_acc = calculer_score_disjoint(df['Magnitude_Acc'].values, debut)
        score_gyr = calculer_score_disjoint(df['Magnitude_Gyr'].values, debut)
        score_final = max(score_acc, score_gyr)
                
        temps_stac.append(df['Temps_s'].iloc[debut + taille_fenetre_pts//2])
        scores_stac.append(score_final)

    scores_stac = np.array(scores_stac)
    temps_stac = np.array(temps_stac)

    zones_actives = np.where(scores_stac > SEUIL_PERIODICITE)[0]
    if len(zones_actives) > 0:
        debut_serie_sec = max(0, temps_stac[zones_actives[0]] - 0.5)
        fin_serie_sec = min(df['Temps_s'].max(), temps_stac[zones_actives[-1]] + 0.5)
    else:
        debut_serie_sec, fin_serie_sec = 0.0, df['Temps_s'].max()

    # Lissage des courbes pour un rendu professionnel
    pg.setConfigOptions(antialias=True)
    pg.setConfigOption('background', 'w') # Fond blanc
    pg.setConfigOption('foreground', 'k') # Texte noir

    # Création de la fenêtre (sans l'afficher immédiatement pour éviter un clignotement)
    win = pg.GraphicsLayoutWidget(title=f"Éditeur de Rognage : {nom_fichier}")
    win.showMaximized() # Affichage de la fenêtre en plein écran
    
    label = win.addLabel(
        f"<b>{nom_fichier}</b><br>"
        "<span style='color: #27ae60;'><b>Glissez les bords du bloc vert</b></span> pour ajuster.<br>"
        "<b>ENTRÉE</b>: Sauvegarder | <b>ÉCHAP</b>: Ignorer | <b>Q</b>: Quitter", 
        row=0, col=0, colspan=1
    )
    
    # Création des 5 graphiques empilés
    p1 = win.addPlot(row=1, col=0, title="Accéléromètre 3 axes")
    p2 = win.addPlot(row=2, col=0, title="Gyroscope 3 axes")
    p3 = win.addPlot(row=3, col=0, title="Magnitude Acc")
    p4 = win.addPlot(row=4, col=0, title="Magnitude Gyr")
    p5 = win.addPlot(row=5, col=0, title="Score STAC Fusionné")

    # On lie l'axe X de tous les graphiques pour qu'ils zooment ensemble
    p2.setXLink(p1)
    p3.setXLink(p1)
    p4.setXLink(p1)
    p5.setXLink(p1)

    temps = df['Temps_s'].values
    
    # Couleurs personnalisées
    pen_x = pg.mkPen(color=(231, 76, 60), width=1.5)
    pen_y = pg.mkPen(color=(46, 204, 113), width=1.5)
    pen_z = pg.mkPen(color=(52, 152, 219), width=1.5)
    pen_mag = pg.mkPen(color=(142, 68, 173), width=2)
    pen_score = pg.mkPen(color=(211, 84, 0), width=2)

    p1.plot(temps, df['Acc_X'].values, pen=pen_x, name='X')
    p1.plot(temps, df['Acc_Y'].values, pen=pen_y, name='Y')
    p1.plot(temps, df['Acc_Z'].values, pen=pen_z, name='Z')

    p2.plot(temps, df['Gyr_X'].values, pen=pen_x)
    p2.plot(temps, df['Gyr_Y'].values, pen=pen_y)
    p2.plot(temps, df['Gyr_Z'].values, pen=pen_z)

    p3.plot(temps, df['Magnitude_Acc'].values, pen=pen_mag)
    p4.plot(temps, df['Magnitude_Gyr'].values, pen=pen_mag)

    p5.plot(temps_stac, scores_stac, pen=pen_score)
    ligne_seuil = pg.InfiniteLine(angle=0, movable=False, pos=SEUIL_PERIODICITE, pen=pg.mkPen('g', style=pg.QtCore.Qt.PenStyle.DashLine))
    p5.addItem(ligne_seuil)

    regions = []
    
    # Fonction pour synchroniser le mouvement de la zone verte sur les 5 graphiques
    def update_regions(region_item):
        vmin, vmax = region_item.getRegion()
        for r in regions:
            if r != region_item:
                r.blockSignals(True) # Empêche la boucle infinie de signaux
                r.setRegion([vmin, vmax])
                r.blockSignals(False)

    # On ajoute la zone verte magique sur chaque graphique
    brush_color = pg.mkBrush(46, 204, 113, 50) # Vert semi-transparent
    for p in [p1, p2, p3, p4, p5]:
        # Cet objet natif PyQtGraph gère parfaitement la souris (bords + centre)
        region = pg.LinearRegionItem([debut_serie_sec, fin_serie_sec], brush=brush_color)
        region.setZValue(10)
        p.addItem(region)
        region.sigRegionChanged.connect(lambda r=region: update_regions(r))
        regions.append(region)

    def on_key_press(ev):
        key = ev.key()
        # Code 16777220 et 16777221 = Touche "Entrée" (Numérique et Principale)
        if key in [16777220, 16777221]:
            vmin, vmax = regions[0].getRegion()
            df_rogne = df[(df['Temps_s'] >= vmin) & (df['Temps_s'] <= vmax)]
            df_rogne.to_csv(chemin_sortie, index=False)
            
            # Vérification physique sur le disque pour confirmer la sauvegarde
            if os.path.exists(chemin_sortie):
                print(f"Fichier enregistré avec succès : {nom_fichier_sortie} (de {vmin:.1f}s à {vmax:.1f}s)")
            else:
                print(f"Échec de l'enregistrement pour : {nom_fichier_sortie}")
                
            win.close()
            app.quit() # Libère la boucle pour passer au fichier suivant
            
        # Code 16777216 = Touche "Échap"
        elif key == 16777216:
            print(f"Fichier ignoré.")
            win.close()
            app.quit()
            
        # Code 81 et 113 = Touche "Q" ou "q"
        elif key in [81, 113]:
            print("Arrêt manuel du programme.")
            sys.exit(0)

    # On attache notre écouteur de clavier à la fenêtre
    win.keyPressEvent = on_key_press

    # On lance la fenêtre et on bloque l'exécution jusqu'à ce que l'utilisateur appuie sur Entrée ou Échap
    app.exec()

if __name__ == "__main__":
    if not os.path.exists(DOSSIER_ENTREE):
        print(f"Erreur : Le dossier {DOSSIER_ENTREE} n'existe pas.")
        sys.exit(1)

    tous_fichiers_csv = [f for f in os.listdir(DOSSIER_ENTREE) if f.endswith('.csv')]
    
    # 1. Filtrage intelligent : on ne garde que les fichiers qui n'ont pas encore de version "_trimmed"
    fichiers_a_traiter = []
    for fichier in tous_fichiers_csv:
        nom_sans_ext = os.path.splitext(fichier)[0]
        nom_base = nom_sans_ext.replace('_train', '') if nom_sans_ext.endswith('_train') else nom_sans_ext
        chemin_verif = os.path.join(DOSSIER_SORTIE, f"{nom_base}_trimmed.csv")
        
        if not os.path.exists(chemin_verif):
            fichiers_a_traiter.append(fichier)
        else:
            print(f"{fichier} déjà rogné.")
    
    # 2. Lancement conditionnel
    if not fichiers_a_traiter:
        print(f"Les {len(tous_fichiers_csv)} fichiers ont déjà été traités. Fin du programme.")
    else:
        print(f"Démarrage de l'outil interactif ({len(fichiers_a_traiter)} restants sur {len(tous_fichiers_csv)})...")
        
        # On initialise le moteur graphique 
        app = pg.mkQApp("TrackWatch Éditeur")
        
        for fichier in fichiers_a_traiter:
            traiter_fichier_interactif(fichier, app)
            
        print("Terminé ! Tous les fichiers ont été analysés.")