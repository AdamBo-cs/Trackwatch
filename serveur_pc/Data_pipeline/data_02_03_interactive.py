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
PAS_GLISSEMENT_SEC = 0.1  
HORIZON_RECHERCHE_SEC = 10.0 

PARAMETRES_ROGNAGE = {
    "Squat": {"capteur": "Acc","fenetre": 2, "seuil_stac": 0.92, "seuil_energie": 2},
    "Curlbiceps": {"capteur": "Gyr","fenetre": 2.0, "seuil_stac": 0.87, "seuil_energie": 0.2},
    "Benchpress": {"capteur": "Acc","fenetre": 2.0, "seuil_stac": 0.8, "seuil_energie": 0.3},
    "Lateralraise": {"capteur": "Gyr","fenetre": 2.0, "seuil_stac": 0.8, "seuil_energie": 0.3},
    "Latpulldown": {"capteur": "Acc","fenetre": 3.0, "seuil_stac": 0.65, "seuil_energie": 0.3},
    "Onearmdumbellrow": {"capteur": "Acc","fenetre": 2.0, "seuil_stac": 0.85, "seuil_energie": 0.3},
    "Overheadtricepsextension": {"capteur": "Gyr","fenetre": 2.0, "seuil_stac": 0.7, "seuil_energie": 0.2},
    "Pecfly": {"capteur": "Gyr","fenetre": 3, "seuil_stac": 0.8, "seuil_energie": 0.3},
    "RDL": {"capteur": "Acc","fenetre": 3.0, "seuil_stac": 0.8, "seuil_energie": 0.3},
    "Reardelt": {"capteur": "Gyr ","fenetre": 3.0, "seuil_stac": 0.7, "seuil_energie": 0.15},
    "Underhandtricepsextension": {"capteur": "Gyr","fenetre": 3.0, "seuil_stac": 0.7, "seuil_energie": 0.5},
    "Barbellrow": {"capteur": "Acc","fenetre": 3.0, "seuil_stac": 0.9, "seuil_energie": 1},
    "Inclinedbenchpress": {"capteur": "Acc","fenetre": 2.0, "seuil_stac": 0.85, "seuil_energie": 0.3},
    "Militarypress": {"capteur": "Acc","fenetre": 2.0, "seuil_stac": 0.8, "seuil_energie": 0.3},
    "Defaut": {"capteur": "Acc","fenetre": 2.0, "seuil_stac": 0.3, "seuil_energie": 0.5}
}

