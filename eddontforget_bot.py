from datetime import datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters
from apscheduler.schedulers.background import BackgroundScheduler

TOKEN = 'your bot's tokken'
scheduler = BackgroundScheduler()

def remind(context: CallbackContext):
    job = context.job
    context.bot.send_message(chat_id=job.context, text=job.name)

def start(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text='Отправьте мне текст для напоминания.')

def handle_message(update: Update, context: CallbackContext) -> None:
    reminder_text = update.message.text
    message = "Последние две цифры года (например, 23 для 2023):"
    context.user_data['reminder'] = {'text': reminder_text}
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    context.user_data['next_step'] = handle_year

def handle_year(update: Update, context: CallbackContext) -> None:
    year = int("20" + update.message.text)
    context.user_data['reminder']['year'] = year
    message = "Теперь укажите месяц (от 1 до 12):"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    context.user_data['next_step'] = handle_month

def handle_month(update: Update, context: CallbackContext) -> None:
    month = int(update.message.text)
    context.user_data['reminder']['month'] = month
    message = "Укажите день:"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    context.user_data['next_step'] = handle_day

def handle_day(update: Update, context: CallbackContext) -> None:
    day = int(update.message.text)
    context.user_data['reminder']['day'] = day
    message = "Теперь укажите время в формате HH:MM:"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    context.user_data['next_step'] = schedule_reminder

def schedule_reminder(update: Update, context: CallbackContext) -> None:
    time_str = update.message.text
    hour, minute = map(int, time_str.split(':'))
    reminder = context.user_data['reminder']
    dt = datetime(reminder['year'], reminder['month'], reminder['day'], hour, minute)
    
    scheduler.add_job(remind, 'date', run_date=dt, args=[context], id=str(update.effective_chat.id), name=reminder['text'])
    message = "Напоминание запланировано!"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    del context.user_data['reminder']
    del context.user_data['next_step']

def message_handler(update: Update, context: CallbackContext) -> None:
    if 'next_step' in context.user_data:
        context.user_data['next_step'](update, context)
    else:
        handle_message(update, context)

def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))

    scheduler.start()
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
