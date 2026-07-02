# Emir Market — Concierge Bot (UchQadam v0.1)

Single-file Telegram bot for the UchQadam validation experiment.

- Customers DM the bot in Uzbek or Russian.
- Each customer message is mirrored to a private "Emir Market — Ops" Telegram group with order-control buttons.
- The merchant taps a button to send a canonical message back, or replies to the ops message (Telegram's native reply) to send custom text.
- All state lives in a local SQLite file. No external services required.

## Prerequisites

- Python 3.11+
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- A private Telegram group to use as the ops channel, with the bot added as a **member**

## First-time setup

```bash
cd ~/Claude/Projects/UchQadam/bot

# create + activate a virtualenv (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate

# install deps
pip install -r requirements.txt

# copy the env template and fill in real values
cp .env.example .env
$EDITOR .env
```

You need two values in `.env`:

1. **`BOT_TOKEN`** — from @BotFather. Send `/newbot` to BotFather, give it a name (e.g. "Emir Market Yetkazib Berish") and a username ending in `bot`. Paste the token it gives you.
2. **`OPS_GROUP_ID`** — the chat ID of your private ops group. To find it:
   - Create a private group ("Emir Market — Ops"). Add yourself, the merchant, and the bot.
   - In the group, send `/start@<your_bot_username>` (won't do anything useful yet).
   - Either: temporarily add [@RawDataBot](https://t.me/RawDataBot) to the group, send any message, look for `"chat":{"id": -1001234567890}` — that negative integer is the ID. Remove @RawDataBot after.
   - Or: run the bot once, then run `tail -f` on your terminal; any message sent to the group will print an update where you can read the chat ID.

Optionally:
- `MERCHANT_IDS` — comma-separated Telegram user IDs allowed to press order-control buttons. Leave empty during testing.
- `STORE_NAME` — display name shown in welcome messages. Defaults to "Emir Market".
- `DELIVERY_FEE` — added to every bill (in sum, integer). Defaults to `5000`.
- `TRANSFER_CARD` / `TRANSFER_HOLDER` — card details shown when a customer picks "Transfer" at payment time. Leave both blank to only accept cash; the transfer button will be hidden.

## Run

```bash
python main.py
```

You should see something like:

```
12:34:56 INFO bot :: Storage initialised at .../bot/uchqadam.db
12:34:57 INFO bot :: Bot @emirmarketbot ready. Ops group: -1001234567890. Store: Emir Market.
```

Send `/start` to the bot in DM as a test customer. Then send a free-text message ("salom, non bormi"). It should appear in the ops group with action buttons underneath.

## Customer flow

1. `/start` → language picker (Uz / Ru), then a welcome message with a persistent **🆕 Yangi buyurtma** / **🆕 Новый заказ** reply-keyboard button.
2. Customer must **tap the button** to start an order. Random text before that gets a gentle "tap the button to begin" nudge — no phantom orders. Tapping the button while an order is already open cancels that order and starts fresh (it's the reset too).
3. Once the order is open, free-text DMs ("non bormi?") → mirrored to the ops group with action buttons.
4. Conversation continues: merchant taps **💬 Javob yozish** to write custom replies, or **✅ Qabul qilindi** when the basket is firmed up.
5. When merchant taps **📦 Yig'ishni boshlayman**, the bot asks the customer for an address (geolocation button + text fallback — including `pod'yezd` / `подъезд`).
6. After the address arrives, the bot ForceReply-prompts the merchant in the ops group for the items amount.
7. Merchant types the amount (e.g. `32000`) → bot calculates total (items + delivery fee) and sends the customer a bill with **💵 Naqd** / **💳 O'tkazma** buttons.
8. Customer picks a payment method:
    - **Cash**: bot asks for phone via the contact-share button.
    - **Transfer**: bot shows the configured card details + asks for phone (customer is expected to send a payment screenshot in chat).
9. Phone captured → final summary lands in the ops group with **🚴 Yo'lda** / **✅ Yetkazildi** controls.

## Merchant operating notes

- Every customer message becomes a new "Order #N" post in the ops group.
- All posts referencing the same order share an `Order #N` tag — that's how the bot routes your replies.
- The four primary buttons on each customer message:
  - **✅ Qabul qilindi** — the line items are confirmed, conversation continues
  - **💬 Javob yozish** — opens a ForceReply prompt so you can type a free-text response (explain stockouts, propose alternatives, answer questions)
  - **📦 Yig'ishni boshlayman** — triggers the address → bill → payment → phone flow
  - **🚫 Bekor qilish** — closes the order
- To send a free-text reply, either tap **💬 Javob yozish** OR use Telegram's native "Reply" gesture on any bot ops post and type. The customer will see `👨‍🍳 Sotuvchidan: <your text>`.
- After the customer sends the address, the bot will ask you in the ops group for the items amount. Just type the number (e.g. `32000`) and send. The bot auto-adds the delivery fee and sends a bill to the customer.
- `/orders` in the ops group shows all currently open orders.
- `/help` in the ops group shows the action cheatsheet.

## Storage

A single SQLite file (`uchqadam.db` by default) holds:

- `users` — telegram ID, username, language preference, saved phone
- `orders` — one row per order with status, address, phone, items amount, payment method, timestamps

Order status lifecycle: `open` → `in_conversation` → `accepted` → `awaiting_address` → `awaiting_amount` → `awaiting_payment_method` → `awaiting_phone` → `ready` → `enroute` → `delivered` (or `cancelled` at any point; also `cancelled` when the customer taps 🆕 Yangi buyurtma to reset).

The file is gitignored. Back it up by copying it; restore by replacing it.

## Known limitations (v0.1)

- No catalog / no structured cart. This is intentional — we're testing free-text concierge demand first.
- ETA on "Yo'lda" is a fixed phrase ("tez orada"). Add a quick keyboard with `[10] [15] [20] [30]` after first ~20 orders.
- No automatic order-summary line items. The merchant compiles the bag mentally from the conversation. This is fine at <10 orders/day.
- One open order per customer at a time. If you need parallel orders (e.g. same household, different recipients), use a second Telegram account for now.
- Polling mode only. For production, switch to webhooks behind a reverse proxy.

## Where to add the next bits

| When you want… | Touch |
|---|---|
| New customer-facing message | `messages.py` |
| New ops-group button | `keyboards.py::order_controls` + handler in `main.py::on_ops_action` |
| New customer flow phase | add a status to `storage.OPEN_STATUSES`, branch in `on_customer_text` |
| Catalog / cart | new `catalog.py` + new handler tree; keep free-text path as fallback |
| Click/Payme payment | new module + new "Yo'lda" handler that triggers a payment intent before delivery |
