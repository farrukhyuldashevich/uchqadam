"""Entry point for the Emir Market concierge bot.

Architecture:
    - Customers DM the bot.
    - Every DM chat has a persistent "🆕 New order" reply-keyboard button.
      The customer must tap it to start an order — random text no longer
      auto-creates one. Tapping it again resets (cancels the current order
      and opens a new one).
    - Each in-order customer message is mirrored into a private ops
      Telegram group with an inline keyboard of order controls underneath.
    - Merchant taps a preset button -> bot sends the canonical reply.
    - Merchant replies (native Telegram reply) to a bot ops-message ->
      the bot forwards the text as "Sotuvchidan: ..." to the customer.

Run with:
    python -m bot.main           (from repo root)
    or: python main.py           (from inside bot/)
"""
from __future__ import annotations

import asyncio
import html
import logging
import re
import sys
from typing import Optional

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatType, ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    ForceReply,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
)

try:
    from .config import Config
    from . import keyboards, messages as M
    from .storage import Storage
except ImportError:  # pragma: no cover
    from config import Config            # type: ignore[no-redef]
    import keyboards                     # type: ignore[no-redef]
    import messages as M                 # type: ignore[no-redef]
    from storage import Storage          # type: ignore[no-redef]


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("bot")


customer_router = Router(name="customer")
ops_router = Router(name="ops")


# ----- constants ------------------------------------------------------------

# Marker in an ops message text used to distinguish "merchant is typing the
# items amount" from "merchant is typing a custom reply to the customer".
AMOUNT_PROMPT_MARKER = "mahsulotlar summasini"

# Order statuses where a plain customer text message should be relayed to the
# ops group as conversation. Excludes awaiting_address / awaiting_phone (those
# have dedicated input handlers).
RELAY_STATUSES = {
    "open",
    "in_conversation",
    "accepted",
    "awaiting_amount",
    "awaiting_payment_method",
    "ready",
    "enroute",
}

# Statuses where the ops-group controls should show the post-packing button
# set (Yo'lda / Yetkazildi) instead of the initial (Qabul / Yig'ishni ...)
POST_PACK_STATUSES = {
    "awaiting_address",
    "awaiting_amount",
    "awaiting_payment_method",
    "awaiting_phone",
    "ready",
    "enroute",
}


# ----- helpers --------------------------------------------------------------

def user_label(msg_or_user) -> str:
    user = getattr(msg_or_user, "from_user", msg_or_user)
    if not user:
        return "unknown"
    if user.username:
        return f"@{user.username}"
    return user.full_name or f"id:{user.id}"


def lang_label(lang: str) -> str:
    return "🇺🇿 uz" if lang == "uz" else "🇷🇺 ru"


def truncate(text: str, n: int = 60) -> str:
    text = (text or "").strip().replace("\n", " ")
    return text if len(text) <= n else text[: n - 1] + "…"


def parse_callback(data: str) -> tuple[str, int]:
    parts = data.split(":")
    if len(parts) != 3:
        raise ValueError(f"bad callback {data!r}")
    return parts[1], int(parts[2])


ORDER_ID_RE = re.compile(r"Order #(\d+)", re.IGNORECASE)


def extract_order_id(text: Optional[str]) -> Optional[int]:
    if not text:
        return None
    m = ORDER_ID_RE.search(text)
    return int(m.group(1)) if m else None


def parse_amount(text: str) -> int:
    """'32 000 so'm' -> 32000. Raises ValueError on garbage."""
    digits = re.sub(r"[^\d]", "", text.strip())
    if not digits:
        raise ValueError("no digits")
    n = int(digits)
    if n <= 0 or n > 10_000_000:
        raise ValueError("out of range")
    return n


def fmt_sum(amount: int) -> str:
    return f"{amount:,}".replace(",", " ") + " so'm"


def payment_method_label(method: Optional[str]) -> str:
    return M.PAYMENT_METHOD_LABEL.get(method, "—")


def is_new_order_button(text: str) -> bool:
    """True if the text matches the 'New order' reply-keyboard button in
    either supported language. Also tolerates minor whitespace."""
    if not text:
        return False
    stripped = text.strip()
    return stripped in M.NEW_ORDER_BTN.values()


# ----- customer handlers ----------------------------------------------------

