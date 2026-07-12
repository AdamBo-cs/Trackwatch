import socket

TCP_IP = "0.0.0.0" # Écoute sur toutes les adresses
TCP_PORT = 5005    # Port différent du mode en ligne

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((TCP_IP, TCP_PORT))
sock.listen(1)

print(f" Serveur de fichiers activé sur le port {TCP_PORT}")
print("En attente de la montre...")

while True:
    conn, addr = sock.accept()
    print(f"\n Montre connectée depuis {addr}")
    
    try:
        # 1. Lire le nom du fichier lettre par lettre jusqu'au saut de ligne
        nom_fichier = ""
        while True:
            char = conn.recv(1).decode('utf-8')
            if char == '\n':
                break
            nom_fichier += char
            
        nom_fichier = nom_fichier.strip()
        if not nom_fichier:
            continue
        
        print(f"Réception du fichier : {nom_fichier}...")
        
        # 2. Envoyer "OK" à la montre pour donner le feu vert
        conn.send(b"OK")
        
        # 3. Recevoir toutes les données du fichier
        donnees = b""
        while True:
            packet = conn.recv(4096)
            if not packet:
                break
            donnees += packet
            
        # 4. Sauvegarder sur le PC
        with open(nom_fichier, "wb") as f:
            f.write(donnees)
            
        print(f"Succès ! Fichier sauvegardé ({len(donnees)} octets).")
        
    except Exception as e:
        print(f"Erreur: {e}")
    finally:
        conn.close()