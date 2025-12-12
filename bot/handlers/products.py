"""
Product Management Handlers
Handles product addition conversation flow
"""

import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from ..config import ADMIN_IDS
from ..constants import NAME, DESCRIPTION, PRICE, IMAGE, CATEGORY, INGREDIENTS, CONFIRM
from ..constants import EDIT_SELECT_PRODUCT, EDIT_SELECT_FIELD, EDIT_NEW_VALUE, EDIT_CONFIRM

# Import from root database module
from database import add_product, get_all_products, edit_product


async def add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Start product addition conversation
    Entry point for adding a new product
    """
    print("🔵 add_product_start CALLED!")
    print(f"   Update type: {update.update_id}")
    print(f"   User: {update.effective_user.id if update.effective_user else 'None'}")

    query = update.callback_query if update.callback_query else None

    if query:
        print(f"   Callback data: {query.data}")
        await query.answer()

        if query.from_user.id not in ADMIN_IDS:
            print("   ❌ Not admin")
            await query.edit_message_text("❌ Только для администраторов")
            return ConversationHandler.END

        message = query.message
    else:
        print(f"   Command message")
        if update.effective_user.id not in ADMIN_IDS:
            print("   ❌ Not admin")
            return ConversationHandler.END
        message = update.message

    # Initialize data
    context.user_data['new_product'] = {}

    response_text = (
        "📦 *Добавление нового продукта*\n\n"
        "Шаг 1 из 6\n\n"
        "*Введите название продукта:*\n\n"
        "Например: _Бургер Классический_\n\n"
        "Или /cancel - для отмены"
    )

    print(f"   ✅ Sending response and returning NAME state")

    await message.reply_text(response_text, parse_mode='HTML')

    return NAME


async def product_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle product name input (Step 1)
    """
    name = update.message.text.strip()

    if len(name) < 3:
        await update.message.reply_text(
            "❌ Название слишком короткое!\n\n"
            "Введите название минимум из 3 символов:"
        )
        return NAME

    context.user_data['new_product']['name'] = name

    await update.message.reply_text(
        f"✅ Название: <b>{name}</b>\n\n"
        "Шаг 2 из 6\n"
        "Введите <b>описание блюда</b>:\n\n"
        "✏️ Например: Сочные пельмени с говядиной и свининой, как в России\n\n"
        "💡 <i>Совет: Опишите вкус, состав и особенности блюда</i>",
        parse_mode='HTML'
    )

    return DESCRIPTION


async def product_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle product description input (Step 2)
    """
    description = update.message.text.strip()

    if len(description) < 10:
        await update.message.reply_text(
            "❌ Описание слишком короткое!\n\n"
            "Введите описание минимум из 10 символов:"
        )
        return DESCRIPTION

    context.user_data['new_product']['description'] = description

    await update.message.reply_text(
        "✅ Описание сохранено\n\n"
        "Шаг 3 из 6\n"
        "Введите <b>цену в AED</b> (только число):\n\n"
        "✏️ Например: 25 или 35.5",
        parse_mode='HTML'
    )

    return PRICE


async def product_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle product price input (Step 3)
    """
    try:
        price_text = update.message.text.strip().replace(',', '.')
        price = float(price_text)
        if price <= 0:
            raise ValueError("Price must be positive")

        context.user_data['new_product']['price'] = price

        await update.message.reply_text(
            f"✅ Цена: <b>{price} AED</b>\n\n"
            "Шаг 4 из 6\n"
            "Отправьте <b>ссылку на изображение блюда</b>:\n\n"
            "💡 <b>Совет:</b> Используйте Unsplash для качественных фото еды:\n"
            "1. Перейдите на unsplash.com\n"
            "2. Найдите подходящее фото\n"
            "3. Скопируйте ссылку на изображение\n\n"
            "Пример: https://images.unsplash.com/photo-1234567890?w=300",
            parse_mode='HTML'
        )

        return IMAGE

    except ValueError:
        await update.message.reply_text(
            "❌ <b>Неверный формат цены!</b>\n\n"
            "Введите число (целое или десятичное):\n"
            "✅ Правильно: 25 или 35.5 или 42,90\n"
            "❌ Неправильно: 25AED, двадцать пять\n\n"
            "Попробуйте еще раз:",
            parse_mode='HTML'
        )
        return PRICE


