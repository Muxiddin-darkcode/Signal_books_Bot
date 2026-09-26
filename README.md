---
title: Signal Books Bot
emoji: 📚
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# 📚 Signal Books — Telegram Web App Boti


Ushbu bot **Signal Books** loyihangizning veb-saytini Telegram ichida zamonaviy **Telegram Mini App (Web App)** sifatida qulay ochib berish va do'koningizni to'liq boshqarish uchun yaratilgan.

---

## 🚀 Asosiy Imkoniyatlar

### 👤 Foydalanuvchilar uchun:
- **Telegram Mini App:** Telegram ichidan chiqmasdan to'liq ekranda yoki oyna rejimida kitoblar saytini ochish (`📚 Signal Books (Saytni ochish)`).
- **Pastki menyu tugmasi:** Telegram chatining pastki chap burchagidagi doimiy "Signal Books" tugmasi.
- **Inline tugma:** Har bir xabar ostidagi to'g'ridan-to'g'ri Web App havolasi.
- **Biz haqimizda & Aloqa:** Do'kon ma'lumotlari va qo'llab-quvvatlash xizmati.
- **💬 Adminga Murojaat / Support:** Bot ichidan turib adminga to'g'ridan-to'g'ri savol, murojaat yoki buyurtma yuborish.
- **💡 Kitob taklif qilish (Rasm bilan):** Foydalanuvchilar o'zlari istagan kitob nomini, muallifini va muqova rasmini yuborish imkoniyati.
- **📋 Mening takliflarim:** Foydalanuvchi o'zi taklif qilgan kitoblar holatini (⏳ Kutilmoqda, ✅ Qabul qilindi, ❌ Rad etildi) jonli kuzatib borishi.
- **🔗 Ulashish:** Botni do'stlarga bir tugma bilan tavsiya qilish.

### 👑 Admin Panel (`/admin`):
- 📊 **Jonli Statistika:**
  - Jami foydalanuvchilar soni
  - Faol a'zolar
  - Botni bloklaganlar
  - Bugungi yangi tashrif buyuruvchilar
- 💡 **Kitob Takliflari Boshqaruvi:**
  - Foydalanuvchilar yuborgan takliflarni (muqova rasmi bilan) ko'rish, qabul qilish yoki rad etish
  - Foydalanuvchiga to'g'ridan-to'g'ri bot orqali javob xati yozish
- 💬 **Murojaatlarni (Support) Boshqarish:**
  - Foydalanuvchilar yuborgan savollarga bot orqali to'g'ridan-to'g'ri tezkor javob yozish
- 📢 **Kengaytirilgan Xabar Tarqatish (Broadcast):**
  - Barcha foydalanuvchilarga matn, rasm, video, e'lonlarni yuborish.
  - **👁 O'zida sinab ko'rish (Preview):** Tarqatishdan oldin admin o'z profiliga xabarni sinov tariqasida yuborib ko'rishi mumkin.
  - **🚀 Mini App tugmasi bilan yuborish:** Xabar ostiga avtomatik Web App ochuvchi tugma ulab yuborish.
  - Telegram cheklovlariga (flood limit) tushmaslik uchun xavfsiz sekinlik bilan yuborish.
  - Bloklagan foydalanuvchilarni avtomatik aniqlash va hisobot berish.
- 🌐 **Dinamik Web App URL:**
  - Saytingiz havolasini kodga tegmasdan to'g'ridan-to'g'ri bot orqali istalgan paytda o'zgartirish.
  - Barcha tugmalar va menyular yangi saytga avtomatik o'tadi.