@customer_router.message(CommandStart())
async def on_start(msg: Message, storage: Storage, cfg: Config) -> None:
    user = msg.from_user
    if user is None:
        return
    storage.upsert_user(user.id, username=user.username, first_name=user.first_name)
    user_row = storage.get_user(user.id)
    assert user_row is not None
    lang = user_row["language"]

    # New user (never picked a language) → language picker only, no keyboard.
    # We detect "new" as: never completed an order AND no open order.
    has_history = storage.has_completed_order(user.id) or storage.get_open_order(user.id) is not None
    if not has_history:
        await msg.answer(M.PICK_LANGUAGE_PROMPT, reply_markup=keyboards.language_pick())
        return

    # Returning user → welcome with persistent main-menu keyboard.
    await msg.answer(
        M.WELCOME_RETURNING[lang],
        reply_markup=keyboards.main_menu_kb(lang),
    )


@customer_router.message(Command("til", "yazyk", "lang"))
async def on_lang_cmd(msg: Message) -> None:
    await msg.answer(M.PICK_LANGUAGE_PROMPT, reply_markup=keyboards.language_pick())


@customer_router.message(Command("help"))
async def on_help(msg: Message, storage: Storage) -> None:
    row = storage.get_user(msg.from_user.id) if msg.from_user else None
    lang = row["language"] if row else "uz"
    await msg.answer(M.HELP[lang], reply_markup=keyboards.main_menu_kb(lang))


@customer_router.callback_query(F.data.startswith("lang:"))
async def on_language_pick(cq: CallbackQuery, bot: Bot, storage: Storage, cfg: Config) -> None:
    if cq.from_user is None or cq.message is None:
        await cq.answer()
        return
    lang = cq.data.split(":", 1)[1]
    if lang not in {"uz", "ru"}:
        await cq.answer()
        return

    storage.upsert_user(cq.from_user.id, username=cq.from_user.username, first_name=cq.from_user.first_name)
    storage.set_user_language(cq.from_user.id, lang)

    # Replace the inline language picker with a compact confirmation, then
    # send the real welcome as a new message so we can attach the persistent
    # reply keyboard (which edit_text doesn't support).
    try:
        await cq.message.edit_text(M.LANGUAGE_CONFIRMED[lang])
    except Exception:  # noqa: BLE001
        pass

    returning = storage.has_completed_order(cq.from_user.id)
    welcome_text = (
        M.WELCOME_RETURNING[lang]
        if returning
        else M.WELCOME_FIRST_TIME[lang].format(store=html.escape(cfg.store_name))
    )
    await bot.send_message(
        cq.from_user.id,
        welcome_text,
        reply_markup=keyboards.main_menu_kb(lang),
    )
    await cq.answer()


@customer_router.message(F.location)
async def on_customer_location(msg: Message, bot: Bot, storage: Storage, cfg: Config) -> None:
    if msg.from_user is None or msg.location is None:
        return
    user_row = storage.upsert_user(msg.from_user.id, username=msg.from_user.username, first_name=msg.from_user.first_name)
    lang = user_row["language"]
    order = storage.get_open_order(msg.from_user.id)
    if order is None or order["status"] != "awaiting_address":
        # Not the right phase — ignore quietly. (Random location shares
        # shouldn't become order relay noise.)
        return

    storage.set_address(order["id"], lat=msg.location.latitude, lng=msg.location.longitude)
    storage.set_status(order["id"], "awaiting_amount")

    await bot.send_message(
        chat_id=cfg.ops_group_id,
        text=M.OPS_ADDRESS_RECEIVED_GEO.format(order_id=order["id"]),
    )
    await bot.send_location(
        chat_id=cfg.ops_group_id,
        latitude=msg.location.latitude,
        longitude=msg.location.longitude,
    )

    await msg.answer(
        M.ADDRESS_RECEIVED_WAIT_BILL[lang],
        reply_markup=keyboards.main_menu_kb(lang),
    )
    await _request_amount_from_merchant(order["id"], bot, cfg)