async def product_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle product image URL input (Step 4)
    """
    image_url = update.message.text.strip()

    # Simple URL validation
    if not (image_url.startswith('http://') or image_url.startswith('https://')):
        await update.message.reply_text(
            "❌ Пожалуйста, отправьте полную ссылку, начинающуюся с http:// или https://\n\n"
            "Попробуйте еще раз:"
        )
        return IMAGE

    context.user_data['new_product']['image'] = image_url

    # Send image preview
    try:
        await update.message.reply_photo(
            photo=image_url,
            caption="✅ Изображение загружено успешно!"
        )
    except Exception as e:
        await update.message.reply_text(
            f"⚠️ Не удалось загрузить изображение по ссылке.\n"
            f"Ошибка: {str(e)[:100]}\n\n"
            f"Но ссылка сохранена. Проверьте её корректность.\n"
            f"Хотите продолжить или ввести другую ссылку?\n\n"
            f"Отправьте новую ссылку или /continue для продолжения"
        )
        return IMAGE

    keyboard = [
        [InlineKeyboardButton("🍔 Бургеры", callback_data="cat_burger")],
        [InlineKeyboardButton("🍕 Пицца", callback_data="cat_pizza")],
        [InlineKeyboardButton("🍚 Плов", callback_data="cat_plov")],
        [InlineKeyboardButton("🍲 Супы", callback_data="cat_soup")],
        [InlineKeyboardButton("🥟 Пельмени", callback_data="cat_pelmeni")],
        [InlineKeyboardButton("🥖 Хачапури", callback_data="cat_khachapuri")],
        [InlineKeyboardButton("🍰 Десерты", callback_data="cat_dessert")],
        [InlineKeyboardButton("🥗 Закуски", callback_data="cat_salad")],
        [InlineKeyboardButton("🥤 Напитки", callback_data="cat_drinks")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Шаг 5 из 6\n"
        "Выберите <b>категорию блюда</b>:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

    return CATEGORY


async def product_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle category selection (Step 6)
    """
    query = update.callback_query
    await query.answer()

    category = query.data.replace('cat_', '')
    context.user_data['new_product']['category'] = category

    await query.edit_message_text(
        f"✅ Категория: <b>{category}</b>\n\n"
        "Шаг 6 из 6\n"
        "Введите <b>ингредиенты</b> через запятую:\n\n"
        "Например: Мука, Яйцо, Говядина, Свинина, Лук, Соль, Перец",
        parse_mode='HTML'
    )

    return INGREDIENTS


