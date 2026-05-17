package com.pbt.translator

import android.app.*
import android.content.*
import android.media.*
import android.os.*
import android.speech.tts.TextToSpeech
import androidx.core.app.NotificationCompat
import com.google.mlkit.nl.translate.*
import kotlinx.coroutines.*
import org.vosk.Model
import org.vosk.Recognizer
import java.util.Locale
import kotlin.math.sqrt

class TranslatorService : Service() {

    companion object {
        const val CHANNEL_ID   = "pit_translator"
        const val NOTIF_ID     = 42
        const val SAMPLE_RATE  = 16000
        const val BUF_SAMPLES  = 4096
        const val AMPLIFY      = 3.0f

        const val ACTION_STATUS    = "pit.STATUS"
        const val ACTION_ORIGINAL  = "pit.ORIGINAL"
        const val ACTION_RESULT    = "pit.RESULT"
        const val ACTION_AMPLITUDE = "pit.AMPLITUDE"
        const val ACTION_STOP      = "pit.STOP"
    }

    private var srcLang = "ru"
    private var dstLang = "en"

    private var voskModel:  Model?           = null
    private var recognizer: Recognizer?      = null
    private var audioRec:   AudioRecord?     = null
    private var tts:        TextToSpeech?    = null
    private var translator: com.google.mlkit.nl.translate.Translator? = null

    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private var listening = false
    private var wakeLock: PowerManager.WakeLock? = null

    // ── Lifecycle ──────────────────────────────────────────────────
    override fun onBind(i: Intent?) = null

    override fun onCreate() {
        super.onCreate()
        createChannel()
        acquireWakeLock()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent?.action == ACTION_STOP) { stopSelf(); return START_NOT_STICKY }

        srcLang = intent?.getStringExtra("lang_src") ?: "ru"
        dstLang = intent?.getStringExtra("lang_dst") ?: "en"

        startForeground(NOTIF_ID, buildNotif("Инициализация…"))
        broadcast(ACTION_STATUS, "status", "⏳ Загрузка…")

