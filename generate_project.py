#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PitTranslator — генератор Android-проекта
Автор: Бутовский П.М. (Pit)

Запуск:
    python3 generate_project.py

Затем:
    cd PitTranslator
    git init && git add . && git commit -m "Initial commit"
    git remote add origin https://github.com/YOUR_USER/PitTranslator.git
    git push -u origin main
    # GitHub Actions соберёт APK автоматически
"""
import os

BASE = "PitTranslator"

def w(path, content):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content.lstrip("\n"))
    print(f"  ✓ {path}")

print("\n=== PitTranslator — генерация проекта ===\n")

# ─────────────────────────────────────────────────────────────
# GRADLE BUILD FILES
# ─────────────────────────────────────────────────────────────
w("settings.gradle", """
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "PitTranslator"
include ':app'
""")

w("build.gradle", """
plugins {
    id 'com.android.application' version '8.2.0' apply false
    id 'org.jetbrains.kotlin.android' version '1.9.22' apply false
}
""")

w("gradle.properties", """
android.useAndroidX=true
android.enableJetifier=true
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
kotlin.code.style=official
""")

w("gradle/wrapper/gradle-wrapper.properties", """
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-8.6-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
""")

w("app/build.gradle", """
plugins {
    id 'com.android.application'
    id 'org.jetbrains.kotlin.android'
}

android {
    namespace 'com.pbt.translator'
    compileSdk 34

    defaultConfig {
        applicationId "com.pbt.translator"
        minSdk 26
        targetSdk 34
        versionCode 1
        versionName "1.0"
    }

    buildFeatures { viewBinding true }

    buildTypes {
        release { minifyEnabled false }
        debug   { debuggable true }
    }

    compileOptions {
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = '17' }

    packagingOptions {
        jniLibs { useLegacyPackaging = true }
        resources {
            excludes += ['META-INF/INDEX.LIST',
                         'META-INF/io.netty.versions.properties']
        }
    }
}

dependencies {
    implementation 'androidx.core:core-ktx:1.12.0'
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.11.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
    implementation 'androidx.lifecycle:lifecycle-service:2.7.0'
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3'

    // Vosk offline STT
    implementation 'com.alphacephei:vosk-android:0.3.47'

    // ML Kit Translation (скачивает языковые модели по WiFi)
    implementation 'com.google.mlkit:translate:17.0.2'

    // OkHttp для загрузки Vosk-моделей
    implementation 'com.squareup.okhttp3:okhttp:4.12.0'
}
""")

# ─────────────────────────────────────────────────────────────
# ANDROID MANIFEST
# ─────────────────────────────────────────────────────────────
w("app/src/main/AndroidManifest.xml", """
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.RECORD_AUDIO" />
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.BLUETOOTH" />
    <uses-permission android:name="android.permission.BLUETOOTH_CONNECT" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MICROPHONE" />
    <uses-permission android:name="android.permission.WAKE_LOCK" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:label="PitTranslator"
        android:theme="@style/Theme.PitTranslator"
        android:supportsRtl="true">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:screenOrientation="portrait"
            android:windowSoftInputMode="adjustPan">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <service
            android:name=".TranslatorService"
            android:foregroundServiceType="microphone"
            android:exported="false" />

    </application>
</manifest>
""")

# ─────────────────────────────────────────────────────────────
# RESOURCE: colors
# ─────────────────────────────────────────────────────────────
w("app/src/main/res/values/colors.xml", """
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="bg_dark">#0D1117</color>
    <color name="card_dark">#161B22</color>
    <color name="card_mid">#21262D</color>
    <color name="primary">#2F81F7</color>
    <color name="primary_dark">#1F6FEB</color>
    <color name="green">#3FB950</color>
    <color name="red">#F85149</color>
    <color name="amber">#D29922</color>
    <color name="text_primary">#E6EDF3</color>
    <color name="text_secondary">#8B949E</color>
    <color name="divider">#30363D</color>
    <color name="ic_launcher_background">#2F81F7</color>
</resources>
""")

w("app/src/main/res/values/strings.xml", """
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">PitTranslator</string>
    <string name="btn_start">СТАРТ</string>
    <string name="btn_stop">СТОП</string>
    <string name="ready">Готов</string>
    <string name="loading_model">Загрузка модели…</string>
    <string name="listening">Слушаю…</string>
    <string name="translating">Перевожу…</string>
    <string name="speaking">Воспроизвожу…</string>
