package com.example.trackwatch.presentation

import android.content.Intent
import android.graphics.Color
import android.graphics.Typeface
import android.os.Bundle
import android.view.Gravity
import android.view.ViewGroup
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.activity.ComponentActivity

class WeightPickerActivity : ComponentActivity() {

    private var currentWeight = 20 // Poids par défaut : 20kg (barre à vide)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val exerciceDetecte = SessionManager.predictedExercise

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            layoutParams = ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT)
            setBackgroundColor(Color.parseColor("#121212"))
            setPadding(10, 20, 10, 20)
        }

        val tvTitre = TextView(this).apply {
            text = "🏋️ $exerciceDetecte détecté"
            textSize = 12f
            setTextColor(Color.parseColor("#4CAF50"))
            gravity = Gravity.CENTER
            layoutParams = LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f)
        }

        // --- Contrôles du poids (Ligne horizontale) ---
        val controlsLayout = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER
            layoutParams = LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 1.5f)
        }

        val btnMinus = Button(this).apply {
            text = "-"
            textSize = 24f
            layoutParams = LinearLayout.LayoutParams(100, 100).apply { setMargins(10, 0, 10, 0) }
        }

        val tvPoids = TextView(this).apply {
            text = "$currentWeight kg"
            textSize = 28f
            typeface = Typeface.DEFAULT_BOLD
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
            layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
        }

        val btnPlus = Button(this).apply {
            text = "+"
            textSize = 24f
            layoutParams = LinearLayout.LayoutParams(100, 100).apply { setMargins(10, 0, 10, 0) }
        }

        btnMinus.setOnClickListener {
            if (currentWeight > 0) currentWeight -= 5
            tvPoids.text = "$currentWeight kg"
        }

        btnPlus.setOnClickListener {
            currentWeight += 5
            tvPoids.text = "$currentWeight kg"
        }

        controlsLayout.addView(btnMinus)
        controlsLayout.addView(tvPoids)
        controlsLayout.addView(btnPlus)

        // --- Bouton Sauvegarder ---
        val btnSave = Button(this).apply {
            text = "SAUVEGARDER"
            setBackgroundColor(Color.parseColor("#2980b9"))
            setTextColor(Color.WHITE)
            layoutParams = LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f)
        }

        btnSave.setOnClickListener {
            val processor = SignalProcessor(this)
            processor.saveToCsv(exerciceDetecte, currentWeight)

            Toast.makeText(this, "✅ Série enregistrée !", Toast.LENGTH_SHORT).show()

            SessionManager.clear() // On vide la RAM
            val intent = Intent(this, MainActivity::class.java)
            intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP
            startActivity(intent)
            finish()
        }

        layout.addView(tvTitre)
        layout.addView(controlsLayout)
        layout.addView(btnSave)

        setContentView(layout)
    }
}