package com.example.trackwatch.presentation

import android.content.Context

object CompteurPrefs {
    private const val PREFS_NAME = "TrackWatchPrefs"

    fun getProchainNumero(context: Context, lettre: String): Int {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        val dernierNumero = prefs.getInt(lettre, 0)
        return dernierNumero + 1
    }

    fun incrementerLettre(context: Context, lettre: String) {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        val actuel = prefs.getInt(lettre, 0)
        prefs.edit().putInt(lettre, actuel + 1).apply()
    }
}