</resources>
""")

w("app/src/main/res/values/themes.xml", """
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="Theme.PitTranslator"
           parent="Theme.MaterialComponents.DayNight.NoActionBar">
        <item name="colorPrimary">@color/primary</item>
        <item name="colorPrimaryDark">@color/primary_dark</item>
        <item name="colorAccent">@color/green</item>
        <item name="android:windowBackground">@color/bg_dark</item>
        <item name="android:statusBarColor">@color/bg_dark</item>
        <item name="android:navigationBarColor">@color/bg_dark</item>
    </style>

    <style name="CardLabel" parent="Widget.MaterialComponents.TextView">
        <item name="android:textColor">@color/text_secondary</item>
        <item name="android:textSize">10sp</item>
        <item name="android:letterSpacing">0.08</item>
        <item name="android:textAllCaps">true</item>
    </style>
</resources>
""")

# ─────────────────────────────────────────────────────────────
# RESOURCE: drawables
# ─────────────────────────────────────────────────────────────
w("app/src/main/res/drawable/status_badge_bg.xml", """
<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#1A3FB950" />
    <stroke android:width="1dp" android:color="#3FB950" />
    <corners android:radius="12dp" />
</shape>
""")

w("app/src/main/res/drawable/ic_launcher_fg.xml", """
<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <!-- headphones arc -->
    <path
        android:fillColor="@android:color/transparent"
        android:strokeColor="#FFFFFF"
        android:strokeWidth="6"
        android:strokeLineCap="round"
        android:pathData="M28,58 C28,38 37.9,22 54,22 C70.1,22 80,38 80,58"/>
    <!-- left cup -->
    <rect android:fillColor="#FFFFFF" android:x="18" android:y="54"
        android:width="14" android:height="22" android:rx="7"/>
    <!-- right cup -->
    <rect android:fillColor="#FFFFFF" android:x="76" android:y="54"
        android:width="14" android:height="22" android:rx="7"/>
    <!-- translate arrow -->
    <path android:fillColor="#FFFFFF"
        android:pathData="M40,86 L68,86 M61,80 L68,86 L61,92"/>
</vector>
""")

w("app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml", """
<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/ic_launcher_background"/>
    <foreground android:drawable="@drawable/ic_launcher_fg"/>
</adaptive-icon>
""")

w("app/src/main/res/mipmap-anydpi-v26/ic_launcher_round.xml", """
<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/ic_launcher_background"/>
    <foreground android:drawable="@drawable/ic_launcher_fg"/>
