package com.example.trackwatch.presentation

import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import androidx.activity.ComponentActivity

class SelecteurActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val mode = intent.getStringExtra("MODE") ?: "LOCAL"

        val scrollView = ScrollView(this)

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = android.view.Gravity.CENTER
            setPadding(0, 40, 0, 40) // Un peu d'espace en haut et en bas pour respirer
        }
        scrollView.addView(layout)

        val tvTitre = TextView(this).apply {
            text = "CHOISIS UN EXERCICE"
            textSize = 14f
            setTextColor(Color.WHITE)
            gravity = android.view.Gravity.CENTER
            setPadding(0, 0, 0, 20)
        }
        layout.addView(tvTitre)

        val exercices = listOf(
            "Squat",
            "RDL",
            "Deadlift",
            "Benchpress",
            "Pecfly",
            "Inclinedbenchpress",
            "Militarypress",
            "Lateralraise",
            "Pullup",
            "Barbellrow",
            "Latpulldown",
            "Onearmdumbellrow",
            "Curlbiceps",
        )

        for (exo in exercices) {
            val btn = Button(this).apply {
                text = exo
                // On ajoute des marges pour que les boutons ne soient pas collés
                val params = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
                )
                params.setMargins(20, 10, 20, 10)
                layoutParams = params
            }

            btn.setOnClickListener {
                val intent = Intent(this, DecompteActivity::class.java)
                intent.putExtra("MODE", mode)
                intent.putExtra("EXERCICE", exo)
                startActivity(intent)
            }
            layout.addView(btn)
        }

        val btnRetour = Button(this).apply {
            text = "⬅️ RETOUR"
            textSize = 12f
            val params = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
            params.setMargins(20, 30, 20, 10)
            layoutParams = params
        }
        btnRetour.setOnClickListener { finish() }
        layout.addView(btnRetour)

        setContentView(scrollView)
    }
}

