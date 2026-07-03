package com.example.trackwatch.presentation

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import androidx.activity.ComponentActivity

class SelecteurActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val modeChoisi = intent.getStringExtra("MODE") ?: "LOCAL"

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = android.view.Gravity.CENTER
        }

        val titre = TextView(this).apply {
            text = "Catégorie ?"
            textSize = 16f
            gravity = android.view.Gravity.CENTER
        }
        layout.addView(titre)

        val lettres = listOf("A", "B", "C")
        for (lettre in lettres) {
            val btn = Button(this).apply {
                text = "[ $lettre ]"
                textSize = 20f
            }
            btn.setOnClickListener {
                val intent = Intent(this@SelecteurActivity, DecompteActivity::class.java)
                intent.putExtra("MODE", modeChoisi)
                intent.putExtra("LETTRE", lettre)
                startActivity(intent)
                finish()
            }
            layout.addView(btn)
        }

        // Bouton retour
        val btnRetour = Button(this).apply {
            text = "⬅️ RETOUR"
            textSize = 12f
        }
        btnRetour.setOnClickListener {
            finish()
        }
        layout.addView(btnRetour)

        setContentView(layout)
    }
}