</adaptive-icon>
""")

# ─────────────────────────────────────────────────────────────
# RESOURCE: layout
# ─────────────────────────────────────────────────────────────
w("app/src/main/res/layout/activity_main.xml", """
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:orientation="vertical"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@color/bg_dark"
    android:padding="16dp">

    <!-- ── Title bar ── -->
    <LinearLayout
        android:orientation="horizontal"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:gravity="center_vertical"
        android:layout_marginBottom="16dp">

        <TextView
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:text="🎧 PitTranslator"
            android:textColor="@color/text_primary"
            android:textSize="20sp"
            android:textStyle="bold"
            android:fontFamily="monospace"/>

        <TextView
            android:id="@+id/tvStatus"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="Готов"
            android:textColor="@color/green"
            android:textSize="12sp"
            android:background="@drawable/status_badge_bg"
            android:paddingStart="10dp"
            android:paddingEnd="10dp"
            android:paddingTop="5dp"
            android:paddingBottom="5dp"/>
    </LinearLayout>

    <!-- ── Language selectors ── -->
    <LinearLayout
        android:orientation="horizontal"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:gravity="center_vertical"
        android:layout_marginBottom="12dp">

        <!-- Lang 1: source (he speaks) -->
        <com.google.android.material.card.MaterialCardView
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            app:cardBackgroundColor="@color/card_dark"
            app:cardCornerRadius="12dp"
            app:cardElevation="0dp"
            app:strokeColor="@color/divider"
            app:strokeWidth="1dp">
            <LinearLayout
                android:orientation="vertical"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:padding="10dp">
                <TextView
                    style="@style/CardLabel"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="он говорит"/>
                <Spinner
                    android:id="@+id/spinnerLang1"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:textColor="@color/text_primary"
                    android:backgroundTint="@color/primary"
                    android:layout_marginTop="4dp"/>
            </LinearLayout>
        </com.google.android.material.card.MaterialCardView>

        <!-- Swap button -->
        <TextView
            android:id="@+id/btnSwap"
            android:layout_width="40dp"
            android:layout_height="40dp"
            android:gravity="center"
            android:text="⇄"
            android:textColor="@color/primary"
            android:textSize="20sp"
            android:background="?attr/selectableItemBackgroundBorderless"
            android:layout_marginStart="8dp"
            android:layout_marginEnd="8dp"/>

        <!-- Lang 2: target (TTS output) -->
        <com.google.android.material.card.MaterialCardView
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            app:cardBackgroundColor="@color/card_dark"
            app:cardCornerRadius="12dp"
            app:cardElevation="0dp"
            app:strokeColor="@color/divider"
            app:strokeWidth="1dp">
            <LinearLayout
                android:orientation="vertical"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:padding="10dp">
                <TextView
                    style="@style/CardLabel"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="вывод в BT"/>
                <Spinner
                    android:id="@+id/spinnerLang2"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:textColor="@color/text_primary"
                    android:backgroundTint="@color/primary"
                    android:layout_marginTop="4dp"/>
            </LinearLayout>
        </com.google.android.material.card.MaterialCardView>
    </LinearLayout>

    <!-- ── Waveform ── -->
    <com.pbt.translator.WaveformView
        android:id="@+id/waveformView"
        android:layout_width="match_parent"
        android:layout_height="64dp"
        android:layout_marginBottom="12dp"/>

    <!-- ── Original text ── -->
    <com.google.android.material.card.MaterialCardView
        android:id="@+id/cardOriginal"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1"
        android:layout_marginBottom="8dp"
        app:cardBackgroundColor="@color/card_dark"
        app:cardCornerRadius="12dp"
        app:cardElevation="0dp"
        app:strokeColor="@color/divider"
        app:strokeWidth="1dp">
        <LinearLayout
            android:orientation="vertical"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:padding="12dp">
            <TextView
                style="@style/CardLabel"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="оригинал"/>
            <TextView
                android:id="@+id/tvOriginal"
                android:layout_width="match_parent"
                android:layout_height="0dp"
                android:layout_weight="1"
                android:layout_marginTop="6dp"
                android:text="Жду речи…"
                android:textColor="@color/text_primary"
                android:textSize="16sp"
                android:gravity="start|top"
                android:lineSpacingExtra="4dp"/>
        </LinearLayout>
    </com.google.android.material.card.MaterialCardView>

    <!-- ── Translated text ── -->
    <com.google.android.material.card.MaterialCardView
        android:id="@+id/cardTranslated"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1"
        android:layout_marginBottom="16dp"
        app:cardBackgroundColor="@color/card_dark"
        app:cardCornerRadius="12dp"
        app:cardElevation="0dp"
        app:strokeColor="@color/primary"
        app:strokeWidth="1dp">
        <LinearLayout
            android:orientation="vertical"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:padding="12dp">
            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="ПЕРЕВОД 🔊"
                android:textColor="@color/primary"
                android:textSize="10sp"
                android:letterSpacing="0.08"
                android:textAllCaps="true"/>
            <TextView
                android:id="@+id/tvTranslated"
                android:layout_width="match_parent"
                android:layout_height="0dp"
                android:layout_weight="1"
                android:layout_marginTop="6dp"
                android:text="Перевод появится здесь…"
                android:textColor="@color/text_primary"
                android:textSize="16sp"
                android:gravity="start|top"
                android:lineSpacingExtra="4dp"/>
        </LinearLayout>
    </com.google.android.material.card.MaterialCardView>

    <!-- ── Start / Stop FAB ── -->
    <com.google.android.material.floatingactionbutton.ExtendedFloatingActionButton
        android:id="@+id/fabStart"
        android:layout_width="match_parent"
        android:layout_height="56dp"
        android:text="▶  СТАРТ"
        android:textColor="@android:color/white"
        android:textSize="16sp"
        android:textStyle="bold"
        app:backgroundTint="@color/primary"/>

</LinearLayout>
""")

# ─────────────────────────────────────────────────────────────
# KOTLIN: WaveformView
# ─────────────────────────────────────────────────────────────
PKG = "app/src/main/java/com/pbt/translator"

w(f"{PKG}/WaveformView.kt", """
package com.pbt.translator

