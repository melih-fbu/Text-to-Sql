# 🤖 Bruin — AI Veri Asistanı

Doğal dil ile şirket verilerinizi sorgulayın. SQL yazmaya gerek yok!

Slack veya web arayüzü üzerinden soru sorun, Bruin arka planda Gemini AI ile SQL üretir, veritabanında çalıştırır ve sonuçları anlaşılır şekilde sunar.

## 🚀 Hızlı Başlangıç

### 1. Backend

```bash
cd backend
pip install -r requirements.txt

# .env dosyası oluşturun
cp .env.example .env
# GEMINI_API_KEY değerini düzenleyin

# Sunucuyu başlatın
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Tarayıcıda `http://localhost:5173` adresini açın.

## 📁 Proje Yapısı

```
Bruin/
├── backend/              # FastAPI Backend
│   ├── app/
│   │   ├── main.py       # Ana uygulama
│   │   ├── config.py     # Ayarlar
│   │   ├── database.py   # Veritabanı modelleri
│   │   ├── routers/      # API endpointleri
│   │   ├── services/     # İş mantığı
│   │   └── prompts/      # AI prompt şablonları
│   └── requirements.txt
│
├── frontend/             # React Admin Paneli
│   ├── src/
│   │   ├── pages/        # Sayfa bileşenleri
│   │   ├── components/   # UI bileşenleri
│   │   └── utils/        # Yardımcı fonksiyonlar
│   └── package.json
│
└── README.md
```

## 🔑 Ortam Değişkenleri

| Değişken | Açıklama | Zorunlu |
|----------|----------|---------|
| `GEMINI_API_KEY` | Google Gemini API anahtarı | ✅ |
| `SLACK_BOT_TOKEN` | Slack Bot Token | ❌ |
| `SLACK_SIGNING_SECRET` | Slack Signing Secret | ❌ |
| `DATABASE_URL` | Metadata DB | ❌ (default: SQLite) |

## 🧠 Nasıl Çalışır?

1. **Soru** → Kullanıcı Türkçe/İngilizce soru sorar
2. **AI** → Gemini soruyu SQL'e çevirir
3. **Güvenlik** → SQL güvenlik kontrolünden geçer (sadece SELECT)
4. **Çalıştırma** → Veritabanında sorgu çalıştırılır
5. **Yorumlama** → Gemini sonuçları yorumlar
6. **Yanıt** → Tablo + içgörü olarak sunulur

## 📡 API Endpointleri

| Endpoint | Metod | Açıklama |
|----------|-------|----------|
| `/api/v1/chat/ask` | POST | Soru sor |
| `/api/v1/schemas/discover` | GET | Veritabanı şemasını keşfet |
| `/api/v1/queries/history` | GET | Sorgu geçmişi |
| `/api/v1/queries/stats` | GET | İstatistikler |
| `/api/v1/slack/events` | POST | Slack webhook |
| `/docs` | GET | Swagger UI |

## 💬 Slack Entegrasyonu

1. [Slack API](https://api.slack.com/apps) üzerinden yeni bir app oluşturun
2. Bot Token Scopes: `chat:write`, `app_mentions:read`
3. Event Subscriptions URL: `https://your-domain.com/api/v1/slack/events`
4. Subscribe to: `app_mention`
5. `.env` dosyasına `SLACK_BOT_TOKEN` ve `SLACK_SIGNING_SECRET` ekleyin

## 📜 Lisans

MIT
