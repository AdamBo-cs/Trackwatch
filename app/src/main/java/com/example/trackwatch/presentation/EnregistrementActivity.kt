package com.example.trackwatch.presentation

import android.content.Intent
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
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

class EnregistrementActivity : ComponentActivity(), SensorEventListener {

    private lateinit var sensorManager: SensorManager
    private var accelSensor: Sensor? = null
    private var gyroSensor: Sensor? = null
    private var heartSensor: Sensor? = null

    private lateinit var mode: String
    private lateinit var lettre: String
    private lateinit var nomFichier: String

    private var fileWriter: FileWriter? = null

    // N'oublie pas de remplacer par l'IP de ton PC Windows
    private val pcIpAddress = "192.168.1.X"
    private val port = 5000
    private var udpSocket = DatagramSocket()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        mode = intent.getStringExtra("MODE") ?: "LOCAL"
        lettre = intent.getStringExtra("LETTRE") ?: "A"

        val numero = CompteurPrefs.getProchainNumero(this, lettre)
        nomFichier = "${lettre}_$numero"

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = android.view.Gravity.CENTER
        }
        val tvInfo = TextView(this).apply {
            text = "En cours : $nomFichier\nMode : $mode"
            gravity = android.view.Gravity.CENTER
        }
        val btnStop = Button(this).apply { text = "⏹️ ARRÊTER" }

        layout.addView(tvInfo)
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
        val valeurs = event.values.joinToString(",")
        val ligneData = "$timestamp,$type,$valeurs"

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
        sensorManager.unregisterListener(this)
        try {
            fileWriter?.flush()
            fileWriter?.close()
        } catch (e: Exception) { e.printStackTrace() }

        CompteurPrefs.incrementerLettre(this, lettre)

        // Retourne proprement sur ton MainActivity
        val intent = Intent(this, MainActivity::class.java)
        intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP
        startActivity(intent)
        finish()
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}
}