import android.content.Context
import android.graphics.*
import android.util.AttributeSet
import android.view.View
import kotlin.math.abs
import kotlin.math.sin

class WaveformView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : View(context, attrs) {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
    }

    private val barCount = 32
    private var amps = FloatArray(barCount) { 0.05f }
    private var phase = 0f
    private var active = false

    fun updateAmplitude(level: Float) {
        active = level > 0.02f
        phase += if (active) 0.18f else 0.06f
        amps = FloatArray(barCount) { i ->
            if (active) {
                val wave = abs(sin((i.toFloat() / barCount * Math.PI * 2 + phase).toFloat()))
                (wave * 0.55f + Math.random().toFloat() * 0.45f) * level.coerceIn(0f, 1f)
            } else {
                (abs(sin((i.toFloat() / barCount * Math.PI + phase).toFloat())) * 0.06f + 0.04f)
            }
        }
        invalidate()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val w = width.toFloat()
        val h = height.toFloat()
        val barW = w / (barCount * 1.6f)
        val gap   = w / (barCount * 1.6f) * 0.6f
        val cy    = h / 2f

        for (i in 0 until barCount) {
            val amp   = amps[i].coerceIn(0.02f, 1f)
            val barH  = (amp * h * 0.95f).coerceAtLeast(3f)
            val x     = i * (barW + gap) + gap / 2f
            val alpha = if (active) 220 else 70

            paint.color = Color.argb(alpha, 0x2F, 0x81, 0xF7)
            canvas.drawRoundRect(
                x, cy - barH / 2f,
                x + barW, cy + barH / 2f,
                barW / 2f, barW / 2f, paint
            )
        }
    }
}
""")

# ─────────────────────────────────────────────────────────────
# KOTLIN: ModelDownloader
# ─────────────────────────────────────────────────────────────
w(f"{PKG}/ModelDownloader.kt", """
package com.pbt.translator

import android.content.Context
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import java.io.File
import java.io.IOException
import java.util.concurrent.TimeUnit
import java.util.zip.ZipInputStream

object ModelDownloader {

    // Vosk small models (~40-50 MB each)
    private val MODELS = mapOf(
        "ru" to ("vosk-model-small-ru-0.22"      to "https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip"),
        "en" to ("vosk-model-small-en-us-0.15"   to "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"),
        "de" to ("vosk-model-small-de-0.15"       to "https://alphacephei.com/vosk/models/vosk-model-small-de-0.15.zip"),
        "es" to ("vosk-model-small-es-0.42"       to "https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip"),
        "fr" to ("vosk-model-small-fr-pguyot-0.3" to "https://alphacephei.com/vosk/models/vosk-model-small-fr-pguyot-0.3.zip"),
        "zh" to ("vosk-model-small-cn-0.22"       to "https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip"),
        "tr" to ("vosk-model-small-tr-0.3"        to "https://alphacephei.com/vosk/models/vosk-model-small-tr-0.3.zip")
    )

    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(180, TimeUnit.SECONDS)
        .build()

    /** Returns the local path to the ready model (downloads if needed). */
    suspend fun getModelPath(
        context: Context,
        langCode: String,
        onStatus: (String) -> Unit
    ): String = withContext(Dispatchers.IO) {
        val (modelName, url) = MODELS[langCode] ?: MODELS["en"]!!
        val modelsRoot = File(context.filesDir, "vosk")
        val modelDir   = File(modelsRoot, modelName)

        if (isReady(modelDir)) return@withContext modelDir.absolutePath

        onStatus("Загрузка Vosk ($langCode) ≈45 МБ…")
        download(context, modelName, url, modelsRoot, onStatus)
        modelDir.absolutePath
    }

    private fun isReady(dir: File) = dir.exists() && File(dir, "conf").exists()

