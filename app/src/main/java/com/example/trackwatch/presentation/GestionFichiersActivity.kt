package com.example.trackwatch.presentation

import android.graphics.Color
import android.os.Bundle
import android.text.TextUtils
import android.view.Gravity
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.activity.ComponentActivity
import java.io.File

class GestionFichiersActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val scrollView = ScrollView(this)
        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(20, 30, 20, 30) // Marges globales pour ne pas coller aux bords de la montre
        }
        scrollView.addView(layout)

        val tvTitre = TextView(this).apply {
            text = "FICHIERS"
            textSize = 14f
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, 20)
        }
        layout.addView(tvTitre)

        val dossier = filesDir
        val fichiers = dossier.listFiles { _, name -> name.endsWith(".csv") }

        if (fichiers == null || fichiers.isEmpty()) {
            layout.addView(TextView(this).apply {
                text = "Aucun fichier"
                setTextColor(Color.GRAY)
                gravity = Gravity.CENTER
            })
        } else {
            for (fichier in fichiers) {
                // Une "Row" est un conteneur horizontal (Texte à gauche, Bouton à droite)
                val row = LinearLayout(this).apply {
                    orientation = LinearLayout.HORIZONTAL
                    gravity = Gravity.CENTER_VERTICAL
                    layoutParams = LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.MATCH_PARENT,
                        LinearLayout.LayoutParams.WRAP_CONTENT
                    ).apply { setMargins(0, 0, 0, 15) }
                }

                val tvNom = TextView(this).apply {
                    text = fichier.name
                    textSize = 11f
                    setTextColor(Color.LTGRAY)

                    isSingleLine = true // Interdit au texte de faire plusieurs lignes
                    ellipsize = TextUtils.TruncateAt.MIDDLE // Met "..." au milieu (ex: "Pompes...022.csv")

                    // layout_width = 0 et weight = 1f : Prend l'espace restant, SANS écraser le bouton !
                    layoutParams = LinearLayout.LayoutParams(
                        0,
                        LinearLayout.LayoutParams.WRAP_CONTENT,
                        1f
                    ).apply { setMargins(0, 0, 10, 0) }
                }

                val btnDelete = Button(this).apply {
                    text = "❌"
                    // On force une taille carrée absolue (100x100 pixels) indélogeable
                    layoutParams = LinearLayout.LayoutParams(100, 100)
                    setPadding(0, 0, 0, 0) // Enlève les marges internes pour bien centrer la croix
                }

                // Action de suppression
                btnDelete.setOnClickListener {
                    if (fichier.delete()) {
                        layout.removeView(row) // Supprime la ligne de l'écran en temps réel
                        Toast.makeText(this@GestionFichiersActivity, "Supprimé !", Toast.LENGTH_SHORT).show()
                    }
                }

                row.addView(tvNom)
                row.addView(btnDelete)
                layout.addView(row)
            }
        }

        val btnRetour = Button(this).apply {
            text = "⬅️ RETOUR"
            textSize = 12f
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { setMargins(0, 20, 0, 0) }
            setOnClickListener { finish() }
        }
        layout.addView(btnRetour)

        setContentView(scrollView)
    }
}