package com.example.trackwatch.presentation

import android.content.Intent
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.view.WindowManager
import android.os.Bundle
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import androidx.activity.ComponentActivity
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.io.File
import java.io.FileWriter
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress
import android.graphics.Color
import android.graphics.Typeface
import android.view.ViewGroup
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class EnregistrementActivity : ComponentActivity(), SensorEventListener {

    private lateinit var sensorManager: SensorManager
    private var accelSensor: Sensor? = null
    private var gyroSensor: Sensor? = null
    private var heartSensor: Sensor? = null

    private lateinit var mode: String
    private lateinit var exercice: String
    private lateinit var nomFichier: String

    private var fileWriter: FileWriter? = null

    // IP du PC pour le mode En Ligne (UDP)
    private val pcIpAddress = "192.168.1.56" //  REMPLACER PAR L'IP DU PC
    private val port = 5000
    private var udpSocket = DatagramSocket()

    // Variables pour l'affichage à l'écran
    private lateinit var tvAccel: TextView
    private lateinit var tvGyro: TextView
    private var derniereMiseAJourUI = 0L

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        mode = intent.getStringExtra("MODE") ?: "LOCAL"
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)

        // 1. On récupère le nom de l'exercice cliqué
        exercice = intent.getStringExtra("EXERCICE") ?: "Inconnu"

        // 2. On génère la date et l'heure
        val dateFormat = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault())
        val dateStr = dateFormat.format(Date())

        // 3. Le nom final
        nomFichier = "${exercice}_$dateStr".replace(" ", "_")

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
            setBackgroundColor(Color.parseColor("#121212"))
        }

        val tvInfo = TextView(this).apply {
            text = "ENREGISTREMENT\n$nomFichier"
            typeface = Typeface.create("sans-serif-medium", Typeface.NORMAL)
            setTextColor(Color.parseColor("#4CAF50"))
            textSize = 12f
            gravity = android.view.Gravity.CENTER
            layoutParams = LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 1.5f)
        }

        // Zone de texte pour les 3 axes de l'Accéléromètre
        tvAccel = TextView(this).apply {
            text = "ACC: En attente..."
            typeface = Typeface.create("monospace", Typeface.NORMAL)
            setTextColor(Color.parseColor("#64B5F6")) // Bleu clair
            textSize = 10f
            gravity = android.view.Gravity.CENTER
            layoutParams = LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f)
        }

        // Zone de texte pour les 3 axes du Gyroscope
        tvGyro = TextView(this).apply {
            text = "GYR: En attente..."
            typeface = Typeface.create("monospace", Typeface.NORMAL)
            setTextColor(Color.parseColor("#FFB74D")) // Orange clair
            textSize = 10f
            gravity = android.view.Gravity.CENTER
            layoutParams = LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f)
        }

        val btnStop = Button(this).apply {
            text = "ARRETER"
            typeface = Typeface.create("sans-serif-medium", Typeface.BOLD)
            setBackgroundColor(Color.parseColor("#D32F2F"))
            setTextColor(Color.WHITE)
            layoutParams = LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 1.5f)
        }

        layout.addView(tvInfo)
        layout.addView(tvAccel)
        layout.addView(tvGyro)
        layout.addView(btnStop)
        setContentView(layout)

        sensorManager = getSystemService(SENSOR_SERVICE) as SensorManager
        accelSensor = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
        gyroSensor = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE)
        heartSensor = sensorManager.getDefaultSensor(Sensor.TYPE_HEART_RATE)

        if (mode == "LOCAL") {
            val dossier = filesDir
            val fichier = File(dossier, "$nomFichier.csv")
            fileWriter = FileWriter(fichier, true)
            fileWriter?.write("Timestamp,SensorType,X,Y,Z\n")
        }

        sensorManager.registerListener(this, accelSensor, SensorManager.SENSOR_DELAY_GAME)
        sensorManager.registerListener(this, gyroSensor, SensorManager.SENSOR_DELAY_GAME)
        sensorManager.registerListener(this, heartSensor, SensorManager.SENSOR_DELAY_NORMAL)

        btnStop.setOnClickListener {
            ArreterEnregistrement()
        }
    }

    override fun onSensorChanged(event: SensorEvent?) {
        if (event == null) return

        val timestamp = System.currentTimeMillis()
        val type = event.sensor.type
        val valeurs = event.values

        if (timestamp - derniereMiseAJourUI > 300) {
            when (type) {
                Sensor.TYPE_ACCELEROMETER -> {
                    tvAccel.text = "ACC X:${"%.2f".format(valeurs[0])}\nY:${"%.2f".format(valeurs[1])}\nZ:${"%.2f".format(valeurs[2])}"
                    derniereMiseAJourUI = timestamp
                }
                Sensor.TYPE_GYROSCOPE -> {
                    tvGyro.text = "GYR X:${"%.2f".format(valeurs[0])}\nY:${"%.2f".format(valeurs[1])}\nZ:${"%.2f".format(valeurs[2])}"
                    derniereMiseAJourUI = timestamp
                }
            }
        }

        val ligneData = "$timestamp,$type,${valeurs.joinToString(",")}"

        if (mode == "LOCAL") {
            CoroutineScope(Dispatchers.IO).launch {
                try {
                    fileWriter?.write("$ligneData\n")
                } catch (e: Exception) { e.printStackTrace() }
            }
        } else {
            CoroutineScope(Dispatchers.IO).launch {
                try {
                    val ip = InetAddress.getByName(pcIpAddress)
                    val paquet = DatagramPacket(ligneData.toByteArray(), ligneData.length, ip, port)
                    udpSocket.send(paquet)
                } catch (e: Exception) { e.printStackTrace() }
            }
        }
    }

    private fun ArreterEnregistrement() {
        window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        sensorManager.unregisterListener(this)
        try {
            fileWriter?.flush()
            fileWriter?.close()
        } catch (e: Exception) { e.printStackTrace() }


        val intent = Intent(this, MainActivity::class.java)
        intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP
        startActivity(intent)
        finish()
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}
}