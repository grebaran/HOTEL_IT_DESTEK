import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler
from database import db_manager
from bot import handlers

# .env dosyasından güvenlik anahtarını yükle
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")


def main():
    print("🏨 Hotel IT Support Sistemi Başlatılıyor...")

    # 1. Veritabanını hazırla (İlk çalışmada otomatik dosya oluşturur)
    db_manager.init_db()
    print("✅ Veritabanı bağlantısı başarılı.")

    if not TOKEN:
        print("❌ HATA: .env dosyasında TELEGRAM_TOKEN bulunamadı!")
        return

    # 2. Telegram Botunu kur
    app = Application.builder().token(TOKEN).build()

    # 3. Komutları tanıt
    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(CommandHandler("ariza", handlers.ariza))
    app.add_handler(CommandHandler("bekleyenler", handlers.bekleyenler))
    app.add_handler(CommandHandler("cozuldu", handlers.cozuldu))
    app.add_handler(CommandHandler("rapor", handlers.rapor))

    print("🚀 Bot yayında! Telegram'a gidip /start yazabilirsiniz. (Durdurmak için CTRL+C)")
    app.run_polling()


if __name__ == '__main__':
    main()