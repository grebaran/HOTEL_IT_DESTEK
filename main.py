import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler
from database import db_manager
from bot import handlers

# Token'ı koda kabak gibi yazmamak için .env dosyasından gizlice çekiyoruz. 
# Otel verisi sonuçta, güvenlik ilk iş.
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

def main():
    print("🏨 Hotel IT Support Sistemi Başlatılıyor...")

    # Veritabanı yoksa ilk açılışta kendi kendine kursun. 
    # Kurulumda amelelik yapmayalım, tak-çalıştır olsun.
    db_manager.init_db()
    print("✅ Veritabanı bağlantısı başarılı. DB hazır.")

    # Eğer .env dosyasını unuttuysak sistemi hiç yorma, fişi çek.
    if not TOKEN:
        print("❌ HATA: Usta .env dosyasına TELEGRAM_TOKEN girmeyi unutmuşsun!")
        return

    # Botun iskeletini ayağa kaldırıyoruz
    app = Application.builder().token(TOKEN).build()

    # Botun anlayacağı komutları (slash komutları) rotalıyoruz. 
    # Hangi komut geldiğinde hangi fonksiyon çalışacak...
    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(CommandHandler("ariza", handlers.ariza))          # Housekeeping ve personelin kullanacağı
    app.add_handler(CommandHandler("bekleyenler", handlers.bekleyenler)) # Bizim IT tayfanın bakacağı liste
    app.add_handler(CommandHandler("cozuldu", handlers.cozuldu))      # İşi bitirince atacağımız komut
    app.add_handler(CommandHandler("rapor", handlers.rapor))          # Müdürün şov yapacağı kısım :)

    # Her şey tamamsa botu 7/24 dinlemeye al.
    print("🚀 Bot yayında! Telegram'a gidip /start yazabilirsiniz. (Durdurmak için CTRL+C)")
    app.run_polling()

if __name__ == '__main__':
    # Ana motoru bismillah deyip ateşliyoruz
    main()