async def product_ingredients(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle ingredients input (Step 7 - final step)
    Shows preview and confirmation
    """
    text = update.message.text.strip()

    # Check for skip command
    if text == '/skip':
        ingredients_list = []
        context.user_data['new_product']['ingredients'] = json.dumps([], ensure_ascii=False)
    else:
        ingredients_str = text
        ingredients_list = [ing.strip() for ing in ingredients_str.split(',') if ing.strip()]

        if not ingredients_list:
            await update.message.reply_text(
                "❌ Пожалуйста, введите хотя бы один ингредиент\n"
                "Или отправьте /skip чтобы пропустить"
            )
            return INGREDIENTS

        context.user_data['new_product']['ingredients'] = json.dumps(ingredients_list, ensure_ascii=False)

    # Format preview
    product = context.user_data['new_product']

    # Send image with preview
    preview_text = f"""
📋 <b>ПРЕДПРОСМОТР БЛЮДА</b>

🍽️ <b>Название:</b> {product['name']}
📝 <b>Описание:</b> {product['description']}
💰 <b>Цена:</b> {product['price']} AED
📂 <b>Категория:</b> {product['category']}
"""

    if ingredients_list:
        preview_text += f"🥘 <b>Ингредиенты:</b> {', '.join(ingredients_list[:8])}{'...' if len(ingredients_list) > 8 else ''}\n"

    preview_text += "\n<b>Всё верно? Сохранить блюдо?</b>"

    keyboard = [
        [InlineKeyboardButton("✅ Да, сохранить", callback_data="saveproduct")],
        [InlineKeyboardButton("❌ Отменить", callback_data="cancel_product")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Try to send with image
    try:
        await update.message.reply_photo(
            photo=product['image'],
            caption=preview_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    except Exception:
        # If failed - send without image
        await update.message.reply_text(
            preview_text + f"\n\n⚠️ Изображение: {product['image'][:50]}...",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )

    return CONFIRM


async def saveproduct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Save the product to database
    Called when user confirms product creation
    """
    query = update.callback_query
    await query.answer()

    product = context.user_data.get('new_product')
    if not product:
        await query.edit_message_caption(
            caption="❌ *Ошибка*\n\n/start",
            parse_mode='HTML'
        )
        return ConversationHandler.END

    try:
        # Extract data
        ingredients_str = product.get('ingredients', '[]')
        ingredients_list = json.loads(ingredients_str) if isinstance(ingredients_str, str) else ingredients_str

        # Add product via database adapter
        new_id = add_product(
            name=product['name'],
            description=product['description'],
            price=product['price'],
            image=product['image'],
            category=product['category'],
            ingredients=product['ingredients']
        )

        success_message = f"""✅ *Продукт добавлен!*

📦 ID: {new_id}
📝 {product['name']}
💰 {product['price']} AED
🏷 {product['category']}

⚡ Изменения сохранены в базе данных!
➡️ Проверьте мини-приложение.
"""

        try:
            await query.edit_message_caption(caption=success_message, parse_mode='HTML')
        except Exception:
            await query.message.reply_text(success_message, parse_mode='HTML')

    except Exception as e:
        error_message = f"❌ *Ошибка*\n\n{str(e)}\n\n/start"
        try:
            await query.edit_message_caption(caption=error_message, parse_mode='HTML')
        except Exception:
            await query.message.reply_text(error_message, parse_mode='HTML')
    finally:
        context.user_data.clear()

    return ConversationHandler.END


async def cancel_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Cancel product addition
    Clears conversation state
    """
    query = update.callback_query if update.callback_query else None

    if query:
        await query.answer()
        await query.edit_message_text("❌ Добавление блюда отменено")
    else:
        await update.message.reply_text("❌ Добавление блюда отменено")

    context.user_data.clear()
    return ConversationHandler.END


def get_product_conversation_handler():
    """
    Create and return the ConversationHandler for product addition
    This is used in main bot setup
    """
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(add_product_start, pattern='^add_product$'),
            CommandHandler('addproduct', add_product_start)
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, product_name)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, product_description)],
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, product_price)],
            IMAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, product_image)],
            CATEGORY: [CallbackQueryHandler(product_category, pattern='^cat')],
            INGREDIENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, product_ingredients)],
            CONFIRM: [
                CallbackQueryHandler(saveproduct, pattern='saveproduct'),
                CallbackQueryHandler(cancel_product, pattern='cancelproduct')
            ]
        },
        fallbacks=[
            CommandHandler('cancel', cancel_product),
            CallbackQueryHandler(cancel_product, pattern='cancelproduct')
        ]
    )


# ============================================================================
# EDIT PRODUCT HANDLERS
# ============================================================================

async def edit_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start editing a product - show list of all products"""
    query = update.callback_query if update.callback_query else None

    if query:
        await query.answer()
        if query.from_user.id not in ADMIN_IDS:
            await query.edit_message_text("❌ Только для администраторов")
            return ConversationHandler.END
        message = query.message
    else:
        if update.effective_user.id not in ADMIN_IDS:
            await update.message.reply_text("❌ Только для администраторов")
            return ConversationHandler.END
        message = update.message

    # Get all products
    products = get_all_products()

    if not products:
        text = "❌ Нет продуктов для редактирования"
        if query:
            await query.edit_message_text(text)
        else:
            await message.reply_text(text)
        return ConversationHandler.END

    # Create buttons for each product (max 3 per row)
    keyboard = []
    for i in range(0, len(products), 3):
        row = []
        for product in products[i:i+3]:
            product_id = product[0]
            product_name = product[1]
            # Truncate long names
            display_name = product_name[:20] + '...' if len(product_name) > 20 else product_name
            row.append(InlineKeyboardButton(display_name, callback_data=f"editprod_{product_id}"))
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("❌ Отменить", callback_data="cancel_edit")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "📝 <b>Редактирование продукта</b>\n\nВыберите продукт для редактирования:"

    if query:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
    else:
        await message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')

    return EDIT_SELECT_PRODUCT


async def edit_select_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User selected a product, now select which field to edit"""
    query = update.callback_query
    await query.answer()

    product_id = query.data.replace('editprod_', '')
    context.user_data['edit_product_id'] = product_id

    # Get product details
    products = get_all_products()
    product = next((p for p in products if p[0] == product_id), None)

    if not product:
        await query.edit_message_text("❌ Продукт не найден")
        return ConversationHandler.END

    # Store product info
    context.user_data['edit_product_info'] = {
        'id': product[0],
        'name': product[1],
        'description': product[2],
        'price': product[3],
        'image': product[4]
    }

    keyboard = [
        [InlineKeyboardButton("📝 Название", callback_data="editfield_name")],
        [InlineKeyboardButton("📄 Описание", callback_data="editfield_description")],
        [InlineKeyboardButton("💰 Цена", callback_data="editfield_price")],
        [InlineKeyboardButton("🖼️ Изображение", callback_data="editfield_image")],
        [InlineKeyboardButton("❌ Отменить", callback_data="cancel_edit")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"""📦 <b>Продукт:</b> {product[1]}

<b>Текущие данные:</b>
📝 Название: {product[1]}
📄 Описание: {product[2][:100]}{'...' if len(product[2]) > 100 else ''}
💰 Цена: {product[3]} AED
🖼️ Изображение: {product[4][:50]}...

Что вы хотите изменить?"""

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
    return EDIT_SELECT_FIELD


async def edit_input_new_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User selected field to edit, ask for new value"""
    query = update.callback_query
    await query.answer()

    field = query.data.replace('editfield_', '')
    context.user_data['edit_field'] = field

    product_info = context.user_data.get('edit_product_info', {})

    field_names = {
        'name': 'название',
        'description': 'описание',
        'price': 'цену',
        'image': 'URL изображения'
    }

    field_examples = {
        'name': 'Например: Пельмени домашние',
        'description': 'Например: Вкусные домашние пельмени с мясом',
        'price': 'Например: 85.50',
        'image': 'Например: https://images.unsplash.com/photo-...'
    }

    text = f"""✏️ <b>Редактирование: {field_names[field]}</b>

<b>Текущее значение:</b>
{product_info.get(field, 'Не указано')}

Введите новое значение:
{field_examples[field]}"""

    await query.edit_message_text(text, parse_mode='HTML')
    return EDIT_NEW_VALUE


async def edit_confirm_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User entered new value, show confirmation"""
    new_value = update.message.text.strip()
    field = context.user_data.get('edit_field')
    product_info = context.user_data.get('edit_product_info', {})

    # Validate input
    if field == 'price':
        try:
            new_value = float(new_value)
            if new_value <= 0:
                await update.message.reply_text("❌ Цена должна быть больше 0. Попробуйте снова:")
                return EDIT_NEW_VALUE
        except ValueError:
            await update.message.reply_text("❌ Неверный формат цены. Введите число (например: 25 или 25.50):")
            return EDIT_NEW_VALUE
    elif field == 'name' and len(new_value) < 3:
        await update.message.reply_text("❌ Название слишком короткое. Минимум 3 символа:")
        return EDIT_NEW_VALUE
    elif field == 'description' and len(new_value) < 10:
        await update.message.reply_text("❌ Описание слишком короткое. Минимум 10 символов:")
        return EDIT_NEW_VALUE
    elif field == 'image' and not new_value.startswith(('http://', 'https://')):
        await update.message.reply_text("❌ URL изображения должен начинаться с http:// или https://:")
        return EDIT_NEW_VALUE

    context.user_data['edit_new_value'] = new_value

    field_names = {
        'name': 'Название',
        'description': 'Описание',
        'price': 'Цена',
        'image': 'Изображение'
    }

    old_value = product_info.get(field, 'Не указано')
    display_new = new_value if field != 'image' else f"{str(new_value)[:50]}..."
    display_old = old_value if field != 'image' else f"{str(old_value)[:50]}..."

    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_edit")],
        [InlineKeyboardButton("❌ Отменить", callback_data="cancel_edit")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"""📋 <b>Подтверждение изменений</b>

<b>Продукт:</b> {product_info.get('name')}
<b>Поле:</b> {field_names[field]}

<b>Было:</b>
{display_old}

<b>Станет:</b>
{display_new}

Подтвердить изменение?"""

    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')
    return EDIT_CONFIRM


async def edit_save_changes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save changes to database"""
    query = update.callback_query
    await query.answer()

    product_id = context.user_data.get('edit_product_id')
    field = context.user_data.get('edit_field')
    new_value = context.user_data.get('edit_new_value')
    product_info = context.user_data.get('edit_product_info', {})

    try:
        edit_product(product_id, field, new_value)

        field_names = {
            'name': 'название',
            'description': 'описание',
            'price': 'цена',
            'image': 'изображение'
        }

        success_text = f"""✅ <b>Изменения сохранены!</b>

📦 Продукт: {product_info.get('name')}
✏️ Обновлено: {field_names[field]}

⚡ Изменения вступили в силу!
➡️ Проверьте мини-приложение."""

        await query.edit_message_text(success_text, parse_mode='HTML')

    except Exception as e:
        await query.edit_message_text(f"❌ Ошибка при сохранении: {str(e)}")

    finally:
        context.user_data.clear()

    return ConversationHandler.END


async def cancel_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel edit operation"""
    query = update.callback_query if update.callback_query else None

    if query:
        await query.answer()
        await query.edit_message_text("❌ Редактирование отменено")
    else:
        await update.message.reply_text("❌ Редактирование отменено")

    context.user_data.clear()
    return ConversationHandler.END


def get_edit_product_conversation_handler():
    """Create and return the ConversationHandler for product editing"""
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(edit_product_start, pattern='^edit_product$'),
            CommandHandler('edit', edit_product_start)
        ],
        states={
            EDIT_SELECT_PRODUCT: [
                CallbackQueryHandler(edit_select_field, pattern='^editprod_'),
                CallbackQueryHandler(cancel_edit, pattern='^cancel_edit$')
            ],
            EDIT_SELECT_FIELD: [
                CallbackQueryHandler(edit_input_new_value, pattern='^editfield_'),
                CallbackQueryHandler(cancel_edit, pattern='^cancel_edit$')
            ],
            EDIT_NEW_VALUE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, edit_confirm_change)
            ],
            EDIT_CONFIRM: [
                CallbackQueryHandler(edit_save_changes, pattern='^confirm_edit$'),
                CallbackQueryHandler(cancel_edit, pattern='^cancel_edit$')
            ]
        },
        fallbacks=[
            CommandHandler('cancel', cancel_edit),
            CallbackQueryHandler(cancel_edit, pattern='^cancel_edit$')
        ]
    )
