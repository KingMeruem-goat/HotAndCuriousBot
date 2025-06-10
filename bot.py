import os
import telebot
from flask import Flask, request

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

questions = {
    "Icebreaker Fun": [
        "Quel est ton plus gros fou rire récemment ?",
        "Si tu pouvais être un personnage de film, qui serais-tu ?"
    ],
    "Deep & Curious": [
        "Qu'est-ce qui te fait te sentir profondément aimé(e) ?",
        "As-tu une blessure du passé que tu n’as jamais partagée ?"
    ],
    "Flirty & Cheeky": [
        "Quelle partie de ton corps préfères-tu qu'on touche ?",
        "Préférerais-tu un baiser doux ou un baiser passionné ?"
    ],
    "Hot & Spicy": [
        "Décris ce que tu aimerais faire si on était seuls maintenant.",
        "Quel fantasme aimerais-tu réaliser un jour ?"
    ],
    "Dare Time": [
        "Envoie un message vocal sexy à l’autre.",
        "Fais une imitation sexy de ton animal préféré en vocal."
    ]
}

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for level in questions:
        markup.add(level)
    bot.send_message(message.chat.id, "Bienvenue dans *Hot & Curious* 🔥 Choisis un niveau :", parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in questions)
def send_question(message):
    import random
    level = message.text
    q = random.choice(questions[level])
    bot.send_message(message.chat.id, f"🃏 *{level}*

{q}", parse_mode='Markdown')

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return 'OK', 200

@app.route('/')
def index():
    return "Bot is running!"

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
