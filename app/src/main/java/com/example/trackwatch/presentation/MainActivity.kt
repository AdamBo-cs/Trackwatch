package com.example.trackwatch.presentation

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.LinearLayout
import androidx.activity.ComponentActivity

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = android.view.Gravity.CENTER
        }

        val btnOnline = Button(this).apply { text = "📡 EN LIGNE" }
        val btnLocal = Button(this).apply { text = "💾 LOCAL" }

        layout.addView(btnOnline)
        layout.addView(btnLocal)
        setContentView(layout)

        btnOnline.setOnClickListener {
            val intent = Intent(this, SelecteurActivity::class.java)
            intent.putExtra("MODE", "ONLINE")
            startActivity(intent)
        }

        btnLocal.setOnClickListener {
            startActivity(Intent(this, MenuLocalActivity::class.java))
        }
    }
}