        scope.launch {
            try {
                initTTS()
                val path = ModelDownloader.getModelPath(
                    this@TranslatorService, srcLang
                ) { msg -> broadcast(ACTION_STATUS, "status", msg) }
                voskModel  = Model(path)
                recognizer = Recognizer(voskModel, SAMPLE_RATE.toFloat())
                initTranslator()
                startListening()
            } catch (e: Exception) {
                broadcast(ACTION_STATUS, "status", "❌ ${e.message}")
            }
        }
        return START_STICKY
    }

    override fun onDestroy() {
        listening = false
        audioRec?.stop(); audioRec?.release()
        recognizer?.close(); voskModel?.close()
        tts?.stop(); tts?.shutdown()
        translator?.close()
        scope.cancel()
        wakeLock?.release()
        super.onDestroy()
    }

    // ── Init helpers ───────────────────────────────────────────────
    private fun initTTS() {
        tts = TextToSpeech(this) { status ->
            if (status == TextToSpeech.SUCCESS) {
                tts?.language = Locale.forLanguageTag(dstLang)
                // Route to Bluetooth A2DP — NOT SCO → BT mic stays silent
                tts?.setAudioAttributes(
                    AudioAttributes.Builder()
                        .setUsage(AudioAttributes.USAGE_MEDIA)
                        .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                        .build()
                )
            }
        }
    }

    private fun initTranslator() {
        val src = TranslateLanguage.fromLanguageTag(srcLang) ?: TranslateLanguage.RUSSIAN
        val dst = TranslateLanguage.fromLanguageTag(dstLang) ?: TranslateLanguage.ENGLISH
        val opts = TranslatorOptions.Builder()
            .setSourceLanguage(src)
            .setTargetLanguage(dst)
            .build()
        translator = Translation.getClient(opts)
        // Download translation model (any network, no WiFi restriction)
        translator?.downloadModelIfNeeded(DownloadConditions.Builder().build())
    }

    // ── Audio loop ─────────────────────────────────────────────────
    private fun startListening() {
        val minBuf = AudioRecord.getMinBufferSize(
            SAMPLE_RATE, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT
        ).coerceAtLeast(BUF_SAMPLES * 2)

        audioRec = AudioRecord(
            MediaRecorder.AudioSource.VOICE_RECOGNITION,
            SAMPLE_RATE,
            AudioFormat.CHANNEL_IN_MONO,
            AudioFormat.ENCODING_PCM_16BIT,
            minBuf
        )

        // Prefer far-field (away from user) microphone — API 28+
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            audioRec?.setPreferredMicrophoneDirection(
                MicrophoneDirection.MIC_DIRECTION_AWAY_FROM_USER
            )
        }

        audioRec?.startRecording()
        listening = true
        broadcast(ACTION_STATUS, "status", "🎤 Слушаю…")
        updateNotif("🎤 Слушаю…")

        scope.launch(Dispatchers.IO) {
            val rec = recognizer ?: return@launch
            val buf = ShortArray(BUF_SAMPLES)

            while (listening) {
                val n = audioRec?.read(buf, 0, buf.size) ?: break
                if (n <= 0) continue

                // Amplify
                val amp = ShortArray(n) { i ->
                    (buf[i] * AMPLIFY).toInt()
                        .coerceIn(Short.MIN_VALUE.toInt(), Short.MAX_VALUE.toInt()).toShort()
                }

                // RMS → waveform
                val rms = sqrt(amp.take(n).fold(0.0) { a, s -> a + s.toDouble() * s }.toDouble() / n).toFloat()
                sendAmp((rms / 32768f).coerceIn(0f, 1f))

                // Bytes for Vosk
                val bytes = ByteArray(n * 2).also { b ->
                    for (i in 0 until n) {
                        b[i * 2]     = (amp[i].toInt() and 0xFF).toByte()
                        b[i * 2 + 1] = (amp[i].toInt() shr 8 and 0xFF).toByte()
                    }
                }

                if (rec.acceptWaveForm(bytes, bytes.size)) {
                    val text = extractText(rec.result)
                    if (text.isNotBlank()) {
                        withContext(Dispatchers.Main) { handleRecognized(text) }
                    }
                }
            }
        }
    }

    // ── Text handling ──────────────────────────────────────────────
    private fun handleRecognized(text: String) {
        broadcast(ACTION_ORIGINAL, "text", text)
        broadcast(ACTION_STATUS, "status", "⚡ Перевожу…")

        translator?.translate(text)
            ?.addOnSuccessListener { translated ->
                broadcast(ACTION_RESULT, "text", translated)
                broadcast(ACTION_STATUS, "status", "🔊 Говорю…")
                updateNotif("🔊 $translated")
                tts?.speak(translated, TextToSpeech.QUEUE_FLUSH, null,
                    "utt_${System.currentTimeMillis()}")
                scope.launch {
                    delay(600)
                    withContext(Dispatchers.Main) {
                        broadcast(ACTION_STATUS, "status", "🎤 Слушаю…")
                        updateNotif("🎤 Слушаю…")
                    }
                }
            }
            ?.addOnFailureListener { e ->
                broadcast(ACTION_STATUS, "status", "⚠ ${e.message}")
            }
    }

    private fun extractText(json: String): String {
        val start = json.indexOf('"', json.indexOf(""text"") + 7)
        if (start < 0) return ""
        val end = json.indexOf('"', start + 1)
        if (end < 0) return ""
        return json.substring(start + 1, end).trim()
    }

    // ── Notification ───────────────────────────────────────────────
    private fun createChannel() {
        val ch = NotificationChannel(CHANNEL_ID, "PitTranslator",
            NotificationManager.IMPORTANCE_LOW).apply {
            description = "Фоновый переводчик"
        }
        getSystemService(NotificationManager::class.java).createNotificationChannel(ch)
    }

    private fun buildNotif(text: String): Notification {
        val stopPi = PendingIntent.getService(
            this, 0,
            Intent(this, TranslatorService::class.java).apply { action = ACTION_STOP },
            PendingIntent.FLAG_IMMUTABLE
        )
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("🎧 PitTranslator")
            .setContentText(text)
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .addAction(android.R.drawable.ic_media_pause, "Стоп", stopPi)
            .setOngoing(true)
            .build()
    }

    private fun updateNotif(text: String) =
        getSystemService(NotificationManager::class.java).notify(NOTIF_ID, buildNotif(text))

    // ── Helpers ────────────────────────────────────────────────────
    private fun broadcast(action: String, key: String, value: String) =
        sendBroadcast(Intent(action).apply { putExtra(key, value); setPackage(packageName) })

    private fun sendAmp(v: Float) =
        sendBroadcast(Intent(ACTION_AMPLITUDE).apply {
            putExtra("amplitude", v); setPackage(packageName) })

    private fun acquireWakeLock() {
        val pm = getSystemService(PowerManager::class.java)
        wakeLock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "PitTranslator::mic")
        wakeLock?.acquire(4 * 60 * 60 * 1000L) // 4 hours max
    }
}