def traiter_fichier_interactif(nom_fichier, app):
    chemin_entree = os.path.join(DOSSIER_ENTREE, nom_fichier)
    nom_sans_extension = os.path.splitext(nom_fichier)[0]
    
    # 1. Nom de l'exercice central (_trimmed)
    nom_base = nom_sans_extension.replace('_train', '')
    nom_fichier_sortie = f"{nom_base}_trimmed.csv"
    chemin_sortie = os.path.join(DOSSIER_SORTIE, nom_fichier_sortie)

    # 2. Génération des noms pour la Null Class (Nothing)
    parts = nom_fichier.split('_', 1)
    suffix_with_ext = parts[1] if len(parts) == 2 else nom_fichier
    nom_sans_ext_suffix, ext = os.path.splitext(suffix_with_ext)
    
    if nom_sans_ext_suffix.endswith('_train'):
        base_suf = nom_sans_ext_suffix[:-6] # Enlève '_train'
        nom_avant = f"Nothing_{base_suf}_1_trimmed{ext}"
        nom_apres = f"Nothing_{base_suf}_2_trimmed{ext}"
    else:
        nom_avant = f"Nothing_{nom_sans_ext_suffix}_1{ext}"
        nom_apres = f"Nothing_{nom_sans_ext_suffix}_2{ext}"

    chemin_avant = os.path.join(DOSSIER_SORTIE, nom_avant)
    chemin_apres = os.path.join(DOSSIER_SORTIE, nom_apres)

    if os.path.exists(chemin_sortie):
        print(f"⏩ Déjà rogné, on saute : {nom_fichier_sortie}")
        return

    nom_exo = nom_sans_extension.split('_')[0]
    params = PARAMETRES_ROGNAGE.get(nom_exo, PARAMETRES_ROGNAGE["Defaut"])
    capteur_cible = params["capteur"]
    taille_fenetre_sec = params["fenetre"]
    seuil_periodicite = params["seuil_stac"]
    seuil_energie_min = params["seuil_energie"]

    print(f"\n📥 Chargement de : {nom_fichier}")
    print(f"⚙️ Paramètres appliqués ({nom_exo}) -> Capteur: {capteur_cible} | Fenêtre: {taille_fenetre_sec}s | Seuil: {seuil_periodicite}")
    
    df = pd.read_csv(chemin_entree)

    taille_fenetre_pts = int(taille_fenetre_sec * FREQUENCE)
    pas_glissement_pts = int(PAS_GLISSEMENT_SEC * FREQUENCE)
    total_pts = len(df)

    temps_stac = []
    scores_stac = []

    print("🔄 Calcul de l'algorithme STAC (Veuillez patienter)...")
    horizon_recherche_pts = int(HORIZON_RECHERCHE_SEC * FREQUENCE)

    def calculer_score_disjoint(signal, idx_ref):
        W_ref = signal[idx_ref : idx_ref + taille_fenetre_pts]
        
        # Application dynamique du seuil d'énergie
        if np.var(W_ref) < seuil_energie_min: return 0.0
            
        W_ref_centree = W_ref - np.mean(W_ref)
        energie_ref = np.sum(W_ref_centree**2)
        if energie_ref == 0: return 0.0
            
        max_pearson = 0.0
        
        # Limitation de la recherche (Horizon local)
        idx_start = max(0, idx_ref - horizon_recherche_pts)
        idx_end = min(total_pts - taille_fenetre_pts, idx_ref + horizon_recherche_pts)
        
        for idx_test in range(idx_start, idx_end, pas_glissement_pts):
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
        if capteur_cible == "Acc":
            score_x = calculer_score_disjoint(df['Acc_X'].values, debut)
            score_y = calculer_score_disjoint(df['Acc_Y'].values, debut)
            score_z = calculer_score_disjoint(df['Acc_Z'].values, debut)
            score_final = max(score_x, score_y, score_z)
        else:
            score_x = calculer_score_disjoint(df['Gyr_X'].values, debut)
            score_y = calculer_score_disjoint(df['Gyr_Y'].values, debut)
            score_z = calculer_score_disjoint(df['Gyr_Z'].values, debut)
            score_final = max(score_x, score_y, score_z)
                
        temps_stac.append(df['Temps_s'].iloc[debut + taille_fenetre_pts//2])
        scores_stac.append(score_final)

    scores_stac = np.array(scores_stac)
    temps_stac = np.array(temps_stac)

    zones_actives = np.where(scores_stac > seuil_periodicite)[0]
    if len(zones_actives) > 0:
        debut_serie_sec = max(0, temps_stac[zones_actives[0]] - 0.5)
        fin_serie_sec = min(df['Temps_s'].max(), temps_stac[zones_actives[-1]] + 0.5)
    else:
        debut_serie_sec, fin_serie_sec = 0.0, df['Temps_s'].max()

    pg.setConfigOptions(antialias=True)
    pg.setConfigOption('background', 'w') 
    pg.setConfigOption('foreground', 'k') 

    win = pg.GraphicsLayoutWidget(title=f"Éditeur de Rognage : {nom_fichier}")
    win.showMaximized() 
    
    label = win.addLabel(
        f"<b>{nom_fichier}</b> (Mode: {nom_exo})<br>"
        "<span style='color: #27ae60;'><b>Glissez les bords du bloc vert</b></span> pour encadrer l'exercice.<br>"
        "<i>Ce qui est en dehors sera classé comme 'Nothing' (Repos).</i><br>"
        "<b>ENTRÉE</b>: Sauvegarder (3 fichiers) | <b>ÉCHAP</b>: Ignorer | <b>Q</b>: Quitter", 
        row=0, col=0, colspan=1
    )
    
    p1 = win.addPlot(row=1, col=0, title="Accéléromètre (3 axes bruts)")
    p2 = win.addPlot(row=2, col=0, title="Gyroscope (3 axes bruts)")
    p3 = win.addPlot(row=3, col=0, title=f"Score STAC ciblé ({capteur_cible}) (Seuil dynamique: {seuil_periodicite})")

    p2.setXLink(p1)
    p3.setXLink(p1)

    temps = df['Temps_s'].values
    
    pen_x = pg.mkPen(color=(231, 76, 60), width=1.5)
    pen_y = pg.mkPen(color=(46, 204, 113), width=1.5)
    pen_z = pg.mkPen(color=(52, 152, 219), width=1.5)
    pen_score = pg.mkPen(color=(211, 84, 0), width=2)

    p1.plot(temps, df['Acc_X'].values, pen=pen_x, name='X')
    p1.plot(temps, df['Acc_Y'].values, pen=pen_y, name='Y')
    p1.plot(temps, df['Acc_Z'].values, pen=pen_z, name='Z')

    p2.plot(temps, df['Gyr_X'].values, pen=pen_x)
    p2.plot(temps, df['Gyr_Y'].values, pen=pen_y)
    p2.plot(temps, df['Gyr_Z'].values, pen=pen_z)

    p3.plot(temps_stac, scores_stac, pen=pen_score)
    ligne_seuil = pg.InfiniteLine(angle=0, movable=False, pos=seuil_periodicite, pen=pg.mkPen('g', style=pg.QtCore.Qt.PenStyle.DashLine))
    p3.addItem(ligne_seuil)

    regions = []
    
    def update_regions(region_item):
        vmin, vmax = region_item.getRegion()
        for r in regions:
            if r != region_item:
                r.blockSignals(True) 
                r.setRegion([vmin, vmax])
                r.blockSignals(False)

    brush_color = pg.mkBrush(46, 204, 113, 50) 
    for p in [p1, p2, p3]:
        region = pg.LinearRegionItem([debut_serie_sec, fin_serie_sec], brush=brush_color)
        region.setZValue(10)
        p.addItem(region)
        region.sigRegionChanged.connect(lambda r=region: update_regions(r))
        regions.append(region)

    def on_key_press(ev):
        key = ev.key()
        if key in [16777220, 16777221]: # Touche Entrée
            vmin, vmax = regions[0].getRegion()
            
            # --- 1. PARTIE AVANT (Nothing / Repos) ---
            df_avant = df[df['Temps_s'] < vmin].copy()
            if not df_avant.empty:
                df_avant['Temps_s'] = df_avant['Temps_s'] - df_avant['Temps_s'].iloc[0]
                df_avant.to_csv(chemin_avant, index=False)
                print(f"✅ Généré : Nothing (Avant) -> {nom_avant} [{len(df_avant)} lignes]")

            # --- 2. PARTIE CENTRALE (L'Exercice Pûr) ---
            df_rogne = df[(df['Temps_s'] >= vmin) & (df['Temps_s'] <= vmax)].copy()
            if not df_rogne.empty:
                df_rogne['Temps_s'] = df_rogne['Temps_s'] - df_rogne['Temps_s'].iloc[0]
                df_rogne.to_csv(chemin_sortie, index=False)
                print(f"✅ Généré : Exercice Pûr -> {nom_fichier_sortie} [{len(df_rogne)} lignes]")

            # --- 3. PARTIE APRÈS (Nothing / Repos) ---
            df_apres = df[df['Temps_s'] > vmax].copy()
            if not df_apres.empty:
                df_apres['Temps_s'] = df_apres['Temps_s'] - df_apres['Temps_s'].iloc[0]
                df_apres.to_csv(chemin_apres, index=False)
                print(f"✅ Généré : Nothing (Après) -> {nom_apres} [{len(df_apres)} lignes]")
            
            win.close()
            app.quit() 
            
        elif key == 16777216: # Touche Échap
            print(f"⏩ Fichier ignoré.")
            win.close()
            app.quit()
            
        elif key in [81, 113]: # Touche Q
            print("🛑 Arrêt manuel du programme.")
            sys.exit(0)

    win.keyPressEvent = on_key_press
    app.exec()

if __name__ == "__main__":
    if not os.path.exists(DOSSIER_ENTREE):
        print(f"Erreur : Le dossier {DOSSIER_ENTREE} n'existe pas.")
        sys.exit(1)

    tous_fichiers_csv = [f for f in os.listdir(DOSSIER_ENTREE) if f.endswith('.csv')]
    
    fichiers_a_traiter = []
    for fichier in tous_fichiers_csv:
        nom_sans_ext = os.path.splitext(fichier)[0]
        nom_base = nom_sans_ext.replace('_train', '') if nom_sans_ext.endswith('_train') else nom_sans_ext
        chemin_verif = os.path.join(DOSSIER_SORTIE, f"{nom_base}_trimmed.csv")
        
        if not os.path.exists(chemin_verif):
            fichiers_a_traiter.append(fichier)
        else:
            pass # Fichier déjà traité
    
    if not fichiers_a_traiter:
        print(f"✅ Super ! Les {len(tous_fichiers_csv)} fichiers ont déjà été traités. Fin du programme.")
    else:
        print(f"🚀 Démarrage de l'outil interactif ({len(fichiers_a_traiter)} restants sur {len(tous_fichiers_csv)})...")
        app = pg.mkQApp("TrackWatch Éditeur")
        
        for fichier in fichiers_a_traiter:
            traiter_fichier_interactif(fichier, app)
            
        print("🎉 Terminé ! Tous les fichiers ont été découpés en Exercice + Nothing.")