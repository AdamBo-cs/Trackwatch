package com.example.trackwatch.presentation

import android.content.Intent
import android.graphics.Color
import android.graphics.Typeface
import android.os.Bundle
import android.os.CountDownTimer
import android.view.Gravity
import android.view.ViewGroup
import android.widget.LinearLayout
import android.widget.TextView
import androidx.activity.ComponentActivity

class DecompteActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val mode = intent.getStringExtra("MODE") ?: "LOCAL"
        val exercice = intent.getStringExtra("EXERCICE") ?: "Inconnu"

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
            setBackgroundColor(Color.parseColor("#121212")) // Fond sombre
        }

        val tvTitre = TextView(this).apply {
            text = "PRÉPARE-TOI\n$exercice"
            textSize = 14f
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, 20)
        }

        val tvChiffre = TextView(this).apply {
            text = "3"
            textSize = 60f
            typeface = Typeface.DEFAULT_BOLD
            setTextColor(Color.parseColor("#4CAF50")) // Vert
            gravity = Gravity.CENTER
        }

        layout.addView(tvTitre)
        layout.addView(tvChiffre)
        setContentView(layout)

        object : CountDownTimer(3000, 1000) {
            override fun onTick(millisUntilFinished: Long) {
                // On rajoute +1 car le compteur de base affiche souvent 2, 1, 0
                val secondesRestantes = (millisUntilFinished / 1000) + 1
                tvChiffre.text = secondesRestantes.toString()
            }

            override fun onFinish() {
                tvChiffre.text = "GO!"

                val intent = Intent(this@DecompteActivity, EnregistrementActivity::class.java)
                intent.putExtra("MODE", mode)
                intent.putExtra("EXERCICE", exercice)
                startActivity(intent)

                finish()
            }
        }.start()
    }
}