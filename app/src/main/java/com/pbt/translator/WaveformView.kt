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
