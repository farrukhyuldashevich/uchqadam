"""All customer-facing strings, bilingual. Merchant-side strings stay in Uzbek
(merchant is a single known person; no need to localize their UI).

Uses HTML parse mode. Allowed tags: <b>, <i>, <code>, <pre>, <a>.
Any value substituted into a template MUST be html-escaped first.
"""
from __future__ import annotations

Lang = str  # "uz" | "ru"


def pick(lang: Lang, uz: str, ru: str) -> str:
    return ru if lang == "ru" else uz


# --- customer-facing messages ---------------------------------------------

PICK_LANGUAGE_PROMPT = (
    "Assalomu alaykum! 🛒\n"
    "Tilni tanlang / Выберите язык:"
)

WELCOME_FIRST_TIME = {
    "uz": (
        "Xush kelibsiz! <b>{store}</b>dan mahallaga to'g'ridan-to'g'ri yetkazib beramiz — "
        "suv, non, sut, muzqaymoq va kundalik kerakli mahsulotlar.\n\n"
        "Buyurtma berish uchun pastdagi <b>🆕 Yangi buyurtma</b> tugmasini bosing 👇"
    ),
    "ru": (
        "Добро пожаловать! Доставляем напрямую из <b>{store}</b> — "
        "вода, хлеб, молоко, мороженое и всё необходимое.\n\n"
        "Чтобы заказать, нажмите <b>🆕 Новый заказ</b> внизу 👇"
    ),
}

WELCOME_RETURNING = {
    "uz": "Yana xush kelibsiz 🙏 Buyurtma berish uchun pastdagi <b>🆕 Yangi buyurtma</b> tugmasini bosing 👇",
    "ru": "С возвращением 🙏 Чтобы заказать, нажмите <b>🆕 Новый заказ</b> внизу 👇",
}

# Reply-keyboard button text. The customer must tap this to begin or reset
# an order — typing alone no longer auto-creates one.
NEW_ORDER_BTN = {
    "uz": "🆕 Yangi buyurtma",
    "ru": "🆕 Новый заказ",
}

NEW_ORDER_STARTED = {
    "uz": "Buyurtma boshlandi ✍️ Yozing — nima yetkazib beraylik bugun?",
    "ru": "Заказ начат ✍️ Напишите, что доставить сегодня?",
}

NEW_ORDER_REPLACED = {
    "uz": "Oldingi buyurtma bekor qilindi va yangisi boshlandi ✍️ Yozing — nima kerak?",
    "ru": "Предыдущий заказ отменён, начинаем новый ✍️ Напишите, что нужно?",
}

TAP_TO_START = {
    "uz": "Buyurtma berish uchun pastdagi <b>🆕 Yangi buyurtma</b> tugmasini bosing 👇",
    "ru": "Чтобы заказать, нажмите <b>🆕 Новый заказ</b> внизу 👇",
}

LANGUAGE_CONFIRMED = {
    "uz": "Til: O'zbekcha ✓",
    "ru": "Язык: Русский ✓",
}

LANGUAGE_SWITCHED = {
    "uz": "Til o'zbekchaga o'zgartirildi ✅",
    "ru": "Язык переключён на русский ✅",
}

ORDER_ACCEPTED = {
    "uz": "Qabul qilindi 🧾 Yana biron nima kerakmi?",
    "ru": "Принято 🧾 Что-то ещё?",
}

ORDER_PACKING_ASK_ADDRESS = {
    "uz": (
        "Buyurtmangiz tayyorlanmoqda 📦\n\n"
        "Yetkazib berish uchun <b>manzilingizni</b> yuboring:\n"
        "📍 Geolokatsiya orqali — eng tezi (pastdagi tugma)\n"
        "✍️ Yoki yozing: ko'cha, uy, pod'yezd, kvartira, mo'ljal"
    ),
    "ru": (
        "Заказ собираем 📦\n\n"
        "Отправьте, пожалуйста, <b>адрес доставки</b>:\n"
        "📍 Геолокацией — быстрее всего (кнопка ниже)\n"
        "✍️ Или текстом: улица, дом, подъезд, квартира, ориентир"
    ),
}

ADDRESS_RECEIVED_WAIT_BILL = {
    "uz": "Manzil qabul qilindi 👍 Hisobni hozir tayyorlaymiz...",
    "ru": "Адрес принят 👍 Сейчас подготовим счёт...",
}

BILL_TEMPLATE = {
    "uz": (
        "📋 <b>Hisob — Order #{order_id}</b>\n"
        "• Mahsulotlar: {items}\n"
        "• Yetkazib berish: {delivery}\n"
        "• <b>Jami: {total}</b>\n\n"
        "To'lov usulini tanlang:"
    ),
    "ru": (
        "📋 <b>Счёт — Order #{order_id}</b>\n"
        "• Товары: {items}\n"
        "• Доставка: {delivery}\n"
        "• <b>Итого: {total}</b>\n\n"
        "Выберите способ оплаты:"
    ),
}