@customer_router.message(F.contact)
async def on_customer_contact(msg: Message, bot: Bot, storage: Storage, cfg: Config) -> None:
    if msg.from_user is None or msg.contact is None:
        return
    user_row = storage.upsert_user(msg.from_user.id, username=msg.from_user.username, first_name=msg.from_user.first_name)
    lang = user_row["language"]

    # Always cache the phone (future orders skip the ask)
    storage.set_user_phone(msg.from_user.id, msg.contact.phone_number)

    order = storage.get_open_order(msg.from_user.id)
    if order is None or order["status"] != "awaiting_phone":
        return  # not the right phase; phone is cached above and that's all we do

    storage.set_phone(order["id"], msg.contact.phone_number)
    storage.set_status(order["id"], "ready")

    await msg.answer(
        M.PHONE_RECEIVED[lang],
        reply_markup=keyboards.main_menu_kb(lang),
    )
    await _push_order_summary(order["id"], bot, storage, cfg)


@customer_router.message(F.text)
async def on_customer_text(msg: Message, bot: Bot, storage: Storage, cfg: Config) -> None:
    if msg.from_user is None or msg.text is None:
        return

    text = msg.text.strip()
    user_row = storage.upsert_user(msg.from_user.id, username=msg.from_user.username, first_name=msg.from_user.first_name)
    lang = user_row["language"]

    # 1. "🆕 New order" reply-keyboard tap — cancel any existing order,
    #    start a fresh one. Also acts as reset if user is stuck mid-flow.
    if is_new_order_button(text):
        existing = storage.get_open_order(msg.from_user.id)
        replaced = False
        if existing is not None:
            storage.set_status(existing["id"], "cancelled")
            replaced = True
            try:
                await bot.send_message(
                    cfg.ops_group_id,
                    M.OPS_CUSTOMER_RESET.format(order_id=existing["id"]),
                )
            except Exception:  # noqa: BLE001
                pass
        # Create a fresh open order for this user
        storage.open_or_get_order(msg.from_user.id)
        await msg.answer(
            M.NEW_ORDER_REPLACED[lang] if replaced else M.NEW_ORDER_STARTED[lang],
            reply_markup=keyboards.main_menu_kb(lang),
        )
        return

    order = storage.get_open_order(msg.from_user.id)

    # 2. Phase: awaiting an address (typed fallback for location)
    if order is not None and order["status"] == "awaiting_address":
        addr = text
        storage.set_address(order["id"], address=addr)
        storage.set_status(order["id"], "awaiting_amount")
        await bot.send_message(
            chat_id=cfg.ops_group_id,
            text=M.OPS_ADDRESS_RECEIVED_TEXT.format(order_id=order["id"], address=html.escape(addr)),
        )
        await msg.answer(
            M.ADDRESS_RECEIVED_WAIT_BILL[lang],
            reply_markup=keyboards.main_menu_kb(lang),
        )
        await _request_amount_from_merchant(order["id"], bot, cfg)
        return

    # 3. Phase: awaiting a phone (typed fallback for contact)
    if order is not None and order["status"] == "awaiting_phone":
        phone = re.sub(r"[^\d+]", "", text)
        if len(phone) < 7:
            await msg.answer(
                M.INVALID_INPUT_ASK_PHONE[lang],
                reply_markup=keyboards.request_contact_kb(lang),
            )
            return
        storage.set_user_phone(msg.from_user.id, phone)
        storage.set_phone(order["id"], phone)
        storage.set_status(order["id"], "ready")
        await msg.answer(
            M.PHONE_RECEIVED[lang],
            reply_markup=keyboards.main_menu_kb(lang),
        )
        await _push_order_summary(order["id"], bot, storage, cfg)
        return

    # 4. Conversation phase: relay to ops
    if order is not None and order["status"] in RELAY_STATUSES:
        await _relay_to_ops(msg, bot, storage, cfg, text=text)
        return

    # 5. No open order (or terminal state): nudge them to tap the button
    await msg.answer(
        M.TAP_TO_START[lang],
        reply_markup=keyboards.main_menu_kb(lang),
    )


