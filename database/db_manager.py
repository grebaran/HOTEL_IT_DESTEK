import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "hotel_data.db"


def init_db():
    """Veritabanını ve gerekli tabloları sıfırdan oluşturur."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faults (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_no TEXT NOT NULL,
            issue TEXT NOT NULL,
            reported_by TEXT,
            status TEXT DEFAULT 'AÇIK 🔴',
            reported_at TIMESTAMP,
            resolved_at TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def add_fault(room_no, issue, reported_by):
    """Sisteme yeni bir arıza kaydı ekler."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO faults (room_no, issue, reported_by, reported_at) VALUES (?, ?, ?, ?)",
        (room_no, issue, reported_by, now)
    )
    conn.commit()
    fault_id = cursor.lastrowid
    conn.close()
    return fault_id


def get_open_faults():
    """Henüz çözülmemiş (AÇIK) arızaları listeler."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, room_no, issue, reported_at FROM faults WHERE status='AÇIK 🔴'")
    records = cursor.fetchall()
    conn.close()
    return records


def mark_resolved(fault_id):
    """Belirtilen ID'ye sahip arızayı 'ÇÖZÜLDÜ' olarak işaretler."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "UPDATE faults SET status='ÇÖZÜLDÜ 🟢', resolved_at=? WHERE id=? AND status='AÇIK 🔴'",
        (now, fault_id)
    )
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0


def export_to_excel(filename="otel_ariza_raporu.xlsx"):
    """Tüm veritabanını yöneticiler için şık bir Excel (.xlsx) dosyasına dönüştürür."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM faults", conn)
    conn.close()

    # Sütun isimlerini Türkçeleştirip güzelleştirelim
    df.rename(columns={
        'id': 'Kayıt No',
        'room_no': 'Oda / Konum',
        'issue': 'Arıza Detayı',
        'reported_by': 'Bildiren Kişi',
        'status': 'Durum',
        'reported_at': 'Bildirim Saati',
        'resolved_at': 'Çözüm Saati'
    }, inplace=True)

    df.to_excel(filename, index=False)
    return filename