BILL_TEMPLATE_CASH_PICKED = {
    "uz": (
        "📋 <b>Hisob — Order #{order_id}</b>\n"
        "• Mahsulotlar: {items}\n"
        "• Yetkazib berish: {delivery}\n"
        "• <b>Jami: {total}</b>\n\n"
        "✓ To'lov: <b>naqd, eshik oldida</b>"
    ),
    "ru": (
        "📋 <b>Счёт — Order #{order_id}</b>\n"
        "• Товары: {items}\n"
        "• Доставка: {delivery}\n"
        "• <b>Итого: {total}</b>\n\n"
        "✓ Оплата: <b>наличными у двери</b>"
    ),
}

BILL_TEMPLATE_TRANSFER_PICKED = {
    "uz": (
        "📋 <b>Hisob — Order #{order_id}</b>\n"
        "• Mahsulotlar: {items}\n"
        "• Yetkazib berish: {delivery}\n"
        "• <b>Jami: {total}</b>\n\n"
        "✓ To'lov: <b>o'tkazma</b>"
    ),
    "ru": (
        "📋 <b>Счёт — Order #{order_id}</b>\n"
        "• Товары: {items}\n"
        "• Доставка: {delivery}\n"
        "• <b>Итого: {total}</b>\n\n"
        "✓ Оплата: <b>перевод</b>"
    ),
}

PAYMENT_CASH_NEXT = {
    "uz": "Naqd to'lov tanlandi 💵\nEndi telefon raqamingizni yuboring (pastdagi tugma orqali).",
    "ru": "Выбрана оплата наличными 💵\nТеперь поделитесь номером телефона (кнопка ниже).",
}

PAYMENT_TRANSFER_INSTRUCTIONS = {
    "uz": (
        "O'tkazma uchun 💳\n\n"
        "<b>Karta:</b> <code>{card}</code>\n"
        "<b>Egasi:</b> {holder}\n"
        "<b>Summa:</b> {total}\n\n"
        "To'lov bo'lgach <b>chekni</b> shu yerga yuboring va telefon raqamingizni ulashing 👇"
    ),
    "ru": (
        "Для перевода 💳\n\n"
        "<b>Карта:</b> <code>{card}</code>\n"
        "<b>Получатель:</b> {holder}\n"
        "<b>Сумма:</b> {total}\n\n"
        "После оплаты пришлите <b>чек</b> сюда и поделитесь номером телефона 👇"
    ),
}

PAYMENT_TRANSFER_UNAVAILABLE = {
    "uz": "O'tkazma hozircha mavjud emas, naqd to'lov tanlang.",
    "ru": "Перевод временно недоступен, выберите наличные.",
}

ASK_PHONE = {
    "uz": "Telefon raqamingizni yuboring (pastdagi tugma orqali eng oson).",
    "ru": "Поделитесь номером телефона (проще всего через кнопку ниже).",
}

PHONE_RECEIVED = {
    "uz": "Rahmat 🙏 Buyurtmangiz tayyorlanmoqda. Tez orada eshigingiz oldida bo'lamiz.",
    "ru": "Спасибо 🙏 Заказ собирается. Скоро будем у двери.",
}

ORDER_ENROUTE = {
    "uz": "Buyurtmangiz yo'lda 🚴 Tez orada yetib boramiz.",
    "ru": "Заказ в пути 🚴 Скоро будем.",
}

ORDER_DELIVERED = {
    "uz": "Yetkazib berildi 🙏 Rahmat! Yana kerak bo'lsa shu yerga yozavering.",
    "ru": "Доставлено 🙏 Спасибо! Если что-то понадобится — пишите сюда.",
}

ORDER_CANCELLED = {
    "uz": "Buyurtma bekor qilindi. Savol bo'lsa yozing, biz shu yerdamiz.",
    "ru": "Заказ отменён. Если будут вопросы — пишите, мы здесь.",
}

CUSTOM_REPLY_PREFIX = {
    "uz": "👨‍🍳 <b>Sotuvchidan:</b>",
    "ru": "👨‍🍳 <b>От продавца:</b>",
}

INVALID_INPUT_ASK_ADDRESS = {
    "uz": "Iltimos, manzilingizni <b>geolokatsiya</b> bilan yoki <b>yozma</b> yuboring.",
    "ru": "Пожалуйста, отправьте <b>геолокацию</b> или <b>текст с адресом</b>.",
}

INVALID_INPUT_ASK_PHONE = {
    "uz": "Iltimos, <b>kontakt tugmasi</b> orqali yoki <b>raqam yozib</b> yuboring.",
    "ru": "Пожалуйста, отправьте <b>контакт</b> или <b>напишите номер</b>.",
}

