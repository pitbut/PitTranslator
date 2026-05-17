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
