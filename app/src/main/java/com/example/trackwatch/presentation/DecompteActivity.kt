package com.example.trackwatch.presentation

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import androidx.activity.ComponentActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

class DecompteActivity : ComponentActivity() {

    private var chronoJob: Job? = null // Permet de stopper le chrono si on clique sur retour

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val modeChoisi = intent.getStringExtra("MODE")
        val lettreChoisie = intent.getStringExtra("LETTRE")

        val tvChrono = TextView(this).apply {
            text = "3"
            textSize = 40f
            gravity = android.view.Gravity.CENTER
        }

        val btnRetour = Button(this).apply {
            text = "❌ ANNULER"
            textSize = 11f
        }

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = android.view.Gravity.CENTER
            addView(tvChrono)
            addView(btnRetour)
        }
        setContentView(layout)

        btnRetour.setOnClickListener {
            chronoJob?.cancel() // Arrête le compte à rebours en cours
            finish() // Ferme l'écran
        }

        // Lancement du chrono
        chronoJob = lifecycleScope.launch {
            delay(1000)
            tvChrono.text = "2"
            delay(1000)
            tvChrono.text = "1"
            delay(1000)
            tvChrono.text = "GO"
            delay(500)

            val intent = Intent(this@DecompteActivity, EnregistrementActivity::class.java)
            intent.putExtra("MODE", modeChoisi)
            intent.putExtra("LETTRE", lettreChoisie)
            startActivity(intent)
            finish()
        }
    }
}