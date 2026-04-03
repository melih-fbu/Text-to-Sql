# 🤖 Truin — AI Veri Asistanı

Doğal dil ile şirket verilerinizi sorgulayın. SQL yazmaya gerek yok! Slack veya web arayüzü üzerinden soru sorun, Bruin arka planda **Gemini AI** ile SQL üretir, veritabanında çalıştırır ve sonuçları anlaşılır şekilde sunar.

---

## 🚀 Nasıl Çalışır?

1.  **Soru** ➔ Kullanıcı Türkçe/İngilizce soru sorar.
2.  **AI** ➔ Gemini soruyu SQL'e çevirir.
3.  **Güvenlik** ➔ SQL güvenlik kontrolünden geçer (sadece SELECT).
4.  **Çalıştırma** ➔ Veritabanında sorgu çalıştırılır.
5.  **Yorumlama** ➔ Gemini sonuçları yorumlar.
6.  **Yanıt** ➔ Tablo + içgörü olarak sunulur.

---

## 🛠 API Endpointleri

| Endpoint | Metod | Açıklama |
| :--- | :--- | :--- |
| `/api/v1/chat/ask` | `POST` | Soru sor |
| `/api/v1/schemas/discover` | `GET` | Veritabanı şemasını keşfet |
| `/api/v1/queries/history` | `GET` | Sorgu geçmişi |
| `/api/v1/queries/stats` | `GET` | İstatistikler |
| `/api/v1/slack/events` | `POST` | Slack webhook |
| `/docs` | `GET` | Swagger UI |

---

## 📜 Lisans
Bu proje **MIT** lisansı ile korunmaktadır.

#Text-to-Sql #AI #Gemini #FastAPI