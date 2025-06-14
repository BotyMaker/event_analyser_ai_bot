import logging
from telegram import Update, BotCommand
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler, 
    filters, 
    ContextTypes
)

from .config import config
from .models import init_db
from .repository import get_user_repo
from .analyzer import NewsAnalysisPipeline
from .localization import localization
from .ui import (
    create_language_keyboard, 
    create_onboarding_keyboard, 
    create_custom_instruction_keyboard, 
    create_settings_keyboard
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

analyzer = NewsAnalysisPipeline()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = create_onboarding_keyboard()
    await update.message.reply_text(
        f"{localization.get_text('onboarding.title')}\n\n"
        f"{localization.get_text('onboarding.instruction')}",
        reply_markup=keyboard
    )


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_repo = get_user_repo()
    user = user_repo.get_or_create(update.effective_user.id)
    
    keyboard = create_language_keyboard(user.language)
    await update.message.reply_text(
        f"{localization.get_text('language.title', user.language)}\n\n"
        f"{localization.get_text('language.instruction', user.language)}\n\n"
        f"{localization.get_text('language.current', user.language)}",
        reply_markup=keyboard
    )


async def setting_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_repo = get_user_repo()
    user = user_repo.get_or_create(update.effective_user.id)
    
    current_instruction = user.custom_instruction or localization.get_default_custom_instruction(user.language)
    
    keyboard = create_settings_keyboard(user.language)
    await update.message.reply_text(
        f"{localization.get_text('settings.title', user.language)}\n\n"
        f"{localization.get_text('settings.current_instruction', user.language)}\n"
        f"```\n{current_instruction}```\n\n"
        f"{localization.get_text('settings.change_prompt', user.language)}",
        parse_mode='Markdown',
        reply_markup=keyboard
    )


async def analyze_news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_repo = get_user_repo()
    user = user_repo.get_or_create(update.effective_user.id)
    
    analyzing_msg = await update.message.reply_text(
        localization.get_text('analysis.analyzing', user.language)
    )
    
    try:
        result = await analyzer.analyze(update.message.text, user.custom_instruction)
        await analyzing_msg.edit_text(result, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        await analyzing_msg.edit_text(
            localization.get_text('analysis.failed', user.language)
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('waiting_for_custom_instruction'):
        await handle_custom_instruction_input(update, context)
    elif context.user_data.get('waiting_for_setting_change'):
        await handle_setting_change_input(update, context)
    else:
        await analyze_news(update, context)


async def handle_custom_instruction_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_repo = get_user_repo()
    user = user_repo.get_or_create(update.effective_user.id)
    
    user_repo.update_custom_instruction(user.telegram_id, update.message.text.strip())
    context.user_data['waiting_for_custom_instruction'] = False
    
    await update.message.reply_text(
        localization.get_text('onboarding.custom_instruction_set', user.language)
    )
    
    await update.message.reply_text(
        f"{localization.get_text('welcome.title', user.language)}\n\n"
        f"{localization.get_text('welcome.description', user.language)}\n\n"
        f"{localization.get_text('welcome.ready', user.language)}"
    )
    
    await update.message.reply_text(
        f"{localization.get_text('onboarding.usage_title', user.language)}\n\n"
        f"{localization.get_text('onboarding.usage_instructions', user.language)}",
        parse_mode='Markdown'
    )


async def handle_setting_change_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_repo = get_user_repo()
    user = user_repo.get_or_create(update.effective_user.id)
    
    user_repo.update_custom_instruction(user.telegram_id, update.message.text.strip())
    context.user_data['waiting_for_setting_change'] = False
    
    await update.message.reply_text(
        localization.get_text('settings.updated', user.language)
    )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("onboard_"):
        await handle_onboarding_language(query, context, data.replace("onboard_", ""))
    
    elif data.startswith("lang_"):
        await handle_language_change(query, data.replace("lang_", ""))
    
    elif data == "custom_default":
        await handle_custom_default(query, context)
    
    elif data == "custom_input":
        await handle_custom_input(query, context)
    
    elif data == "settings_keep":
        await handle_settings_keep(query)
    
    elif data == "settings_reset":
        await handle_settings_reset(query)
    
    elif data == "settings_change":
        await handle_settings_change(query, context)


async def handle_onboarding_language(query, context, language):
    if not localization.is_supported_language(language):
        return
    
    user_repo = get_user_repo()
    user_repo.update_language(query.from_user.id, language)
    
    await query.edit_message_text(
        localization.get_text('onboarding.language_selected', language)
    )
    
    keyboard = create_custom_instruction_keyboard(language)
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f"{localization.get_text('onboarding.custom_instruction_title', language)}\n\n"
             f"{localization.get_text('onboarding.custom_instruction_prompt', language)}",
        reply_markup=keyboard
    )


async def handle_language_change(query, language):
    if not localization.is_supported_language(language):
        return
    
    user_repo = get_user_repo()
    user_repo.update_language(query.from_user.id, language)
    user_repo.update_custom_instruction(
        query.from_user.id, 
        localization.get_default_custom_instruction(language)
    )
    
    await query.edit_message_text(
        localization.get_text('language.changed', language)
    )


async def handle_custom_default(query, context):
    user_repo = get_user_repo()
    user = user_repo.get_or_create(query.from_user.id)
    
    user_repo.update_custom_instruction(
        query.from_user.id,
        localization.get_default_custom_instruction(user.language)
    )
    
    await query.edit_message_text(
        localization.get_text('onboarding.custom_instruction_set', user.language)
    )
    
    await show_welcome_messages(context.bot, query.message.chat_id, user.language)


async def handle_custom_input(query, context):
    user_repo = get_user_repo()
    user = user_repo.get_or_create(query.from_user.id)
    
    await query.edit_message_text(
        localization.get_text('onboarding.custom_instruction_input_prompt', user.language)
    )
    
    context.user_data['waiting_for_custom_instruction'] = True


async def handle_settings_keep(query):
    user_repo = get_user_repo()
    user = user_repo.get_or_create(query.from_user.id)
    
    await query.edit_message_text(
        localization.get_text('settings.kept', user.language)
    )


async def handle_settings_reset(query):
    user_repo = get_user_repo()
    user = user_repo.get_or_create(query.from_user.id)
    
    user_repo.update_custom_instruction(
        query.from_user.id,
        localization.get_default_custom_instruction(user.language)
    )
    
    await query.edit_message_text(
        localization.get_text('settings.reset', user.language)
    )


async def handle_settings_change(query, context):
    user_repo = get_user_repo()
    user = user_repo.get_or_create(query.from_user.id)
    
    await query.edit_message_text(
        localization.get_text('onboarding.custom_instruction_input_prompt', user.language)
    )
    
    context.user_data['waiting_for_setting_change'] = True


async def show_welcome_messages(bot, chat_id, language):
    await bot.send_message(
        chat_id=chat_id,
        text=f"{localization.get_text('welcome.title', language)}\n\n"
             f"{localization.get_text('welcome.description', language)}\n\n"
             f"{localization.get_text('welcome.ready', language)}"
    )
    
    await bot.send_message(
        chat_id=chat_id,
        text=f"{localization.get_text('onboarding.usage_title', language)}\n\n"
             f"{localization.get_text('onboarding.usage_instructions', language)}",
        parse_mode='Markdown'
    )


async def setup_bot_commands(app: Application) -> None:
    commands = [
        BotCommand("start", "Start the bot and setup"),
        BotCommand("language", "Change language"),
        BotCommand("setting", "Customize analysis style"),
    ]
    await app.bot.set_my_commands(commands)
    
    # Set bot description
    description = (
        "Truth Detector - AI-Powered News Fact-Checker\n\n"
        "🤖 AI-Powered Analysis using GPT models\n"
        "🔍 Multi-Source Verification for comprehensive fact-checking\n\n"
        "Open Source & Free: https://github.com/BotyMaker/event_analyser_ai_bot"
    )
    await app.bot.set_my_description(description)


def create_app() -> Application:
    app = Application.builder().token(config.telegram_bot_token).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("language", language_command))
    app.add_handler(CommandHandler("setting", setting_command))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    return app


async def post_init(app: Application) -> None:
    await setup_bot_commands(app)


def run_bot() -> None:
    init_db()
    app = create_app()
    app.post_init = post_init
    logger.info("Starting EventAnalyzer bot...")
    app.run_polling() 