import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.integrate import cumulative_trapezoid
import os

# ==========================================
# ⚙️ 1. CONFIGURATION
# ==========================================
DOSSIER_SCRIPT = os.path.dirname(os.path.abspath(__file__))

NOM_DOSSIER = '04_data_ACP'
NOM_FICHIER = 'Pecfly_20260721_194732_trimmed_acp.csv' 

CHEMIN_FICHIER_CSV = os.path.join(DOSSIER_SCRIPT, NOM_DOSSIER, NOM_FICHIER)

PARAMETRES_BIOMECA = {
    "Squat": {
        "capteur": "Acc", "hauteur_min": 3, "distance_sec": 1.2, "chute_min": 2.5,
        "seuil_variance": 0.2, "duree_pause_sec": 0.8, "seuil_amp": 0.15, "phase_1": "excentrique"
    },
    "Benchpress": {
        "capteur": "Acc", "hauteur_min": 4.0, "distance_sec": 1.2, "chute_min": 2.0,
        "seuil_variance": 0.15, "duree_pause_sec": 0.8, "seuil_amp": 0.15, "phase_1": "excentrique"
    },
    "Curlbiceps": {
        "capteur": "Gyr", "hauteur_min": 1.5, "distance_sec": 1.0, "chute_min": 2.5,
        "seuil_variance": 0.5, "duree_pause_sec": 1, "seuil_amp": 0.20, "phase_1": "concentrique"
    },
    "Barbellrow": {
        "capteur": "Acc", "hauteur_min": 2.0, "distance_sec": 1.0, "chute_min": 1.5,
        "seuil_variance": 0.1, "duree_pause_sec": 0.5, "seuil_amp": 0.10, "phase_1": "concentrique"
    },
    "Onearmdumbellrow": {
        "capteur": "Acc", "hauteur_min": 5.0, "distance_sec": 1.0, "chute_min": 5,
        "seuil_variance": 0.8, "duree_pause_sec": 0.5, "seuil_amp": 0.10, "phase_1": "concentrique"
    },
    "Overheadtricepsextension": {
        "capteur": "Gyr", "hauteur_min": 2.0, "distance_sec": 1.0, "chute_min": 1.5,
        "seuil_variance": 0.05, "duree_pause_sec": 0.5, "seuil_amp": 0.15, "phase_1": "concentrique"
    },
    "Pecfly": {
        "capteur": "Gyr", "hauteur_min": 1.5, "distance_sec": 1.0, "chute_min":3,
        "seuil_variance": 0.05, "duree_pause_sec": 0.5, "seuil_amp": 0.15, "phase_1": "concentrique"
    },
    "RDL": {
        "capteur": "Acc", "hauteur_min": 5.0, "distance_sec": 2, "chute_min": 2,
        "seuil_variance": 0.2, "duree_pause_sec": 0.7, "seuil_amp": 0.10, "phase_1": "concentrique"
    },
    "Reardelt": {
        "capteur": "Gyr", "hauteur_min": 1, "distance_sec": 0.6, "chute_min": 1.5,
        "seuil_variance": 0.05, "duree_pause_sec": 0.5, "seuil_amp": 0.7, "phase_1": "concentrique"
    },
    "Hipthrust": {
        "capteur": "Gyr", "hauteur_min": 2.0, "distance_sec": 1.0, "chute_min": 1.5,
        "seuil_variance": 0.05, "duree_pause_sec": 0.5, "seuil_amp": 0.15, "phase_1": "excentrique"
    },
    "Defaut": {
        "capteur": "Gyr", "hauteur_min": 2.0, "distance_sec": 1.0, "chute_min": 1.5,
        "seuil_variance": 0.05, "duree_pause_sec": 0.5, "seuil_amp": 0.10, "phase_1": "excentrique"
    },
}

