"""Inline + reply keyboards."""
from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)


# --- customer-facing -------------------------------------------------------

def language_pick() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang:uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
        ]]
    )


def request_location_kb(lang: str) -> ReplyKeyboardMarkup:
    label = "📍 Geolokatsiya yuborish" if lang != "ru" else "📍 Отправить геолокацию"
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=label, request_location=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder=(
            "Yoki yozma manzil yuboring..." if lang != "ru" else "Или напишите адрес..."
        ),
    )


def request_contact_kb(lang: str) -> ReplyKeyboardMarkup:
    label = "📞 Telefon raqamni ulashish" if lang != "ru" else "📞 Поделиться номером"
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=label, request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder=(
            "Yoki raqamni yozib yuboring..." if lang != "ru" else "Или напишите номер..."
        ),
    )


def remove_kb() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


def main_menu_kb(lang: str) -> ReplyKeyboardMarkup:
    """Persistent reply keyboard with a single 'New order' / 'Reset' button.

    Until the customer taps this, the bot does not create an order — random
    text or accidental taps no longer trigger a phantom order.
    """
    label = "🆕 Yangi buyurtma" if lang != "ru" else "🆕 Новый заказ"
    placeholder = (
        "Yozing nima kerak..." if lang != "ru" else "Напишите, что нужно..."
    )
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=label)]],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder=placeholder,
    )


def payment_method_kb(order_id: int, lang: str, *, include_transfer: bool = True) -> InlineKeyboardMarkup:
    cash_label = "💵 Naqd, eshik oldida" if lang != "ru" else "💵 Наличные у двери"
    transfer_label = "💳 O'tkazma orqali" if lang != "ru" else "💳 Переводом"
    rows = [[InlineKeyboardButton(text=cash_label, callback_data=f"pay:cash:{order_id}")]]
    if include_transfer:
        rows.append([InlineKeyboardButton(text=transfer_label, callback_data=f"pay:transfer:{order_id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# --- ops-group (merchant) --------------------------------------------------

def order_controls(order_id: int, *, packing_done: bool = False) -> InlineKeyboardMarkup:
    """Buttons under each customer-message-relay in the ops group.

    Pre-packing: Accept, Reply, Start packing, Cancel.
    Post-packing (after merchant tapped 'Start packing'): On the way, Delivered,
    Reply, Cancel.

    Note: "Out of stock" was deliberately removed — a curt "not available"
    is bad customer service. The merchant should use "Reply" to explain,
    apologize, and propose an alternative.
    """
    if not packing_done:
        rows = [
            [
                InlineKeyboardButton(text="✅ Qabul qilindi", callback_data=f"act:accept:{order_id}"),
                InlineKeyboardButton(text="💬 Javob yozish", callback_data=f"act:reply:{order_id}"),
            ],
            [
                InlineKeyboardButton(text="📦 Yig'ishni boshlayman", callback_data=f"act:pack:{order_id}"),
                InlineKeyboardButton(text="🚫 Bekor qilish", callback_data=f"act:cancel:{order_id}"),
            ],
        ]
    else:
        rows = [
            [
                InlineKeyboardButton(text="🚴 Yo'lda", callback_data=f"act:enroute:{order_id}"),
                InlineKeyboardButton(text="✅ Yetkazildi", callback_data=f"act:delivered:{order_id}"),
            ],
            [
                InlineKeyboardButton(text="💬 Javob yozish", callback_data=f"act:reply:{order_id}"),
                InlineKeyboardButton(text="🚫 Bekor qilish", callback_data=f"act:cancel:{order_id}"),
            ],
        ]
    return InlineKeyboardMarkup(inline_keyboard=rows)