async def _relay_to_ops(
    msg: Message,
    bot: Bot,
    storage: Storage,
    cfg: Config,
    *,
    text: str,
) -> None:
    """Mirror an in-order customer text to the ops group. Assumes an open
    order already exists (caller is responsible for that)."""
    user = msg.from_user
    assert user is not None
    user_row = storage.get_user(user.id)
    lang = user_row["language"] if user_row else "uz"

    order = storage.get_open_order(user.id)
    if order is None:
        return  # defensive; caller shouldn't hit this path

    is_first_message = order["status"] == "open"
    packing_done = order["status"] in POST_PACK_STATUSES

    header = M.OPS_NEW_MESSAGE.format(
        order_id=order["id"],
        user_label=html.escape(user_label(msg)),
        lang=lang_label(lang),
        text=html.escape(text),
    )
    if is_first_message:
        header = header + "\n\n" + M.OPS_NEW_ORDER_HINT

    await bot.send_message(
        chat_id=cfg.ops_group_id,
        text=header,
        reply_markup=keyboards.order_controls(order["id"], packing_done=packing_done),
    )

    if is_first_message:
        storage.set_status(order["id"], "in_conversation")


# ----- amount + bill helpers -----------------------------------------------

async def _request_amount_from_merchant(order_id: int, bot: Bot, cfg: Config) -> None:
    await bot.send_message(
        chat_id=cfg.ops_group_id,
        text=M.OPS_AMOUNT_PROMPT.format(
            order_id=order_id,
            delivery=fmt_sum(cfg.delivery_fee),
        ),
        reply_markup=ForceReply(input_field_placeholder="Masalan: 32000"),
    )


async def _send_bill_to_customer(order_id: int, bot: Bot, storage: Storage, cfg: Config) -> None:
    order = storage.get_order(order_id)
    if order is None or order["items_amount"] is None:
        return
    user = storage.get_user(order["customer_tg_id"])
    if user is None:
        return
    lang = user["language"]
    items = order["items_amount"]
    delivery = cfg.delivery_fee
    total = items + delivery

    await bot.send_message(
        chat_id=order["customer_tg_id"],
        text=M.BILL_TEMPLATE[lang].format(
            order_id=order_id,
            items=fmt_sum(items),
            delivery=fmt_sum(delivery),
            total=fmt_sum(total),
        ),
        reply_markup=keyboards.payment_method_kb(
            order_id, lang, include_transfer=cfg.transfer_enabled
        ),
    )


async def _push_order_summary(order_id: int, bot: Bot, storage: Storage, cfg: Config) -> None:
    order = storage.get_order(order_id)
    if order is None:
        return
    user = storage.get_user(order["customer_tg_id"])
    address = order["address"] or (
        f"{order['location_lat']:.5f},{order['location_lng']:.5f}"
        if order["location_lat"] and order["location_lng"]
        else "—"
    )
    raw_label = ("@" + user["username"]) if user and user["username"] else (user["first_name"] if user else "—")
    items = order["items_amount"] or 0
    total = items + (cfg.delivery_fee if items else 0)
    text = M.OPS_ORDER_SUMMARY.format(
        order_id=order["id"],
        user_label=html.escape(raw_label or "—"),
        lang=lang_label(user["language"] if user else "uz"),
        address=html.escape(address),
        phone=html.escape(order["phone"] or "—"),
        items=fmt_sum(items) if items else "—",
        delivery=fmt_sum(cfg.delivery_fee),
        total=fmt_sum(total) if items else "—",
        method=html.escape(payment_method_label(order["payment_method"])),
    )
    await bot.send_message(
        chat_id=cfg.ops_group_id,
        text=text,
        reply_markup=keyboards.order_controls(order["id"], packing_done=True),
    )


# ----- ops-group handlers ---------------------------------------------------

@ops_router.message(Command("orders"))
async def on_ops_orders(msg: Message, storage: Storage) -> None:
    rows = storage.list_open_orders()
    if not rows:
        await msg.reply(M.OPS_OPEN_ORDERS_EMPTY)
        return
    lines = [M.OPS_OPEN_ORDERS_HEADER]
    for r in rows:
        lbl = ("@" + r["username"]) if r["username"] else (r["first_name"] or f"id:{r['customer_tg_id']}")
        lines.append(M.OPS_OPEN_ORDER_ROW.format(
            order_id=r["id"], user_label=html.escape(lbl), status=html.escape(r["status"])
        ))
    await msg.reply("\n".join(lines))


@ops_router.message(Command("help"))
async def on_ops_help(msg: Message) -> None:
    await msg.reply(M.OPS_HELP)