    private fun download(
        context: Context,
        modelName: String,
        url: String,
        modelsRoot: File,
        onStatus: (String) -> Unit
    ) {
        val request  = Request.Builder().url(url).build()
        val response = client.newCall(request).execute()
        if (!response.isSuccessful) throw IOException("HTTP ${response.code}")

        val body   = response.body ?: throw IOException("Empty body")
        val total  = body.contentLength()
        val zipTmp = File(context.cacheDir, "$modelName.zip")

        var downloaded = 0L
        body.byteStream().use { input ->
            zipTmp.outputStream().use { out ->
                val buf = ByteArray(8192)
                var n: Int
                while (input.read(buf).also { n = it } != -1) {
                    out.write(buf, 0, n)
                    downloaded += n
                    if (total > 0) {
                        val pct = (downloaded * 100 / total).toInt()
                        if (pct % 5 == 0) onStatus("Загрузка $pct%…")
                    }
                }
            }
        }

        onStatus("Распаковка…")
        modelsRoot.mkdirs()

        ZipInputStream(zipTmp.inputStream()).use { zip ->
            var entry = zip.nextEntry
            while (entry != null) {
                val dest = File(modelsRoot, entry.name)
                if (entry.isDirectory) dest.mkdirs()
                else {
                    dest.parentFile?.mkdirs()
                    dest.outputStream().use { out -> zip.copyTo(out) }
                }
                zip.closeEntry()
                entry = zip.nextEntry
            }
        }
        zipTmp.delete()
    }
}
""")

# ─────────────────────────────────────────────────────────────
# KOTLIN: TranslatorService (Foreground Service)
# ─────────────────────────────────────────────────────────────
w(f"{PKG}/TranslatorService.kt", """
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
        val start = json.indexOf('"', json.indexOf("\"text\"") + 7)
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
""")

# ─────────────────────────────────────────────────────────────
# KOTLIN: MainActivity
# ─────────────────────────────────────────────────────────────
w(f"{PKG}/MainActivity.kt", """
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
""")

# ─────────────────────────────────────────────────────────────
# GITHUB ACTIONS WORKFLOW
# ─────────────────────────────────────────────────────────────
w(".github/workflows/build.yml", """
name: Build APK

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build:
    name: Build Debug APK
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: gradle

      - name: Setup Android SDK
        uses: android-actions/setup-android@v3

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v4
        with:
          gradle-version: '8.6'

      - name: Build Debug APK
        run: gradle assembleDebug --no-daemon --stacktrace

      - name: Upload APK artifact
        uses: actions/upload-artifact@v4
        with:
          name: PitTranslator-debug-${{ github.run_number }}
          path: app/build/outputs/apk/debug/app-debug.apk
          retention-days: 30

      - name: Show APK info
        run: |
          echo "=== APK built successfully ==="
          ls -lh app/build/outputs/apk/debug/
""")

# ─────────────────────────────────────────────────────────────
# .gitignore
# ─────────────────────────────────────────────────────────────
w(".gitignore", """
*.iml
.gradle
/local.properties
/.idea/
.DS_Store
/build
/captures
.externalNativeBuild
.cxx
local.properties
""")

# ─────────────────────────────────────────────────────────────
# README
# ─────────────────────────────────────────────────────────────
w("README.md", """
# 🎧 PitTranslator

Переводчик-синхронист для Android. Слушает речь через дальний микрофон,
переводит офлайн и озвучивает в Bluetooth-наушниках (A2DP, микрофон BT не активируется).

## Стек
| Компонент | Технология |
|-----------|-----------|
| STT | Vosk (офлайн, загрузка ~45 МБ при первом запуске) |
| Перевод | ML Kit Translation (офлайн после загрузки) |
| TTS | Android TextToSpeech → A2DP Bluetooth |
| Фон | Android Foreground Service + WakeLock |
| Микрофон | AudioRecord VOICE_RECOGNITION + MIC_DIRECTION_AWAY_FROM_USER |

## Сборка без Android Studio
1. Push в GitHub
2. Actions → Build APK → скачать артефакт `PitTranslator-debug-N`

## Поддерживаемые языки
Русский, English, Deutsch, Español, Français, 中文, Türkçe

## Разрешения
- RECORD_AUDIO — микрофон
- INTERNET — загрузка Vosk/ML Kit моделей
- BLUETOOTH_CONNECT — вывод в наушники
- FOREGROUND_SERVICE_MICROPHONE — работа в фоне
- WAKE_LOCK — экран выключен, работает
""")

print("\n✅ Проект создан в папке PitTranslator/")
print("\nСледующие шаги:")
print("  cd PitTranslator")
print("  git init")
print("  git add .")
print('  git commit -m "PitTranslator initial commit"')
print("  git remote add origin https://github.com/ВАШ_ЛОГИН/PitTranslator.git")
print("  git push -u origin main")
print("\nGitHub Actions автоматически соберёт APK.")
print("Скачай его: Actions → Build APK → Artifacts → PitTranslator-debug-N\n")