# ==========================================
# 🏔️ 2. DÉTECTEURS D'HYSTÉRÉSIS ET SILENCES
# ==========================================
def detecteur_pics_et_silences(signal, seuil_hauteur, distance_pts, chute_min):
    pics = []
    max_val = -float('inf')
    max_pos = -1
    en_montee = True
    dernier_pic_pos = -distance_pts 

    for i in range(1, len(signal)):
        val = signal[i]
        if en_montee:
            if val > max_val:
                max_val = val
                max_pos = i
            elif val <= max_val - chute_min:
                en_montee = False
                if max_val >= seuil_hauteur and (max_pos - dernier_pic_pos) >= distance_pts:
                    pics.append(max_pos)
                    dernier_pic_pos = max_pos
        else:
            if val > signal[i-1]: 
                en_montee = True
                max_val = val
                max_pos = i
    if en_montee and max_val >= seuil_hauteur and (max_pos - dernier_pic_pos) >= distance_pts:
        pics.append(max_pos)
    return pics

def detecter_zones_immobiles(signal, frequence, seuil_variance=0.1, duree_min_sec=0.5):
    fenetre_pts = int(duree_min_sec * frequence)
    ancres_silence = []
    for i in range(0, len(signal) - fenetre_pts, fenetre_pts // 2):
        morceau = signal[i : i + fenetre_pts]
        if np.var(morceau) < seuil_variance:
            ancres_silence.append(i + fenetre_pts // 2)
    return ancres_silence

def detecter_tops_bottoms_amplitude(amplitude, seuil_amp):
    tops, bottoms = [], []
    max_val = min_val = amplitude[0]
    max_pos = min_pos = 0
    etat = None 
    
    for i in range(1, len(amplitude)):
        val = amplitude[i]
        if etat is None:
            if val >= min_val + seuil_amp:
                etat = 'MONTEE'
                max_val, max_pos = val, i
                bottoms.append(min_pos) 
            elif val <= max_val - seuil_amp:
                etat = 'DESCENTE'
                min_val, min_pos = val, i
                tops.append(max_pos)
            else:
                if val > max_val: max_val, max_pos = val, i
                if val < min_val: min_val, min_pos = val, i
        elif etat == 'MONTEE':
            if val > max_val:
                max_val, max_pos = val, i
            elif val <= max_val - seuil_amp:
                tops.append(max_pos)
                etat = 'DESCENTE'
                min_val, min_pos = val, i
        elif etat == 'DESCENTE':
            if val < min_val:
                min_val, min_pos = val, i
            elif val >= min_val + seuil_amp:
                bottoms.append(min_pos)
                etat = 'MONTEE'
                max_val, max_pos = val, i
                
    if etat == 'MONTEE': tops.append(max_pos)
    elif etat == 'DESCENTE': bottoms.append(min_pos)
    return tops, bottoms

# ==========================================
# 🧮 3. FONCTION D'INTÉGRATION (PASSE 1 - DÉCOUVERTE)
# ==========================================
def integrer_avec_ancres_3d(pc1, pc2, pc3, ancres, dt, capteur="Acc"):
    N = len(pc1)
    def traiter_canal(signal):
        if capteur == "Acc":
            v_corr = np.zeros(N)
            for i in range(len(ancres) - 1):
                idx_d, idx_f = ancres[i], ancres[i+1]
                seg = signal[idx_d:idx_f+1]
                if len(seg) < 2: continue
                v_brute = cumulative_trapezoid(seg, dx=dt, initial=0)
                derive_v = np.linspace(v_brute[0], v_brute[-1], len(seg))
                v_corr[idx_d:idx_f+1] = v_brute - derive_v
            p_corr = cumulative_trapezoid(v_corr, dx=dt, initial=0)
            return v_corr, p_corr
        elif capteur == "Gyr":
            derive_v = np.linspace(signal[0], signal[-1], N)
            v_corr = signal - derive_v
            p_corr = cumulative_trapezoid(v_corr, dx=dt, initial=0)
            return v_corr, p_corr

    v1, p1 = traiter_canal(pc1)
    v2, p2 = traiter_canal(pc2)
    v3, p3 = traiter_canal(pc3)
    return v1, p1, v2, p2, v3, p3

# ==========================================
# 🚀 4. LECTURE ET ANALYSE GLOBALE
# ==========================================
if __name__ == "__main__":
    print(f"📥 Lecture de {CHEMIN_FICHIER_CSV}...")
    
    if not os.path.exists(CHEMIN_FICHIER_CSV):
        print(f"❌ Erreur : Le fichier {CHEMIN_FICHIER_CSV} est introuvable !")
        exit()
        
    nom_fichier = os.path.basename(CHEMIN_FICHIER_CSV)
    exercice_extrait = nom_fichier.split('_')[0]
    
    df = pd.read_csv(CHEMIN_FICHIER_CSV)
    t = df['Temps_s'].values
    dt = t[1] - t[0] 
    frequence = 1.0 / dt

    params = PARAMETRES_BIOMECA.get(exercice_extrait, PARAMETRES_BIOMECA["Defaut"])
    prefixe = params["capteur"]
    pc1 = df[f'{prefixe}_PC1'].values
    pc2 = df[f'{prefixe}_PC2'].values
    pc3 = df[f'{prefixe}_PC3'].values

    # Zeroing initial
    pc1 = pc1 - pc1[0]
    pc2 = pc2 - pc2[0]
    pc3 = pc3 - pc3[0]

    # --- PASSE 1 : DÉCOUVERTE (L'Échafaudage) ---
    dist_pts = int(params["distance_sec"] * frequence)
    pics = detecteur_pics_et_silences(pc1, seuil_hauteur=params["hauteur_min"], distance_pts=dist_pts, chute_min=params["chute_min"])
    ancres_silence = detecter_zones_immobiles(pc1, frequence, seuil_variance=params["seuil_variance"], duree_min_sec=params["duree_pause_sec"])
    ancres = sorted(list(set([0] + list(pics) + list(ancres_silence) + [len(pc1) - 1])))
    
    v1_decouverte, p1_decouverte, _, _, _, _ = integrer_avec_ancres_3d(pc1, pc2, pc3, ancres, dt, capteur=params["capteur"])

    # Recherche des Tops et Bottoms sur la courbe d'Amplitude de Découverte
    tops, bottoms = detecter_tops_bottoms_amplitude(p1_decouverte, seuil_amp=params.get("seuil_amp", 0.1))
    events = [(idx, 'TOP') for idx in tops] + [(idx, 'BOTTOM') for idx in bottoms]
    events.sort(key=lambda x: x[0])

    phase_1_type = params["phase_1"]
    reps = []
    
    if len(events) >= 3:
        for i in range(0, len(events) - 2, 2):
            e1, e2, e3 = events[i], events[i+1], events[i+2]
            if e1[1] != e2[1] and e2[1] != e3[1]:
                seg1 = (e1[0], e2[0])
                seg2 = (e2[0], e3[0])
                if phase_1_type == "excentrique":
                    reps.append({'exc': seg1, 'conc': seg2})
                else:
                    reps.append({'conc': seg1, 'exc': seg2})

    # ==========================================
    # 🎯 PASSE 2 : HAUTE PRÉCISION (RÉ-INTÉGRATION TOP-TO-TOP)
    # ==========================================
    unite_capteur = "m/s²" if params["capteur"] == "Acc" else "rad/s²"
    unite_vit = "m/s" if params["capteur"] == "Acc" else "rad/s"
    unite_pos = "cm" if params["capteur"] == "Acc" else "degrés"
    facteur_pos = 100 if params["capteur"] == "Acc" else np.degrees(1)

    print("\n" + "="*65)
    print(f"📊 ANALYSE DÉTAILLÉE : {exercice_extrait.upper()} ({len(reps)} Reps validées)")
    print("="*65)

    totaux_t_exc, totaux_t_conc, totaux_t_pause = 0, 0, 0
    v_seuil = 0.05 if params["capteur"] == "Acc" else 0.1
    
    segments_affines = []

    if len(reps) > 0:
        for i, rep in enumerate(reps):
            idx_exc_start, idx_exc_end = rep['exc']
            idx_conc_start, idx_conc_end = rep['conc']
            
            # Les limites absolues de la répétition (Du Top initial au Top final)
            idx_start_rep = min(idx_exc_start, idx_conc_start)
            idx_end_rep = max(idx_exc_end, idx_conc_end)
            
            # Extraction des données brutes pour cette fenêtre précise
            seg_acc = pc1[idx_start_rep : idx_end_rep + 1]
            N_seg = len(seg_acc)
            
            # --- RÉ-INTÉGRATION LOCALE ---
            if params["capteur"] == "Acc":
                # 1. ZUPT Local (v_start = 0, v_end = 0) - Plus aucune ancre au milieu !
                v_brute = cumulative_trapezoid(seg_acc, dx=dt, initial=0)
                derive_v = np.linspace(v_brute[0], v_brute[-1], N_seg)
                v_propre = v_brute - derive_v
                
                # 2. ZPUT Local (p_start = 0, p_end = 0)
                p_brute = cumulative_trapezoid(v_propre, dx=dt, initial=0)
                derive_p = np.linspace(p_brute[0], p_brute[-1], N_seg)
                p_propre = p_brute - derive_p
                
            elif params["capteur"] == "Gyr":
                # Vitesse angulaire forcée à 0 aux extrémités
                derive_v = np.linspace(seg_acc[0], seg_acc[-1], N_seg)
                v_propre = seg_acc - derive_v
                
                # Angle forcé à 0 aux extrémités
                p_brute = cumulative_trapezoid(v_propre, dx=dt, initial=0)
                derive_p = np.linspace(p_brute[0], p_brute[-1], N_seg)
                p_propre = p_brute - derive_p

            # Sauvegarde pour l'affichage graphique
            segments_affines.append({
                't': t[idx_start_rep : idx_end_rep + 1],
                'v_propre': v_propre,
                'p_propre': p_propre
            })

            # --- Calcul des métriques sur ces nouvelles courbes pures ---
            
            # 1. Amplitude Absolue
            amp = np.max(np.abs(p_propre)) * facteur_pos
            
            # 2. Re-création des index locaux pour cibler les bonnes phases
            loc_conc_start = idx_conc_start - idx_start_rep
            loc_conc_end = idx_conc_end - idx_start_rep
            loc_exc_start = idx_exc_start - idx_start_rep
            loc_exc_end = idx_exc_end - idx_start_rep
            
            # 3. Vitesse Max sur le Concentrique
            v_conc_segment = v_propre[loc_conc_start:loc_conc_end]
            vmax_conc = np.max(np.abs(v_conc_segment)) if len(v_conc_segment) > 0 else 0
            
            # 4. Accélération Max Directionnelle (sur les données brutes)
            acc_conc_segment = seg_acc[loc_conc_start:loc_conc_end]
            deplacement_conc = p_propre[loc_conc_end] - p_propre[loc_conc_start]
            signe_mvt = np.sign(deplacement_conc)
            
            if signe_mvt == 1:
                acc_motrice = acc_conc_segment[acc_conc_segment > 0]
            else:
                acc_motrice = acc_conc_segment[acc_conc_segment < 0]
            acc_max = np.max(np.abs(acc_motrice)) if len(acc_motrice) > 0 else 0
            
            # 5. Tempos Actifs (basés sur la nouvelle vitesse propre)
            v_exc_segment = v_propre[loc_exc_start:loc_exc_end]
            t_exc_actif = np.sum(np.abs(v_exc_segment) >= v_seuil) * dt
            t_conc_actif = np.sum(np.abs(v_conc_segment) >= v_seuil) * dt
            
            t_pause_exc = np.sum(np.abs(v_exc_segment) < v_seuil) * dt
            t_pause_conc = np.sum(np.abs(v_conc_segment) < v_seuil) * dt
            t_pause_totale = t_pause_exc + t_pause_conc
            
            totaux_t_exc += t_exc_actif
            totaux_t_conc += t_conc_actif
            totaux_t_pause += t_pause_totale
            
            # 6. Variance PC2 et PC3
            var_pc2 = np.var(pc2[idx_start_rep:idx_end_rep])
            var_pc3 = np.var(pc3[idx_start_rep:idx_end_rep])
            
            print(f"🔸 REP {i+1} :")
            print(f"   📏 Amplitude      : {amp:.1f} {unite_pos} (Intégration Pure Top-to-Top)")
            print(f"   🚀 Vitesse Max    : {vmax_conc:.2f} {unite_vit} (Phase Concentrique)")
            print(f"   💥 Accélér. Max   : {acc_max:.2f} {unite_capteur} (Explosivité brute)")
            print(f"   ⏱️ Tempo Actif    : Exc. {t_exc_actif:.1f}s | Conc. {t_conc_actif:.1f}s | Pause {t_pause_totale:.1f}s")
            print(f"   ⚖️ Variance Bruit : PC2 = {var_pc2:.2f} | PC3 = {var_pc3:.2f}")
            print("-" * 65)
            
        print(f"🏆 TEMPOS MOYENS DE LA SÉRIE :")
        print(f"   -> Excentrique (Freinage)  : {totaux_t_exc/len(reps):.2f} s")
        print(f"   -> Concentrique (Poussée)  : {totaux_t_conc/len(reps):.2f} s")
        print(f"   -> Pauses cumulées         : {totaux_t_pause:.1f} s")
        print("="*65 + "\n")
    else:
        print("⚠️ Aucune répétition complète détectée par l'algorithme d'amplitude.")

    # --- D. AFFICHAGE GRAPHIQUE ---
    fig, axes = plt.subplots(4, 1, figsize=(14, 12), sharex=True)
    fig.canvas.manager.set_window_title(f'Pipeline Anti-Dérive (Algorithme 2 Passes)')
    
    # 1. GRAPHIQUE ACCÉLÉRATION
    axes[0].plot(t, pc1, color='#e74c3c', label=f"{prefixe}_PC1")
    axes[0].plot(t[pics], pc1[pics], "D", color='black', markersize=8, label="Pics Hystérésis (Passe 1)")
    if len(ancres_silence) > 0:
        axes[0].plot(t[ancres_silence], pc1[ancres_silence], "o", color='blue', markersize=8, label="Ancres Repos (Passe 1)")
    axes[0].set_title(f"1. PC1 ({unite_capteur})")
    axes[0].legend(loc="upper right")
    
    # 2. GRAPHIQUE VITESSE (Comparaison Découverte vs Haute Précision)
    axes[1].plot(t, v1_decouverte, color='#3498db', alpha=0.3, linewidth=1.5, label="Vitesse Passe 1 (Avec ancres milieu)")
    for idx, seg in enumerate(segments_affines):
        lbl = "Vitesse Passe 2 (Pure Top-to-Top)" if idx == 0 else None
        axes[1].plot(seg['t'], seg['v_propre'], color='#2980b9', linewidth=2.5, label=lbl)
    axes[1].set_title(f"2. Vitesse Corrigée")
    axes[1].legend(loc="upper right")
    
    # 3. GRAPHIQUE AMPLITUDE (Comparaison Découverte vs Haute Précision)
    axes[2].plot(t, p1_decouverte * facteur_pos, color='#2ecc71', alpha=0.3, linewidth=1.5, label="Amplitude Passe 1 (Brouillon)")
    for idx, seg in enumerate(segments_affines):
        lbl = "Amplitude Passe 2 (ZPUT Top-to-Top)" if idx == 0 else None
        axes[2].plot(seg['t'], seg['p_propre'] * facteur_pos, color='#e67e22', linewidth=2.5, label=lbl)
        
    if len(tops) > 0:
        axes[2].plot(t[tops], p1_decouverte[tops] * facteur_pos, "o", color='green', alpha=0.5, markersize=6, label="Tops (Début/Fin)")
    if len(bottoms) > 0:
        axes[2].plot(t[bottoms], p1_decouverte[bottoms] * facteur_pos, "X", color='red', alpha=0.5, markersize=8, label="Bottoms (Inversion)")
        
    axes[2].set_title(f"3. Amplitude ({unite_pos})")
    axes[2].legend(loc="upper right")
    
    # 4. GRAPHIQUE TREMBLEMENTS
    axes[3].plot(t, pc3, color='#9b59b6', label=f"Stabilité Axe PC3 (Accélération pure)")
    axes[3].set_title(f"4. Analyse de Stabilité PC3")
    axes[3].set_xlabel("Temps (s)")
    axes[3].legend(loc="upper right")
    
    for ax in axes:
        for a in ancres: 
            ax.axvline(t[a], color='gray', linestyle='--', alpha=0.2)
        ax.grid(True, linestyle=':', alpha=0.6)
    
    plt.tight_layout()
    plt.show()