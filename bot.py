"""
Halloween Quest Telegram Bot
Handles parent linking and photo approval workflow
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Optional

from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import config
from database import db

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Bot instance
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()
router = Router()

# States for FSM
class PhotoReviewStates(StatesGroup):
    waiting_for_comment = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command with session linking"""
    args = message.text.split(" ", 1)
    
    if len(args) > 1 and args[1].startswith("quest_"):
        # Parent linking from QR code
        child_session_id = args[1]
        
        # Create family link
        success = await db.create_family_link(
            child_session_id=child_session_id,
            parent_chat_id=message.chat.id,
            parent_username=message.from_user.username,
            parent_first_name=message.from_user.first_name
        )
        
        if success:
            await message.answer(
                f"🎃 <b>Добро пожаловать в Хеллоуин квест!</b>\n\n"
                f"Вы успешно подключены как родитель.\n"
                f"Теперь вы будете получать фотографии заданий от ребенка для проверки.\n\n"
                f"📱 <i>Ребенок может продолжать квест!</i>",
                parse_mode="HTML"
            )
            logger.info(f"Family link created: {child_session_id} -> {message.chat.id}")
        else:
            await message.answer(
                "❌ Произошла ошибка при подключении.\n"
                "Попробуйте отсканировать QR-код еще раз."
            )
    else:
        # Regular start without linking
        await message.answer(
            f"👋 Привет, {message.from_user.first_name}!\n\n"
            f"Я бот для Хеллоуин квеста. Чтобы подключиться как родитель, "
            f"отсканируйте QR-код из приложения квеста.\n\n"
            f"🎃 Удачного квеста!"
        )

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Help command"""
    await message.answer(
        "🎃 <b>Хеллоуин квест бот</b>\n\n"
        "<b>Команды:</b>\n"
        "• /start - Начать работу с ботом\n"
        "• /help - Показать эту справку\n\n"
        "<b>Как это работает:</b>\n"
        "1. Ребенок сканирует QR-код в приложении квеста\n"
        "2. Вы подтверждаете подключение как родитель\n"
        "3. Получаете фотографии заданий для проверки\n"
        "4. Одобряете или просите переделать\n\n"
        "🎃 Удачного квеста!",
        parse_mode="HTML"
    )

async def send_photo_for_review(parent_chat_id: int, submission_id: str, task_name: str, photo_path: str):
    """Send photo to parent for review"""
    try:
        # Create inline keyboard
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Отлично!", callback_data=f"approve_{submission_id}"),
                InlineKeyboardButton(text="❌ Переделать", callback_data=f"reject_{submission_id}")
            ],
            [
                InlineKeyboardButton(text="💬 Оставить комментарий", callback_data=f"comment_{submission_id}")
            ]
        ])
        
        # Send photo with caption
        photo = FSInputFile(photo_path)
        message = await bot.send_photo(
            chat_id=parent_chat_id,
            photo=photo,
            caption=(
                f"🎃 <b>Новое задание выполнено!</b>\n\n"
                f"📋 <b>Задание:</b> {task_name}\n"
                f"📸 <b>Фотография от ребенка</b>\n\n"
                f"Оцените выполнение задания:"
            ),
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        # Save message info
        await db.save_bot_message(
            chat_id=parent_chat_id,
            message_id=message.message_id,
            submission_id=submission_id,
            message_type="photo_review"
        )
        
        logger.info(f"Photo sent for review: {submission_id} -> {parent_chat_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending photo for review: {e}")
        return False

@router.callback_query(F.data.startswith("approve_"))
async def handle_approve(callback_query: CallbackQuery):
    """Handle photo approval"""
    submission_id = callback_query.data.split("_", 1)[1]
    
    # Update status in database
    success = await db.update_photo_status(submission_id, "approved")
    
    if success:
        await callback_query.message.edit_reply_markup(reply_markup=None)
        await callback_query.answer("✅ Фотография одобрена!")
        await callback_query.message.reply(
            "✅ <b>Задание одобрено!</b>\n\n"
            "Ребенок может продолжать квест. Отличная работа! 🎉",
            parse_mode="HTML"
        )
        logger.info(f"Photo approved: {submission_id}")
    else:
        await callback_query.answer("❌ Ошибка при обработке")

@router.callback_query(F.data.startswith("reject_"))
async def handle_reject(callback_query: CallbackQuery):
    """Handle photo rejection"""
    submission_id = callback_query.data.split("_", 1)[1]
    
    # Update status in database
    success = await db.update_photo_status(submission_id, "rejected", "Попробуйте еще раз")
    
    if success:
        await callback_query.message.edit_reply_markup(reply_markup=None)
        await callback_query.answer("❌ Задание отклонено")
        await callback_query.message.reply(
            "❌ <b>Задание нужно переделать</b>\n\n"
            "Ребенок получит уведомление и сможет попробовать еще раз.",
            parse_mode="HTML"
        )
        logger.info(f"Photo rejected: {submission_id}")
    else:
        await callback_query.answer("❌ Ошибка при обработке")

@router.callback_query(F.data.startswith("comment_"))
async def handle_comment_request(callback_query: CallbackQuery, state: FSMContext):
    """Handle comment request"""
    submission_id = callback_query.data.split("_", 1)[1]
    
    await state.set_state(PhotoReviewStates.waiting_for_comment)
    await state.update_data(submission_id=submission_id)
    
    await callback_query.message.reply(
        "💬 <b>Напишите комментарий для ребенка:</b>\n\n"
        "Например: \"Молодец! Но попробуй сделать тень более четкой\" или \"Отлично выполнено!\"",
        parse_mode="HTML"
    )
    await callback_query.answer()

@router.message(PhotoReviewStates.waiting_for_comment)
async def handle_comment_text(message: Message, state: FSMContext):
    """Handle comment text input"""
    data = await state.get_data()
    submission_id = data.get("submission_id")
    comment = message.text
    
    if not submission_id:
        await message.answer("❌ Ошибка: задание не найдено")
        await state.clear()
        return
    
    # Create keyboard for final decision
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Одобрить с комментарием", callback_data=f"approve_comment_{submission_id}"),
            InlineKeyboardButton(text="❌ Отклонить с комментарием", callback_data=f"reject_comment_{submission_id}")
        ]
    ])
    
    await state.update_data(comment=comment)
    
    await message.answer(
        f"💬 <b>Ваш комментарий:</b>\n\n"
        f"<i>\"{comment}\"</i>\n\n"
        f"Теперь выберите решение:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("approve_comment_"))
async def handle_approve_with_comment(callback_query: CallbackQuery, state: FSMContext):
    """Handle approval with comment"""
    submission_id = callback_query.data.split("_", 2)[2]
    data = await state.get_data()
    comment = data.get("comment", "")
    
    success = await db.update_photo_status(submission_id, "approved", comment)
    
    if success:
        await callback_query.message.edit_reply_markup(reply_markup=None)
        await callback_query.answer("✅ Задание одобрено с комментарием!")
        await callback_query.message.reply(
            f"✅ <b>Задание одобрено!</b>\n\n"
            f"💬 <b>Ваш комментарий:</b> \"{comment}\"\n\n"
            f"Ребенок может продолжать квест! 🎉",
            parse_mode="HTML"
        )
        logger.info(f"Photo approved with comment: {submission_id}")
    else:
        await callback_query.answer("❌ Ошибка при обработке")
    
    await state.clear()

@router.callback_query(F.data.startswith("reject_comment_"))
async def handle_reject_with_comment(callback_query: CallbackQuery, state: FSMContext):
    """Handle rejection with comment"""
    submission_id = callback_query.data.split("_", 2)[2]
    data = await state.get_data()
    comment = data.get("comment", "")
    
    success = await db.update_photo_status(submission_id, "rejected", comment)
    
    if success:
        await callback_query.message.edit_reply_markup(reply_markup=None)
        await callback_query.answer("❌ Задание отклонено с комментарием")
        await callback_query.message.reply(
            f"❌ <b>Задание нужно переделать</b>\n\n"
            f"💬 <b>Ваш комментарий:</b> \"{comment}\"\n\n"
            f"Ребенок получит ваши рекомендации и сможет попробовать еще раз.",
            parse_mode="HTML"
        )
        logger.info(f"Photo rejected with comment: {submission_id}")
    else:
        await callback_query.answer("❌ Ошибка при обработке")
    
    await state.clear()

async def main():
    """Main bot function"""
    # Initialize database
    await db.init_db()
    logger.info("Database initialized")
    
    # Register router
    dp.include_router(router)
    
    # Start polling
    logger.info("Bot starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