HELP = {
    "uz": (
        "Buyurtma berish uchun shu yerga yozing nima kerakligini.\n"
        "/til — tilni o'zgartirish\n"
        "/start — qaytadan boshlash"
    ),
    "ru": (
        "Чтобы заказать, просто напишите сюда, что нужно.\n"
        "/til — сменить язык\n"
        "/start — начать заново"
    ),
}


# --- ops-group strings (Uzbek-only, merchant-facing) ----------------------

OPS_NEW_MESSAGE = (
    "💬 <b>Order #{order_id}</b> — {user_label}\n"
    "<i>Til: {lang}</i>\n\n"
    "{text}"
)

OPS_NEW_ORDER_HINT = (
    "<i>Yangi buyurtma. Mijoz hali biror narsa so'rayotgan bo'lishi mumkin — "
    "shu xabarga reply qilib yoki «💬 Javob yozish» tugmasi orqali javob bering. "
    "Buyurtma to'liq aniq bo'lsa, «✅ Qabul qilindi» bosing.</i>"
)

OPS_CUSTOMER_RESET = (
    "🚫 <b>Order #{order_id}</b> — mijoz buyurtmani bekor qilib yangisini boshladi."
)

OPS_ADDRESS_RECEIVED_TEXT = "📍 <b>Order #{order_id}</b> — manzil: {address}"
OPS_ADDRESS_RECEIVED_GEO = "📍 <b>Order #{order_id}</b> — geolokatsiya yuborildi"
OPS_PHONE_RECEIVED = "📞 <b>Order #{order_id}</b> — telefon: <code>{phone}</code>"

OPS_AMOUNT_PROMPT = (
    "📋 <b>Order #{order_id}</b> — <b>mahsulotlar summasini</b> kiriting (so'mda):\n"
    "<i>Faqat raqam, masalan: 32000. Yetkazib berish ({delivery}) avtomatik qo'shiladi.</i>"
)

OPS_AMOUNT_RECEIVED = (
    "✅ <b>Order #{order_id}</b> — summa qabul qilindi: {items}.\n"
    "Mijozga hisob yuborildi (jami: <b>{total}</b>)."
)

OPS_AMOUNT_INVALID = (
    "❌ Iltimos, summani <b>faqat raqam</b> bilan yozing.\n"
    "Masalan: <code>32000</code> yoki <code>32 000</code>."
)

OPS_PAYMENT_PICKED = (
    "💳 <b>Order #{order_id}</b> — mijoz tanladi: <b>{method}</b>"
)

OPS_ORDER_SUMMARY = (
    "📦 <b>Order #{order_id} — tayyor</b>\n"
    "👤 {user_label} ({lang})\n"
    "📍 {address}\n"
    "📞 <code>{phone}</code>\n"
    "💰 {items} + {delivery} yetkazish = <b>{total}</b>\n"
    "💳 To'lov: <b>{method}</b>"
)

OPS_RELAY_CONFIRMED = "✓ Mijozga yuborildi: <i>{preview}</i>"

OPS_REPLY_PROMPT = (
    "💬 <b>Order #{order_id}</b> — mijozga javob yozing:\n"
    "<i>(Shu xabarga reply qilib yozavering — yozganingiz mijozga \"Sotuvchidan: ...\" deb yetadi.)</i>"
)

OPS_HELP = (
    "<b>Emir Market — Ops</b>\n\n"
    "Mijozdan kelgan har bir xabar pastida tugmalar paydo bo'ladi:\n"
    "• <b>✅ Qabul qilindi</b> — buyurtma aniq, davom etamiz\n"
    "• <b>💬 Javob yozish</b> — mijozga o'z so'zlaringiz bilan javob (savol, taklif, alternativa)\n"
    "• <b>📦 Yig'ishni boshlayman</b> — mijozdan manzil so'raladi, keyin sizdan summa so'raladi\n"
    "• <b>🚴 Yo'lda</b> — yetkazib berishga chiqdik\n"
    "• <b>✅ Yetkazildi</b> — yopildi\n"
    "• <b>🚫 Bekor qilish</b> — buyurtma bekor\n\n"
    "Mijozga javob berish uchun shu xabarga <b>reply</b> qiling va yozavering.\n\n"
    "/orders — bugungi ochiq buyurtmalar"
)

OPS_OPEN_ORDERS_HEADER = "<b>Bugungi ochiq buyurtmalar:</b>"
OPS_OPEN_ORDERS_EMPTY = "<i>Hozircha ochiq buyurtmalar yo'q.</i>"
OPS_OPEN_ORDER_ROW = "• #{order_id} — {user_label} — <i>{status}</i>"


# --- payment method display labels (used in summary) ---------------------

PAYMENT_METHOD_LABEL = {
    "cash": "Naqd, eshik oldida",
    "transfer": "O'tkazma",
    None: "—",
}