@ops_router.callback_query(F.data.startswith("act:"))
async def on_ops_action(cq: CallbackQuery, bot: Bot, storage: Storage, cfg: Config) -> None:
    if cq.data is None or cq.message is None:
        await cq.answer()
        return

    if cfg.merchant_ids and cq.from_user and cq.from_user.id not in cfg.merchant_ids:
        await cq.answer("Faqat sotuvchi bosishi mumkin.", show_alert=True)
        return

    try:
        action, order_id = parse_callback(cq.data)
    except ValueError:
        await cq.answer()
        return

    order = storage.get_order(order_id)
    if order is None:
        await cq.answer("Buyurtma topilmadi.", show_alert=True)
        return

    user = storage.get_user(order["customer_tg_id"])
    if user is None:
        await cq.answer("Mijoz topilmadi.", show_alert=True)
        return
    lang = user["language"]

    if action == "accept":
        storage.set_status(order_id, "accepted")
        await bot.send_message(
            order["customer_tg_id"],
            M.ORDER_ACCEPTED[lang],
            reply_markup=keyboards.main_menu_kb(lang),
        )
        await cq.answer("Yuborildi ✅")

    elif action == "reply":
        await bot.send_message(
            chat_id=cfg.ops_group_id,
            text=M.OPS_REPLY_PROMPT.format(order_id=order_id),
            reply_to_message_id=cq.message.message_id,
            reply_markup=ForceReply(input_field_placeholder="Mijozga javob..."),
        )
        await cq.answer("Yozavering 👇")

    elif action == "pack":
        storage.set_status(order_id, "awaiting_address")
        await bot.send_message(
            order["customer_tg_id"],
            M.ORDER_PACKING_ASK_ADDRESS[lang],
            reply_markup=keyboards.request_location_kb(lang),
        )
        try:
            await cq.message.edit_reply_markup(
                reply_markup=keyboards.order_controls(order_id, packing_done=True)
            )
        except Exception:  # noqa: BLE001
            pass
        await cq.answer("Mijozdan manzil so'raldi 📍")

    elif action == "enroute":
        storage.set_status(order_id, "enroute")
        await bot.send_message(
            order["customer_tg_id"],
            M.ORDER_ENROUTE[lang],
            reply_markup=keyboards.main_menu_kb(lang),
        )
        await cq.answer("Yuborildi 🚴")

    elif action == "delivered":
        storage.set_status(order_id, "delivered")
        await bot.send_message(
            order["customer_tg_id"],
            M.ORDER_DELIVERED[lang],
            reply_markup=keyboards.main_menu_kb(lang),
        )
        await cq.answer("Yopildi ✅")

    elif action == "cancel":
        storage.set_status(order_id, "cancelled")
        await bot.send_message(
            order["customer_tg_id"],
            M.ORDER_CANCELLED[lang],
            reply_markup=keyboards.main_menu_kb(lang),
        )
        await cq.answer("Bekor qilindi.")

    else:
        await cq.answer()


@customer_router.callback_query(F.data.startswith("pay:"))
async def on_customer_payment_pick(cq: CallbackQuery, bot: Bot, storage: Storage, cfg: Config) -> None:
    if cq.data is None or cq.message is None or cq.from_user is None:
        await cq.answer()
        return
    try:
        _, method, order_id_s = cq.data.split(":", 2)
        order_id = int(order_id_s)
    except ValueError:
        await cq.answer()
        return
    if method not in {"cash", "transfer"}:
        await cq.answer()
        return

    order = storage.get_order(order_id)
    if order is None or order["customer_tg_id"] != cq.from_user.id:
        await cq.answer("Buyurtma topilmadi.", show_alert=True)
        return
    user = storage.get_user(order["customer_tg_id"])
    if user is None:
        await cq.answer()
        return
    lang = user["language"]

    if method == "transfer" and not cfg.transfer_enabled:
        await cq.answer(M.PAYMENT_TRANSFER_UNAVAILABLE[lang], show_alert=True)
        return

    storage.set_payment_method(order_id, method)
    storage.set_status(order_id, "awaiting_phone")

    items = order["items_amount"] or 0
    total = items + cfg.delivery_fee

    bill_done_template = (
        M.BILL_TEMPLATE_CASH_PICKED if method == "cash" else M.BILL_TEMPLATE_TRANSFER_PICKED
    )
    try:
        await cq.message.edit_text(
            bill_done_template[lang].format(
                order_id=order_id,
                items=fmt_sum(items),
                delivery=fmt_sum(cfg.delivery_fee),
                total=fmt_sum(total),
            )
        )
    except Exception:  # noqa: BLE001
        pass

    if method == "cash":
        await bot.send_message(
            order["customer_tg_id"],
            M.PAYMENT_CASH_NEXT[lang],
            reply_markup=keyboards.request_contact_kb(lang),
        )
    else:
        await bot.send_message(
            order["customer_tg_id"],
            M.PAYMENT_TRANSFER_INSTRUCTIONS[lang].format(
                card=html.escape(cfg.transfer_card),
                holder=html.escape(cfg.transfer_holder),
                total=fmt_sum(total),
            ),
            reply_markup=keyboards.request_contact_kb(lang),
        )

    await bot.send_message(
        cfg.ops_group_id,
        M.OPS_PAYMENT_PICKED.format(
            order_id=order_id,
            method=html.escape(payment_method_label(method)),
        ),
    )
    await cq.answer("✓")


