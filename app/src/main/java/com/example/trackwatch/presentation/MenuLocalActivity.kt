package com.example.trackwatch.presentation

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.LinearLayout
import android.widget.Toast
import androidx.activity.ComponentActivity

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
            Toast.makeText(this, "Envoi en cours...", Toast.LENGTH_SHORT).show()
        }

        // Action du bouton retour : ferme cet écran
        btnRetour.setOnClickListener {
            finish()
        }

        layout.addView(btnNouveau)
        layout.addView(btnGerer)
        layout.addView(btnEnvoyer)
        layout.addView(btnRetour) // Ajout au visuel

        setContentView(layout)
    }
}