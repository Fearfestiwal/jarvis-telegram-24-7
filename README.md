# 7/24 Kisisel Turkce Jarvis Telegram Botu

PC kapaliyken bile telefondan **yazili ve sesli** olarak Jarvis ile konusabilmeniz icin hazirlanmis, bulut uyumlu (Railway / Docker) Telegram botu.

## Ozellikler
- **7/24 Calisma:** `Dockerfile` ve `railway.toml` ile Railway veya herhangi bir Docker sunucusunda PC kapaliyken bile kesintisiz calisir.
- **Sesli Mesaj Destegi:** Telegram'dan gonderdiginiz sesli mesajlari dogrudan dinleyip Turkce yanitlar.
- **Canli Web Aramasi:** Google Search araci ile guncel bilgilere erisir.
- **Guvenlik Kilidi:** Yalnizca `ALLOWED_TELEGRAM_USER_IDS` icindeki kullanicilara yanit verir.

## Kurulum (3 Adim)
1. Telegram'da `@BotFather` ile `/newbot` komutuyla **Bot Token** alin.
2. `@userinfobot` uzerinden kendi **Telegram User ID** numaranizi ogrenin.
3. [Google AI Studio](https://aistudio.google.com/) uzerinden bir **Gemini API Key** alin.

### Yerelde Test Etme
`.env.example` dosyasini `.env` olarak kopyalayip degerleri doldurun, ardindan:
```powershell
uv run python -m jarvis_bot.main
```

### 7/24 Buluta (Railway) Yukleme
Projeyi GitHub'a yukleyip Railway uzerinden deploy edin ve `TELEGRAM_BOT_TOKEN`, `GEMINI_API_KEY`, `ALLOWED_TELEGRAM_USER_IDS` ortam degiskenlerini tanimlayin.
