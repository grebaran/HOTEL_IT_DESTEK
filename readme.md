# Hotel IT Destek

## Proje Özeti
Otel operasyonlarında, özellikle yoğun sezonlarda veya yeni açılış (pre-opening) süreçlerinde departmanlar arası teknik iletişimi toparlamak için geliştirdiğim Telegram tabanlı bir arıza takip ve görev (ticket) yönetim sistemidir. Telsiz trafiğini azaltarak tüm teknik servis taleplerini dijital bir veritabanında saat ve kişi bazlı kayıt altına alır.

<img width="%15" height="2048" alt="bilgi_ekranı" src="https://github.com/user-attachments/assets/985c7883-f689-4df3-8855-33c5ba0c0bc8"/>




## Neden Böyle Bir Programa İhtiyaç Var?
Otelcilikte klasik bir kaos vardır: Kat görevlisi (Housekeeping) veya resepsiyon, odadaki bir arızayı teknik servise telsizden veya WhatsApp gruplarından yazar. Teknik personel o an başka bir işte olduğu için "tamam" der ama yoğunluktan unutulur. Akşam odaya giriş yapan misafir klimanın çalışmadığını veya TV'nin bozuk olduğunu görünce şikayet eder. 

Sonuç; düşen misafir memnuniyeti, departmanlar arası "ben sana söylemiştim" tartışmaları ve uzayan çözüm süreleridir. Bu program, havaya uçan sözlü bildirimleri tamamen ortadan kaldırıp, sıfır donanım maliyetiyle her şeyi ölçülebilir bir dijital sisteme dökmek için yazılmıştır.

## Sistem Detayları ve Altyapı
Sistem otellere ekstra sunucu veya lisans maliyeti çıkarmaması için son derece hafif ve hızlı çalışacak şekilde tasarlandı. 
* **Dil & Mimarisi:** Python 3.10 kullanılarak asenkron yapıda (python-telegram-bot) kodlandı. Bu sayede aynı anda onlarca personelin talebini çökmeden karşılayabilir.
* **Veritabanı (Gömülü):** Ağır ve kurulumu zor SQL sunucuları yerine, sistemin içine gömülü SQLite kullanıldı. Veriler otelin lokal bilgisayarında güvenle tutulur.
* **Rol ve Yetkilendirme (RBAC):** Sistemin içinde güvenlik hiyerarşisi vardır. Personel sadece arıza bildirebilir, arızayı sadece teknik ekip kapatabilir. Otelin tüm Excel raporunu ise sadece Telegram ID'si sisteme tanımlanmış olan "Yönetici" çekebilir.

## Kurulum: Nasıl Yapılır?
Sistemi herhangi bir bilgisayarda (veya otelin lokal sunucusunda) ayağa kaldırmak 2 dakika sürer:

1. Projeyi bilgisayarınıza indirin:
   `git clone https://github.com/grebaran/HOTEL_IT_DESTEK.git`
2. Klasöre girip gerekli kütüphaneleri yükleyin:
   `pip install -r requirements.txt`
3. Klasörün içinde `.env` isimli bir metin belgesi oluşturun ve içine bot yetkilerini yazın:
   `TELEGRAM_TOKEN=botfatherdan_alinan_token`
   `ADMIN_ID=yoneticinin_telegram_id_numarasi`
4. Programı başlatın:
   `python main.py`

*(Not: KVKK ve siber güvenlik standartları gereği, hassas veriler barındıran `.db` veritabanı dosyası ve `.env` şifre dosyası GitHub deposuna yüklenmemiştir.)*

## Sistem Nasıl Kullanılır? (Telegram Komutları)
Program çalıştıktan sonra otel personeli hiçbir ekstra uygulama indirmeden sadece Telegram üzerinden bot ile konuşarak süreci yönetir:

* **Arıza Bildirmek İçin:** 
  Personel bota `/ariza 105 Klima su akıtıyor` yazar. Bot bunu anında veritabanına ekler, benzersiz bir ID numarası atar ve saati kaydeder.
* **Açık Arızaları Görmek İçin:**
  Teknik personel işi bittiğinde bota `/bekleyenler` yazar. Sistem, henüz çözülmemiş tüm arızaları oda numarası ve saat sırasına göre listeler.
* **Görevi Kapatmak İçin:**
  Teknik personel 105 numaralı odadaki arızayı giderdiğinde bota `/cozuldu 1` (1 numaralı ID) yazar. Sorun loglardan silinmez ancak durumu "ÇÖZÜLDÜ" olarak güncellenir.
* **Yönetici Raporu Almak İçin:**
  Otel müdürü operasyon toplantısından önce bota sadece `/rapor` yazar. Bot, o haftaya ait tüm veritabanını, kimin hangi arızayı kaç dakikada çözdüğünü hesaplayıp anında temiz bir Excel (.xlsx) dosyası olarak müdürün telefonuna gönderir.

<img width="200" height="1744" alt="çalışma_kodları" src="https://github.com/user-attachments/assets/3d337fb3-071b-4e75-84c8-379638e658f6" />