- 📢 **Majburiy Obuna (Kanal):**
  - Foydalanuvchilar botdan foydalanishi uchun kanalingizga a'zo bo'lishini talab qilish (xohlasangiz yoqish, xohlasangiz o'chirish).
- ✏️ **Matnlarni Tahrirlash:**
  - "Biz haqimizda" va "Bog'lanish" matnlarini bot orqali tahrirlash.
- 📥 **Foydalanuvchilar Bazasini Yuklab Olish (CSV/Excel):**
  - Barcha foydalanuvchilar ro'yxati, IDsi, ro'yxatdan o'tgan vaqti bilan fayl holatida olish.

---

## 🛠 O'rnatish va Ishga Tushirish

### 1-qadam: Bot Token va Admin ID olish
1. Telegramda [@BotFather](https://t.me/BotFather) botiga kiring va `/newbot` buyrug'i orqali yangi bot oching (masalan: `Signal Books`).
2. BotFather bergan **HTTP API Token**ni nusxalab oling.
3. O'zingizning Telegram ID raqamingizni bilish uchun [@userinfobot](https://t.me/userinfobot) ga kiring va ID raqamingizni oling.

### 2-qadam: `.env` faylini to'ldirish
Loyihaning asosiy papkasidagi `.env` faylini oching va ma'lumotlaringizni kiriting:

```env
# Bot tokeni
BOT_TOKEN=1234567890:AAH...sizning_tokeningiz

# Admin ID raqamingiz (bir nechta bo'lsa vergul bilan yozing: 12345678,87654321)
ADMIN_IDS=123456789

# Saytingizning HTTPS havolasi
WEB_APP_URL=https://sizning-saytingiz.uz
```

> [!NOTE]
> Telegram Web App ishlashi uchun havola albatta `https://` protokoli bilan boshlanishi kerak.

### 3-qadam: Ishga tushirish
Windows tizimida bot papkasidagi **`run.bat`** faylini ikki marta bosish orqali ishga tushirishingiz mumkin.

Yoki buyruqlar satrida (Terminal):
```bash
py -m venv venv
.\venv\Scripts\pip install -r requirements.txt
.\venv\Scripts\python main.py
```

---

## ☁️ 24/7 Bepul Serverga Yuklash (Render yoki Koyeb)

### Variant 1: Render.com (Tavsiya etiladi - 1 daqiqada)
1. [Render.com](https://render.com) ga kiring va GitHub orqali ro'yxatdan o'ting.
2. **New +** tugmasini bosing va **Web Service** ni tanlang.
3. `Signal_books_Bot` omboringizni tanlang.
4. Sozlamalar:
   - **Name:** `signal-books-bot`
   - **Language / Runtime:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
   - **Instance Type:** `Free`
5. **Environment Variables** (Muhit o'zgaruvchilari) bo'limida 3 ta qiymatni kiriting:
   - `BOT_TOKEN` = Sizning bot tokeningiz
   - `ADMIN_IDS` = Sizning Telegram ID raqamingiz
   - `WEB_APP_URL` = Saytingiz havolasi (https://signal-books.vercel.app/)
6. **Deploy Web Service** tugmasini bosing. Bot bir necha soniyada 24/7 ishlab boshlaydi!

### Variant 2: Koyeb.com
1. [Koyeb.com](https://www.koyeb.com) ga kiring va GitHub hisobingiz bilan kiring.
2. **Create Service** -> **GitHub** -> `Signal_books_Bot` omborini tanlang.
3. Builder: **Dockerfile** yoki **Buildpack** ni tanlang.
4. **Environment Variables** bo'limida `BOT_TOKEN`, `ADMIN_IDS`, `WEB_APP_URL` larni qo'shing.
5. **Deploy** tugmasini bosing.

---

## 💡 BotFather'da Web App menyu tugmasini ulash (Tavsiya etiladi)

Telegram foydalanuvchilariga yanada chiroyli ko'rinishi uchun:
1. [@BotFather](https://t.me/BotFather) ga kiring.
2. `/mybots` buyrug'ini bering va o'z botingizni tanlang.
3. **Bot Settings** -> **Menu Button** -> **Configure menu button** bo'limiga kiring.
4. Saytingiz URL manzilini (`https://...`) va tugma matnini (masalan: `Signal Books`) kiriting.

---

### 5. Firebase Firestore Sozlash (Tavsiya etiladi - 24/7 Doimiy Baza):
Bot ma'lumotlari (foydalanuvchilar, sozlamalar, takliflar) server qayta ishga tushganda o'chib ketmasligi uchun Firebase Firestore'ga ulangan:
1. [Firebase Console](https://console.firebase.google.com/) ga kiring va yangi loyiha oching.
2. **Build** -> **Firestore Database** bo'limiga kirib, **Create database** tugmasini bosing (Start in production mode yoki test mode).
3. **Project Settings** (sozlamalar tishli g'ildiragi) -> **Service accounts** bo'limiga o'ting.
4. **Generate new private key** tugmasini bosing. Sizga `.json` fayl yuklanadi.
5. Yuklangan fayl nomini **`serviceAccountKey.json`** deb o'zgartirib, loyihaning asosiy papkasiga tashlang.
6. Agar sizda avvalgi SQLite bazasida ma'lumotlar bo'lsa, ularni Firebase'ga ko'chirish uchun quyidagi buyruqni ishga tushiring:
   ```bash
   python migrate_sqlite_to_firebase.py
   ```

---

## 📁 Loyiha Strukturasi

```
Signal books bot/
├── .env                          # Sozlamalar (Token, Adminlar, Sayt havolasi, Firebase)
├── .env.example                  # Namuna sozlamalar fayli
├── requirements.txt              # Kerakli Python kutubxonalari (aiogram, firebase-admin va h.k.)
├── run.bat                       # Bir marta bosish bilan ishga tushirish fayli
├── main.py                       # Asosiy ishga tushirish skripti
├── migrate_sqlite_to_firebase.py # SQLite'dan Firebase'ga ko'chirish skripti
├── serviceAccountKey.json        # Firebase Admin kaliti (siz qo'shasiz, gitga kirmaydi)
├── signal_books.db               # SQLite ma'lumotlar bazasi (zaxira)
└── bot/
    ├── config.py                 # Konfiguratsiya va sozlamalar
    ├── database/
    │   ├── db.py                 # Asosiy DB router (Firebase va SQLite)
    │   └── firebase_db.py        # Firebase Firestore integratsiyasi
    ├── handlers/
    │   ├── admin.py              # Admin panel handlerlari
    │   └── user.py               # Foydalanuvchi buyruqlari
    ├── keyboards/
    │   ├── admin_kb.py           # Admin inline tugmalari
    │   └── user_kb.py            # Foydalanuvchi menyu va Web App tugmalari
    ├── middlewares/
    │   └── db_middleware.py      # Foydalanuvchilarni avtomatik bazaga kiritish
    ├── states/
    │   └── admin_states.py       # FSM holatlari (broadcast, url o'zgartirish)
    └── utils/
        └── setup_bot.py          # Yordamchi sozlamalar
```

