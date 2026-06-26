import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
import asyncio

from analyzer import AdvancedTextAnalyzer

BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN" 

# Добавляем свойства по умолчанию, чтобы Markdown разметка рендерилась корректно
bot = Bot(token=BOT_TOKEN, default_properties=DefaultBotProperties(parse_mode="Markdown"))
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.reply(
        "👋 *Привет! Я профессиональный Text Insight Analyzer Bot.*\n\n"
        "Отправь мне любой текст (на английском или русском языке), и я проведу "
        "его полный лингвистический анализ, определю тональность "
        "и построю аккуратный график частоты слов!"
    )

@dp.message(F.text)
async def analyze_user_text(message: types.Message):
    status_message = await message.answer("🔄 *Анализирую текст и генерирую инфографику...*")
    
    try:
        analyzer = AdvancedTextAnalyzer()
        report = analyzer.process_text_data(message.text, source_name=f"User_{message.from_user.id}")
        
        if not report:
            await status_message.edit_text("❌ Текст слишком короткий или пустой для проведения анализа.")
            return

        chart_filename = f"chart_{message.from_user.id}.png"
        analyzer.plot_statistics(report['common_words'], output_path=chart_filename)

        # Профессионально оформленный шаблон вывода с четкими разделителями
        response_text = (
            f"📊 *TEXT ANALYSIS REPORT*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📝 *Количество предложений:* {report['sentences_count']}\n"
            f"🔤 *Слов после очистки:* {report['words_cleaned_count']}\n"
            f"🎭 *Тональность текста:* {report['mood']} ({report['sentiment_score']})\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔝 *Топ-3 частых слова:*\n"
        )
        
        for word, count in report['common_words'][:3]:
            response_text += f"• `{word}`: {count} раз(а)\n"

        await status_message.delete()

        if os.path.exists(chart_filename):
            await message.answer_photo(
                photo=types.FSInputFile(chart_filename),
                caption=response_text
            )
            os.remove(chart_filename)
        else:
            await message.answer(response_text)

    except Exception as e:
        await status_message.edit_text(f"❌ Произошла непредвиденная ошибка при анализе: {str(e)}")

async def main():
    print("[*] Telegram Bot успешно перезапущен с поддержкой правильных графиков и разметки...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
