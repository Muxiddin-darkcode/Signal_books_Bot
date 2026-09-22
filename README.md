# 📚 Signal Books — Telegram Web App Boti

Ushbu bot **Signal Books** loyihangizning veb-saytini Telegram ichida zamonaviy **Telegram Mini App (Web App)** sifatida qulay ochib berish va do'koningizni to'liq boshqarish uchun yaratilgan.

---

## 🚀 Asosiy Imkoniyatlar

### 👤 Foydalanuvchilar uchun:
- **Telegram Mini App:** Telegram ichidan chiqmasdan to'liq ekranda yoki oyna rejimida kitoblar saytini ochish (`📚 Signal Books (Saytni ochish)`).
- **Pastki menyu tugmasi:** Telegram chatining pastki chap burchagidagi doimiy "Signal Books" tugmasi.
- **Inline tugma:** Har bir xabar ostidagi to'g'ridan-to'g'ri Web App havolasi.
- **Biz haqimizda & Aloqa:** Do'kon ma'lumotlari va qo'llab-quvvatlash xizmati.
- **Kitob taklif qilish:** Foydalanuvchilar o'zlari istagan kitoblarni taklif qilish imkoniyati.
- **Ulashish:** Botni do'stlarga bir tugma bilan tavsiya qilish.

### 👑 Admin Panel (`/admin`):
- 📊 **Jonli Statistika:**
  - Jami foydalanuvchilar soni
  - Faol a'zolar
  - Botni bloklaganlar
  - Bugungi yangi tashrif buyuruvchilar
- 💡 **Kitob Takliflari Boshqaruvi:**
  - Foydalanuvchilar yuborgan takliflarni ko'rish, qabul qilish yoki rad etish
  - Foydalanuvchiga to'g'ridan-to'g'ri bot orqali javob xati yozish
- 📢 **Kengaytirilgan Xabar Tarqatish (Broadcast):**
  - Barcha foydalanuvchilarga matn, rasm, video, e'lonlarni yuborish.
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

## 💡 BotFather'da Web App menyu tugmasini ulash (Tavsiya etiladi)

Telegram foydalanuvchilariga yanada chiroyli ko'rinishi uchun:
1. [@BotFather](https://t.me/BotFather) ga kiring.
2. `/mybots` buyrug'ini bering va o'z botingizni tanlang.
3. **Bot Settings** -> **Menu Button** -> **Configure menu button** bo'limiga kiring.
4. Saytingiz URL manzilini (`https://...`) va tugma matnini (masalan: `Signal Books`) kiriting.

---

## 📁 Loyiha Strukturasi

```
Signal books bot/
├── .env                     # Sozlamalar (Token, Adminlar, Sayt havolasi)
├── .env.example             # Namuna sozlamalar fayli
├── requirements.txt         # Kerakli Python kutubxonalari
├── run.bat                  # Bir marta bosish bilan ishga tushirish fayli
├── main.py                  # Asosiy ishga tushirish skripti
├── signal_books.db          # SQLite ma'lumotlar bazasi (avtomatik yaratiladi)
└── bot/
    ├── config.py            # Konfiguratsiya
    ├── database/
    │   └── db.py            # Ma'lumotlar bazasi operatsiyalari
    ├── handlers/
    │   ├── admin.py         # Admin panel handlerlari
    │   └── user.py          # Foydalanuvchi buyruqlari
    ├── keyboards/
    │   ├── admin_kb.py      # Admin inline tugmalari
    │   └── user_kb.py       # Foydalanuvchi menyu va Web App tugmalari
    ├── middlewares/
    │   └── db_middleware.py # Foydalanuvchilarni avtomatik bazaga kiritish
    ├── states/
    │   └── admin_states.py  # FSM holatlari (broadcast, url o'zgartirish)
    └── utils/
        └── setup_bot.py     # Yordamchi sozlamalar
```
