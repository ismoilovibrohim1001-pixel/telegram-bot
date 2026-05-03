import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)

# ===================== SOZLAMALAR =====================
TOKEN = "8681976127:AAFl_mAsRXXQ3K8J-5t6HHvaSopYPN4cvFI"
ADMIN_ID = None  # Admin Telegram ID sini kiriting, masalan: 123456789

# ===================== BOT VA DISPATCHER =====================
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ===================== MA'LUMOTLAR =====================
# { id: { title, description, price, category, phone, user_id, username } }
ads = {}
ad_counter = 0

CATEGORIES = ["📱 Elektronika", "🚗 Avtomobil", "🏠 Uy-joy", "👗 Kiyim", "🛋 Mebel", "💼 Ish", "📚 Kitoblar", "🔧 Boshqa"]

# ===================== HOLATLAR =====================
class PostAd(StatesGroup):
    title = State()
    description = State()
    price = State()
    category = State()
    phone = State()

class SearchAd(StatesGroup):
    query = State()

# ===================== KLAVIATURALAR =====================
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ E'lon joylash"), KeyboardButton(text="🔍 Qidirish")],
            [KeyboardButton(text="📋 Barcha e'lonlar"), KeyboardButton(text="👤 Mening e'lonlarim")],
        ],
        resize_keyboard=True
    )

def category_keyboard():
    buttons = [[KeyboardButton(text=cat)] for cat in CATEGORIES]
    buttons.append([KeyboardButton(text="🔙 Orqaga")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# ===================== START =====================
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        f"👋 Salom, {message.from_user.first_name}!\n\n"
        "🛒 *Savdo Marketplace* botiga xush kelibsiz!\n\n"
        "Bu yerda siz:\n"
        "✅ E'lon joylashingiz\n"
        "✅ Mahsulot qidirishingiz\n"
        "✅ Sotuvchilar bilan bog'lanishingiz mumkin!\n\n"
        "Quyidagi menyudan tanlang 👇",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

# ===================== E'LON JOYLASH =====================
@dp.message(F.text == "➕ E'lon joylash")
async def post_ad_start(message: types.Message, state: FSMContext):
    await state.set_state(PostAd.title)
    await message.answer(
        "📝 *E'lon joylash*\n\n"
        "1-qadam: Mahsulot nomini kiriting:\n"
        "_(Masalan: iPhone 13 Pro)_",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🔙 Orqaga")]],
            resize_keyboard=True
        )
    )

@dp.message(PostAd.title)
async def post_ad_title(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await state.clear()
        await message.answer("Bosh menyu:", reply_markup=main_menu())
        return
    await state.update_data(title=message.text)
    await state.set_state(PostAd.description)
    await message.answer(
        "2-qadam: Tavsif kiriting:\n"
        "_(Mahsulot holati, xususiyatlari haqida yozing)_",
        parse_mode="Markdown"
    )

@dp.message(PostAd.description)
async def post_ad_description(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await state.clear()
        await message.answer("Bosh menyu:", reply_markup=main_menu())
        return
    await state.update_data(description=message.text)
    await state.set_state(PostAd.price)
    await message.answer(
        "3-qadam: Narxini kiriting:\n"
        "_(Masalan: 500000 so'm yoki Kelishiladi)_",
        parse_mode="Markdown"
    )

@dp.message(PostAd.price)
async def post_ad_price(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await state.clear()
        await message.answer("Bosh menyu:", reply_markup=main_menu())
        return
    await state.update_data(price=message.text)
    await state.set_state(PostAd.category)
    await message.answer(
        "4-qadam: Kategoriyani tanlang 👇",
        reply_markup=category_keyboard()
    )

@dp.message(PostAd.category)
async def post_ad_category(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await state.clear()
        await message.answer("Bosh menyu:", reply_markup=main_menu())
        return
    if message.text not in CATEGORIES:
        await message.answer("Iltimos, kategoriyani tanlang 👇", reply_markup=category_keyboard())
        return
    await state.update_data(category=message.text)
    await state.set_state(PostAd.phone)
    await message.answer(
        "5-qadam: Telefon raqamingizni kiriting:\n"
        "_(Masalan: +998901234567)_",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📱 Raqamni ulashish", request_contact=True)],
                [KeyboardButton(text="🔙 Orqaga")]
            ],
            resize_keyboard=True
        )
    )

@dp.message(PostAd.phone)
async def post_ad_phone(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await state.clear()
        await message.answer("Bosh menyu:", reply_markup=main_menu())
        return

    global ad_counter
    phone = message.contact.phone_number if message.contact else message.text

    data = await state.get_data()
    ad_counter += 1
    ads[ad_counter] = {
        "id": ad_counter,
        "title": data["title"],
        "description": data["description"],
        "price": data["price"],
        "category": data["category"],
        "phone": phone,
        "user_id": message.from_user.id,
        "username": message.from_user.username or message.from_user.first_name
    }

    await state.clear()
    await message.answer(
        f"✅ *E'loningiz joylandi!*\n\n"
        f"🆔 E'lon №{ad_counter}\n"
        f"📦 *{data['title']}*\n"
        f"💰 Narx: {data['price']}\n"
        f"📁 Kategoriya: {data['category']}\n\n"
        f"E'loningiz barcha foydalanuvchilarga ko'rinadi!",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

# ===================== BARCHA E'LONLAR =====================
@dp.message(F.text == "📋 Barcha e'lonlar")
async def all_ads(message: types.Message):
    if not ads:
        await message.answer("😔 Hozircha e'lonlar yo'q.\nBirinchi bo'lib e'lon joylang!", reply_markup=main_menu())
        return

    await message.answer(f"📋 *Jami {len(ads)} ta e'lon:*", parse_mode="Markdown")

    for ad_id, ad in list(ads.items())[-10:]:  # Oxirgi 10 ta
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📞 Bog'lanish", callback_data=f"contact_{ad_id}")]
        ])
        await message.answer(
            f"🆔 *E'lon №{ad['id']}*\n"
            f"📦 *{ad['title']}*\n"
            f"📝 {ad['description']}\n"
            f"💰 *Narx: {ad['price']}*\n"
            f"📁 {ad['category']}\n"
            f"👤 Sotuvchi: @{ad['username']}",
            parse_mode="Markdown",
            reply_markup=kb
        )

# ===================== QIDIRISH =====================
@dp.message(F.text == "🔍 Qidirish")
async def search_start(message: types.Message, state: FSMContext):
    await state.set_state(SearchAd.query)
    await message.answer(
        "🔍 Qidirish uchun kalit so'z kiriting:\n"
        "_(Masalan: iPhone, Toyota, Shkaf...)_",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🔙 Orqaga")]],
            resize_keyboard=True
        )
    )

@dp.message(SearchAd.query)
async def search_ads(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await state.clear()
        await message.answer("Bosh menyu:", reply_markup=main_menu())
        return

    query = message.text.lower()
    results = [
        ad for ad in ads.values()
        if query in ad["title"].lower() or query in ad["description"].lower()
    ]

    await state.clear()

    if not results:
        await message.answer(
            f"😔 *'{message.text}'* bo'yicha e'lon topilmadi.\nBoshqa so'z bilan qidiring.",
            parse_mode="Markdown",
            reply_markup=main_menu()
        )
        return

    await message.answer(f"🔍 *{len(results)} ta natija topildi:*", parse_mode="Markdown", reply_markup=main_menu())

    for ad in results:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📞 Bog'lanish", callback_data=f"contact_{ad['id']}")]
        ])
        await message.answer(
            f"🆔 *E'lon №{ad['id']}*\n"
            f"📦 *{ad['title']}*\n"
            f"📝 {ad['description']}\n"
            f"💰 *Narx: {ad['price']}*\n"
            f"📁 {ad['category']}\n"
            f"👤 Sotuvchi: @{ad['username']}",
            parse_mode="Markdown",
            reply_markup=kb
        )

# ===================== MENING E'LONLARIM =====================
@dp.message(F.text == "👤 Mening e'lonlarim")
async def my_ads(message: types.Message):
    my = [ad for ad in ads.values() if ad["user_id"] == message.from_user.id]

    if not my:
        await message.answer("😔 Sizda hozircha e'lon yo'q.\n➕ E'lon joylash tugmasini bosing!", reply_markup=main_menu())
        return

    await message.answer(f"👤 *Sizning e'lonlaringiz ({len(my)} ta):*", parse_mode="Markdown")

    for ad in my:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"delete_{ad['id']}")]
        ])
        await message.answer(
            f"🆔 *E'lon №{ad['id']}*\n"
            f"📦 *{ad['title']}*\n"
            f"💰 Narx: {ad['price']}\n"
            f"📁 {ad['category']}",
            parse_mode="Markdown",
            reply_markup=kb
        )

