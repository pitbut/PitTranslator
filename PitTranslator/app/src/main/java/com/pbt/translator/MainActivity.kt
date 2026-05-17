package com.pbt.translator

import android.Manifest
import android.content.*
import android.content.pm.PackageManager
import android.os.*
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.pbt.translator.databinding.ActivityMainBinding

class MainActivity : AppCompatActivity() {

    private lateinit var b: ActivityMainBinding
    private var running = false

    // (name, vosk/mlkit code)
    private val languages = listOf(
        "Русский"   to "ru",
        "English"   to "en",
        "Deutsch"   to "de",
        "Español"   to "es",
        "Français"  to "fr",
        "中文"       to "zh",
        "Türkçe"    to "tr"
    )

    private val receiver = object : BroadcastReceiver() {
        override fun onReceive(ctx: Context?, i: Intent?) {
            when (i?.action) {
                TranslatorService.ACTION_STATUS    ->
                    b.tvStatus.text = i.getStringExtra("status") ?: return
                TranslatorService.ACTION_ORIGINAL  ->
                    b.tvOriginal.text = i.getStringExtra("text") ?: return
                TranslatorService.ACTION_RESULT    ->
                    b.tvTranslated.text = i.getStringExtra("text") ?: return
                TranslatorService.ACTION_AMPLITUDE ->
                    b.waveformView.updateAmplitude(i.getFloatExtra("amplitude", 0f))
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        b = ActivityMainBinding.inflate(layoutInflater)
        setContentView(b.root)

        setupSpinners()

        b.btnSwap.setOnClickListener {
            val p1 = b.spinnerLang1.selectedItemPosition
            val p2 = b.spinnerLang2.selectedItemPosition
            b.spinnerLang1.setSelection(p2)
            b.spinnerLang2.setSelection(p1)
        }

        b.fabStart.setOnClickListener {
            if (!running) startTranslation() else stopTranslation()
        }

        checkPermissions()
    }

    override fun onResume() {
        super.onResume()
        val f = IntentFilter().apply {
            addAction(TranslatorService.ACTION_STATUS)
            addAction(TranslatorService.ACTION_ORIGINAL)
            addAction(TranslatorService.ACTION_RESULT)
            addAction(TranslatorService.ACTION_AMPLITUDE)
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            registerReceiver(receiver, f, RECEIVER_NOT_EXPORTED)
        } else {
            registerReceiver(receiver, f)
        }
    }

    override fun onPause() {
        super.onPause()
        try { unregisterReceiver(receiver) } catch (_: Exception) {}
    }

    // ── Language spinners ──────────────────────────────────────────
    private fun setupSpinners() {
        val names = languages.map { it.first }
        val makeAdapter = {
            ArrayAdapter(this, android.R.layout.simple_spinner_item, names).also {
                it.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
            }
        }
        b.spinnerLang1.adapter = makeAdapter()
        b.spinnerLang2.adapter = makeAdapter()
        b.spinnerLang1.setSelection(0) // Русский
        b.spinnerLang2.setSelection(1) // English
    }

    // ── Service control ────────────────────────────────────────────
    private fun startTranslation() {
        val src = languages[b.spinnerLang1.selectedItemPosition].second
        val dst = languages[b.spinnerLang2.selectedItemPosition].second

        val intent = Intent(this, TranslatorService::class.java).apply {
            putExtra("lang_src", src)
            putExtra("lang_dst", dst)
        }
        startForegroundService(intent)
        running = true
        b.fabStart.text = "■  СТОП"
        b.fabStart.backgroundTintList =
            ContextCompat.getColorStateList(this, R.color.red)
    }

    private fun stopTranslation() {
        stopService(Intent(this, TranslatorService::class.java))
        running = false
        b.fabStart.text = "▶  СТАРТ"
        b.fabStart.backgroundTintList =
            ContextCompat.getColorStateList(this, R.color.primary)
        b.tvStatus.text = "Остановлено"
        b.waveformView.updateAmplitude(0f)
    }

    // ── Permissions ────────────────────────────────────────────────
    private fun checkPermissions() {
        val needed = mutableListOf<String>()

        fun need(p: String) {
            if (ContextCompat.checkSelfPermission(this, p) != PackageManager.PERMISSION_GRANTED)
                needed.add(p)
        }

        need(Manifest.permission.RECORD_AUDIO)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S)
            need(Manifest.permission.BLUETOOTH_CONNECT)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU)
            need(Manifest.permission.POST_NOTIFICATIONS)

        if (needed.isNotEmpty())
            ActivityCompat.requestPermissions(this, needed.toTypedArray(), 100)
    }

    override fun onRequestPermissionsResult(
        code: Int, perms: Array<String>, results: IntArray
    ) {
        super.onRequestPermissionsResult(code, perms, results)
        if (results.any { it != PackageManager.PERMISSION_GRANTED }) {
            Toast.makeText(this, "Нужны разрешения для работы!", Toast.LENGTH_LONG).show()
        }
    }
}
