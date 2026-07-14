package com.example.trackwatch.presentation

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.LinearLayout
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.net.InetSocketAddress
import java.net.Socket

class MenuLocalActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = android.view.Gravity.CENTER
        }

        val btnNouveau = Button(this).apply { text = "🔴 NOUVEAU" }
        val btnGerer = Button(this).apply { text = "🗑️ GÉRER" }
        val btnEnvoyer = Button(this).apply { text = "📤 ENVOYER PC" }

        // Nouveau bouton Retour
        val btnRetour = Button(this).apply {
            text = "⬅️ RETOUR"
            textSize = 12f
        }

        btnNouveau.setOnClickListener {
            val intent = Intent(this, SelecteurActivity::class.java)
            intent.putExtra("MODE", "LOCAL")
            startActivity(intent)
        }

        btnGerer.setOnClickListener {
            startActivity(Intent(this, GestionFichiersActivity::class.java))
        }

        btnEnvoyer.setOnClickListener {
            //  REMPLACER PAR LA VRAIE IP DU PC
            val pcIpAddress = "192.168.1.56"
            val port = 5005

            val dossier = filesDir
            val fichiers = dossier.listFiles { _, name -> name.endsWith(".csv") }

            if (fichiers == null || fichiers.isEmpty()) {
                Toast.makeText(this, "Aucun fichier à envoyer", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            Toast.makeText(this, "Tentative de connexion...", Toast.LENGTH_SHORT).show()

            lifecycleScope.launch(Dispatchers.IO) {
                for (fichier in fichiers) {
                    try {
                        val socket = Socket()
                        socket.connect(InetSocketAddress(pcIpAddress, port), 3000)

                        val outStream = socket.getOutputStream()
                        val inStream = socket.getInputStream()

                        outStream.write("${fichier.name}\n".toByteArray())
                        outStream.flush()

                        val reponse = ByteArray(2)
                        inStream.read(reponse)

                        val bytes = fichier.readBytes()
                        outStream.write(bytes)
                        outStream.flush()

                        socket.close()

                        withContext(Dispatchers.Main) {
                            Toast.makeText(this@MenuLocalActivity, "✅ ${fichier.name} envoyé !", Toast.LENGTH_SHORT).show()
                        }
                    } catch (e: Exception) {
                        e.printStackTrace()
                        withContext(Dispatchers.Main) {
                            Toast.makeText(this@MenuLocalActivity, "❌ Erreur PC : ${e.message}", Toast.LENGTH_LONG).show()
                        }
                    }
                }
            }
        }

        btnRetour.setOnClickListener {
            finish()
        }

        layout.addView(btnNouveau)
        layout.addView(btnGerer)
        layout.addView(btnEnvoyer)
        layout.addView(btnRetour)

        setContentView(layout)
    }
}