# ===================== CALLBACK =====================
@dp.callback_query(F.data.startswith("contact_"))
async def contact_seller(callback: types.CallbackQuery):
    ad_id = int(callback.data.split("_")[1])
    ad = ads.get(ad_id)

    if not ad:
        await callback.answer("E'lon topilmadi!", show_alert=True)
        return

    if ad["user_id"] == callback.from_user.id:
        await callback.answer("Bu sizning e'loningiz!", show_alert=True)
        return

    await callback.message.answer(
        f"📞 *Sotuvchi bilan bog'lanish:*\n\n"
        f"📦 Mahsulot: *{ad['title']}*\n"
        f"👤 Sotuvchi: @{ad['username']}\n"
        f"📱 Telefon: `{ad['phone']}`\n\n"
        f"Sotuvchiga to'g'ridan-to'g'ri murojaat qiling!",
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("delete_"))
async def delete_ad(callback: types.CallbackQuery):
    ad_id = int(callback.data.split("_")[1])
    ad = ads.get(ad_id)

    if not ad:
        await callback.answer("E'lon topilmadi!", show_alert=True)
        return

    if ad["user_id"] != callback.from_user.id:
        await callback.answer("Bu sizning e'loningiz emas!", show_alert=True)
        return

    del ads[ad_id]
    await callback.message.edit_text(f"🗑 *E'lon №{ad_id} o'chirildi!*", parse_mode="Markdown")
    await callback.answer("O'chirildi!")

# ===================== ISHGA TUSHIRISH =====================
async def main():
    logging.basicConfig(level=logging.INFO)
    print("🤖 Savdo Marketplace boti ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())