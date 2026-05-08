from telegram import Update
from telegram.ext import ContextTypes
import sys
import os

# Üst klasördeki database modülünü çağırabilmek için yol ayarı
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import db_manager

from dotenv import load_dotenv

load_dotenv()

ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
TEKNIK_IDS = [int(i) for i in os.getenv("TEKNIK_IDS", "").split(",") if i]

def yetki_kontrol(user_id, rol="personel"):
    """
    rol="personel" -> Herkes kullanabilir
    rol="teknik"   -> Teknik ekip veya Admin kullanabilir
    rol="admin"    -> Sadece Admin kullanabilir
    """
    if rol == "admin":
        return user_id == ADMIN_ID
    if rol == "teknik":
        return user_id == ADMIN_ID or user_id in TEKNIK_IDS
    return True # Personel ise herkes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    if len(context.args) < 2:
        await update.message.reply_text("❌ Hatalı kullanım! Örnek: `/ariza 105 Klima su akıtıyor`",
                                        parse_mode='Markdown')
        return

    oda_no = context.args[0]
    sorun = " ".join(context.args[1:])
    kullanici = update.effective_user.first_name

    # Veritabanına kaydet ve ID'sini al
    kayit_id = db_manager.add_fault(oda_no, sorun, kullanici)

    await update.message.reply_text(
        f"✅ **Arıza Sisteme Eklendi!**\n\n"
        f"🔖 Kayıt ID: `#{kayit_id}`\n"
        f"📍 Konum: {oda_no}\n"
        f"⚠️ Sorun: {sorun}\n\n"
        f"Teknik ekibe iletildi.",
        parse_mode='Markdown'
    )


async def bekleyenler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    acik_arizalar = db_manager.get_open_faults()

    if not acik_arizalar:
        await update.message.reply_text("🎉 Harika! Şu an otelde bekleyen hiçbir arıza yok.")
        return

    mesaj = "🔴 **BEKLEYEN ARIZALAR LİSTESİ** 🔴\n\n"
    for ariza in acik_arizalar:
        kayit_id, oda, sorun, saat = ariza
        mesaj += f"🔖 **ID #{kayit_id}** | 📍 {oda}\n⚠️ {sorun}\n🕒 {saat}\n➖➖➖➖➖➖\n"

    mesaj += "\n_Görevi kapatmak için: /cozuldu [ID] yazın._"
    await update.message.reply_text(mesaj, parse_mode='Markdown')


async def cozuldu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # KRİTİK KONTROL: Teknik Ekip veya Admin
    if not yetki_kontrol(user_id, rol="teknik"):
        await update.message.reply_text("🚫 **HATA:** Arızayı sadece Teknik Ekip personeli kapatabilir.")
        return
    if len(context.args) < 1:
        await update.message.reply_text("❌ Hangi arızayı çözdünüz? Örnek: `/cozuldu 1`", parse_mode='Markdown')
        return

    try:
        fault_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Lütfen geçerli bir Kayıt ID'si (Sayı) girin.")
        return

    basarili = db_manager.mark_resolved(fault_id)
    if basarili:
        await update.message.reply_text(f"✅ **#{fault_id} numaralı arıza başarıyla ÇÖZÜLDÜ olarak kapatıldı!**",
                                        parse_mode='Markdown')
    else:
        await update.message.reply_text("⚠️ Hata: Böyle bir açık arıza bulunamadı veya zaten çözülmüş.")


async def rapor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # KRİTİK KONTROL: Sadece Admin
    if not yetki_kontrol(user_id, rol="admin"):
        await update.message.reply_text("🚫 **YETKİSİZ ERİŞİM:** Bu raporu sadece Otel Müdürü isteyebilir.")
        return

    await update.message.reply_text("📊 Otel verileri toplanıyor...")

    dosya_adi = db_manager.export_to_excel()

    with open(dosya_adi, 'rb') as dosya:
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=dosya,
            caption="🏨 **Otel Arıza & Operasyon Raporu**\nTüm kayıtlar başarıyla Excel formatında dışa aktarıldı.",
            parse_mode='Markdown'
        )