from telegram import Update
from telegram.ext import ContextTypes
import sys
import os

# Python bazen alt klasörleri görmekte nazlanıyor. 
# Üst klasördeki database modülüne ulaşmak için bu küçük ayarı çakıyoruz.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import db_manager

from dotenv import load_dotenv

# Şifreleri ve yetkili ID'leri sakladığımız gizli dosyayı okutuyoruz.
load_dotenv()

# .env'den müdürün ve teknik ekibin ID'lerini çekiyoruz. 
# Kimse kimsenin yetkisine çökmesin diye :)
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
TEKNIK_IDS = [int(i) for i in os.getenv("TEKNIK_IDS", "").split(",") if i]

def yetki_kontrol(user_id, rol="personel"):
    """
    Güvenlik kapısı:
    rol="personel" -> Temizlikçi, resepsiyon falan herkes.
    rol="teknik"   -> Sadece elinde tornavida olan teknik ekip ve müdür.
    rol="admin"    -> Sadece büyük patron (Otel Müdürü).
    """
    if rol == "admin":
        return user_id == ADMIN_ID
    if rol == "teknik":
        return user_id == ADMIN_ID or user_id in TEKNIK_IDS
    return True # Düz personel ise kapı herkese açık.


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Bota ilk girenlere ne yapacaklarını anlatan karşılama menüsü
    mesaj = (
        "🏨 **IT & Arıza Bildirim Sistemine Hoş Geldiniz**\n\n"
        "Mevcut Komutlar:\n"
        "🛠️ `/ariza [Oda No] [Sorun]` - Yeni arıza bildirimi\n"
        "📋 `/bekleyenler` - Açık arızaları listele\n"
        "✅ `/cozuldu [ID]` - Arızayı çözüldü olarak kapat\n"
        "📊 `/rapor` - Tüm arızaları Excel olarak indir (Yönetici)"
    )
    await update.message.reply_text(mesaj, parse_mode='Markdown')


async def ariza(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Adam sadece /ariza yazıp bırakmışsa uyaralım, oda no ve sorunu da yazsın.
    if len(context.args) < 2:
        await update.message.reply_text("❌ Hatalı kullanım! Örnek: `/ariza 105 Klima su akıtıyor`",
                                        parse_mode='Markdown')
        return

    oda_no = context.args[0]
    sorun = " ".join(context.args[1:])
    kullanici = update.effective_user.first_name

    # Veriyi DB'ye zımbala ve bize bir ticket ID'si versin
    kayit_id = db_manager.add_fault(oda_no, sorun, kullanici)

    # İşlemin alındığına dair geri bildirim
    await update.message.reply_text(
        f"✅ **Arıza Sisteme Eklendi!**\n\n"
        f"🔖 Kayıt ID: `#{kayit_id}`\n"
        f"📍 Konum: {oda_no}\n"
        f"⚠️ Sorun: {sorun}\n\n"
        f"Teknik ekibe iletildi.",
        parse_mode='Markdown'
    )


async def bekleyenler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Çözülmemiş işleri veritabanından çek
    acik_arizalar = db_manager.get_open_faults()

    if not acik_arizalar:
        await update.message.reply_text("🎉 Harika! Şu an otelde bekleyen hiçbir arıza yok. Çay içebiliriz.")
        return

    # Listeyi döküp formatlıyoruz
    mesaj = "🔴 **BEKLEYEN ARIZALAR LİSTESİ** 🔴\n\n"
    for ariza in acik_arizalar:
        kayit_id, oda, sorun, saat = ariza
        mesaj += f"🔖 **ID #{kayit_id}** | 📍 {oda}\n⚠️ {sorun}\n🕒 {saat}\n➖➖➖➖➖➖\n"

    mesaj += "\n_Görevi kapatmak için: /cozuldu [ID] yazın._"
    await update.message.reply_text(mesaj, parse_mode='Markdown')


async def cozuldu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Güvenlik Kontrolü: Kat görevlisi arıza kapatamasın, sadece teknik ekip!
    if not yetki_kontrol(user_id, rol="teknik"):
        await update.message.reply_text("🚫 **HATA:** Arızayı sadece Teknik Ekip personeli kapatabilir.")
        return
        
    if len(context.args) < 1:
        await update.message.reply_text("❌ Hangi arızayı çözdünüz? Örnek: `/cozuldu 1`", parse_mode='Markdown')
        return

    # Adam harf falan girerse bot patlamasın diye try-except koyuyoruz
    try:
        fault_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Lütfen geçerli bir Kayıt ID'si (Sayı) girin.")
        return

    # DB'de arızayı yeşile boyuyoruz (ÇÖZÜLDÜ yapıyoruz)
    basarili = db_manager.mark_resolved(fault_id)
    if basarili:
        await update.message.reply_text(f"✅ **#{fault_id} numaralı arıza başarıyla ÇÖZÜLDÜ olarak kapatıldı! Eline sağlık.**",
                                        parse_mode='Markdown')
    else:
        await update.message.reply_text("⚠️ Hata: Böyle bir açık arıza bulunamadı veya daha önce birisi çoktan çözmüş.")


async def rapor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Patron kontrolü: Bu raporu sadece müdür alabilir, başkası denerse kapı duvar.
    if not yetki_kontrol(user_id, rol="admin"):
        await update.message.reply_text("🚫 **YETKİSİZ ERİŞİM:** Bu raporu sadece Otel Müdürü isteyebilir.")
        return

    await update.message.reply_text("📊 Otel verileri toplanıyor, Excel'i hazırlıyorum...")

    # DB'deki her şeyi Excel'e dök
    dosya_adi = db_manager.export_to_excel()

    # Dosyayı alıp Telegram üzerinden müdüre paslıyoruz
    with open(dosya_adi, 'rb') as dosya:
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=dosya,
            caption="🏨 **Otel Arıza & Operasyon Raporu**\nTüm kayıtlar başarıyla Excel formatında dışa aktarıldı. İyi çalışmalar müdürüm.",
            parse_mode='Markdown'
        )