@ops_router.message(F.reply_to_message)
async def on_ops_reply(msg: Message, bot: Bot, storage: Storage, cfg: Config) -> None:
    """Two cases:
        (a) Merchant replied to an "amount prompt" -> parse as items amount,
            send bill to customer.
        (b) Otherwise -> forward as free-text custom reply to the customer.
    """
    if msg.text is None or not msg.text.strip():
        return
    if cfg.merchant_ids and msg.from_user and msg.from_user.id not in cfg.merchant_ids:
        return

    parent = msg.reply_to_message
    if parent is None:
        return
    parent_text = parent.text or parent.caption
    order_id = extract_order_id(parent_text)
    if order_id is None:
        return

    order = storage.get_order(order_id)
    if order is None:
        return

    is_amount_prompt = bool(parent_text and AMOUNT_PROMPT_MARKER in parent_text.lower())
    if is_amount_prompt and order["status"] == "awaiting_amount":
        try:
            amount = parse_amount(msg.text)
        except ValueError:
            await msg.reply(M.OPS_AMOUNT_INVALID)
            return
        storage.set_items_amount(order_id, amount)
        storage.set_status(order_id, "awaiting_payment_method")
        total = amount + cfg.delivery_fee
        await msg.reply(M.OPS_AMOUNT_RECEIVED.format(
            order_id=order_id,
            items=fmt_sum(amount),
            total=fmt_sum(total),
        ))
        await _send_bill_to_customer(order_id, bot, storage, cfg)
        return

    user = storage.get_user(order["customer_tg_id"])
    if user is None:
        return
    lang = user["language"]
    forwarded = f"{M.CUSTOM_REPLY_PREFIX[lang]} {html.escape(msg.text.strip())}"
    await bot.send_message(order["customer_tg_id"], forwarded)
    try:
        await msg.reply(M.OPS_RELAY_CONFIRMED.format(preview=html.escape(truncate(msg.text))))
    except Exception:  # noqa: BLE001
        pass


# ----- bootstrap ------------------------------------------------------------

async def _main() -> None:
    cfg = Config.from_env()
    storage = Storage(cfg.db_path)
    log.info("Storage initialised at %s", cfg.db_path)

    bot = Bot(token=cfg.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp["storage"] = storage
    dp["cfg"] = cfg

    customer_router.message.filter(F.chat.type == ChatType.PRIVATE)
    customer_router.callback_query.filter(F.message.chat.type == ChatType.PRIVATE)

    ops_router.message.filter(F.chat.id == cfg.ops_group_id)
    ops_router.callback_query.filter(F.message.chat.id == cfg.ops_group_id)

    dp.include_router(customer_router)
    dp.include_router(ops_router)

    me = await bot.get_me()
    log.info("Bot @%s ready. Ops group: %s. Store: %s.", me.username, cfg.ops_group_id, cfg.store_name)
    await bot.delete_webhook(drop_pending_updates=False)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


def main() -> None:
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        log.info("Bye.")
        sys.exit(0)


if __name__ == "__main__":
    main()
