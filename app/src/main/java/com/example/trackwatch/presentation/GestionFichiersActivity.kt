package com.example.trackwatch.presentation

import android.os.Bundle
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.activity.ComponentActivity
import java.io.File

class GestionFichiersActivity : ComponentActivity() {

    private lateinit var layoutListe: LinearLayout

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val scrollView = ScrollView(this)
        layoutListe = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = android.view.Gravity.CENTER_HORIZONTAL
            setPadding(0, 40, 0, 40)
        }

        scrollView.addView(layoutListe)
        setContentView(scrollView)

        chargerFichiers()
    }

    private fun chargerFichiers() {
        layoutListe.removeAllViews()

        val dossier = filesDir
        val fichiers = dossier.listFiles { _, name -> name.endsWith(".csv") }

        // Bouton Retour placé tout en haut ou tout en bas de la liste déroulante
        val btnRetour = Button(this).apply {
            text = "⬅️ RETOUR"
            textSize = 12f
        }
        btnRetour.setOnClickListener { finish() }
        layoutListe.addView(btnRetour)

        if (fichiers == null || fichiers.isEmpty()) {
            val vide = TextView(this).apply {
                text = "\nAucun fichier\nenregistré."
                gravity = android.view.Gravity.CENTER
            }
            layoutListe.addView(vide)
            return
        }

        for (fichier in fichiers) {
            val ligne = LinearLayout(this).apply {
                orientation = LinearLayout.HORIZONTAL
                gravity = android.view.Gravity.CENTER
            }

            val tvNom = TextView(this).apply {
                text = fichier.name
                setPadding(10, 10, 20, 10)
            }

            val btnSupprimer = Button(this).apply { text = "X" }
            btnSupprimer.setOnClickListener {
                if (fichier.delete()) {
                    Toast.makeText(this@GestionFichiersActivity, "${fichier.name} supprimé", Toast.LENGTH_SHORT).show()
                    chargerFichiers()
                }
            }

            ligne.addView(tvNom)
            ligne.addView(btnSupprimer)
            layoutListe.addView(ligne)
        }
    }
}