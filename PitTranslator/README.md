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
