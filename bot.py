import os
import random
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request

# === CONFIGURATION ===
TOKEN = "7771606520:AAFp9ZonHi-MSgi1Jah_M9KmrgGKzH9v_Lk"
bot = telebot.TeleBot(TOKEN, threaded=False)
bot_username = bot.get_me().username
WEBHOOK_URL = f"https://TON-NOM-RENDER.onrender.com/{TOKEN}"  # à remplacer par ton URL Render

app = Flask(__name__)

# === QUESTIONS PAR NIVEAU ===
questions = {
    "Icebreaker Fun": [
        "Quel est ton emoji préféré pour draguer ?",
        "Si on devait avoir un nom d’équipe, ce serait quoi ?",
        "Si tu devais m’envoyer un seul mème pour résumer notre relation, ce serait lequel ?",
        "Est-ce que tu chantes sous la douche ? Preuve audio ?",
        "Quelle est ta pire gaffe en visio ou appel vocal ?",
        "Si tu pouvais dîner avec un personnage fictif, ce serait qui ?",
        "As-tu un surnom marrant ou gênant que tu n’aimes pas trop ?",
        "Tu préfères avoir des doigts en spaghetti ou des jambes en mousse ?",
        "Quelle chanson te donne instantanément la pêche ?",
        "Envoie un selfie avec la tête que tu fais quand tu veux séduire (si t’oses 😏).",
        "Quelle est l’émoticône que tu utilises trop souvent ?",
        "À quelle heure de la journée es-tu au top de ta forme ?",
        "Tu es plutôt “je parle trop” ou “je réponds en 3 mots” en couple à distance ?"
    ],
    "Deep & Curious": [
        "À distance, de quoi as-tu le plus peur dans une relation ?",
        "Quelle est la chose qui te manque le plus chez moi en ce moment ?",
        "Quelle serait pour toi la pire rupture virtuelle ?",
        "Que dirais-tu dans un vocal si tu devais me faire fondre ce soir ?",
        "Qu’est-ce qui te manque le plus quand on est loin ?",
        "As-tu déjà aimé quelqu’un à distance ? Raconte.",
        "Quelle est ta plus grande peur dans une relation ?",
        "Que veux-tu qu’on n’oublie jamais de faire ensemble, peu importe la distance ?",
        "As-tu une blessure du passé que tu n’as pas encore totalement guérie ?",
        "Quel est ton langage de l’amour ?",
        "Quand te sens-tu vraiment écouté.e ?",
        "Quelle qualité aimerais-tu améliorer chez toi ?",
        "As-tu déjà pleuré à cause de l’amour ?",
        "Qu’est-ce qui te rassure instantanément quand on est loin l’un de l’autre ?"
    ],
    "Flirty & Cheeky": [
        "Décris-moi la tenue que tu voudrais que je porte pour toi maintenant.",
        "Tu préfères les messages coquins ou les photos sexy ?",
        "En visio, tu me regardes plus dans les yeux… ou ailleurs ?",
        "Si tu pouvais m’embrasser là tout de suite, tu commencerais par où ?",
        "Si je t’envoie un message “J’ai besoin de toi là, tout de suite”, tu fais quoi ?",
        "Tu préfères qu’on te chuchote des mots doux ou des choses coquines ?",
        "Que portes-tu généralement quand tu es seul·e à la maison ?",
        "Quel est le plus long message sexy que tu as déjà envoyé ?",
        "Quelle partie de mon corps as-tu le plus envie de découvrir en vrai ?",
        "Préfères-tu un strip‑tease par visio ou un vocal très explicite ?",
        "Quelle est ta plus grande tentation quand tu me regardes à l’écran ?",
        "M’enverrais‑tu une photo sexy si je te le demande gentiment ?",
        "Quel mot ou geste de ma part pourrait te rendre fou/folle à distance ?",
        "T’as déjà fantasmé en plein appel vidéo ?"
    ],
    "Hot & Spicy": [
        "Décris-moi un fantasme qu’on pourrait réaliser même à distance.",
        "Tu m’envoies un vocal en murmurant une envie ?",
        "Si je te proposais un strip visio par tour, tu serais partant·e ?",
        "Quelle est la chose la plus coquine que tu aies faite au téléphone ?",
        "Quel est ton fantasme le plus réaliste à réaliser en ligne ?",
        "Si je te dis “on fait un jeu coquin par audio ce soir”, tu dis quoi ?",
        "Quel est le moment de la journée où tu es le plus chaud·e ?",
        "As-tu déjà joué avec toi-même en pensant à moi ? Raconte sans tabou.",
        "Que dirais‑tu si je te proposais un appel vidéo torride maintenant ?",
    ]
}

# === SESSIONS ===
sessions = {}  # key: player_id, value: game info
invitations = {}  # key: token, value: player1_id
game_states = {}  # key: player1_id, value: game_state

# === OUTILS ===
def build_levels_keyboard(player1_id):
    markup = InlineKeyboardMarkup()
    for level in questions.keys():
        markup.add(InlineKeyboardButton(level, callback_data=f"level_{level}|{player1_id}"))
    markup.add(InlineKeyboardButton("Fin de partie ❌", callback_data=f"end|{player1_id}"))
    return markup

def ask_question(level, current_turn, other_player_id):
    q = random.choice(questions[level])
    return f"🔄 Tour de jeu\n\n🎯 *{current_turn}*, choisis une question !\n\n🎤 Question pour *{other_player_id}* :\n_{q}_"

def send_question(player1_id, level):
    state = game_states[player1_id]
    p1, p2 = state["players"]
    current_turn = state["current_turn"]
    other = p1 if current_turn == p2 else p2

    text = ask_question(level, current_turn, other)
    markup = build_levels_keyboard(player1_id)

    for pid in (p1, p2):
        bot.send_message(pid, text, reply_markup=markup, parse_mode="Markdown")

def end_game(player1_id):
    state = game_states.get(player1_id)
    if not state: return
    for pid in state["players"]:
        try:
            bot.send_message(pid, "🚫 Fin de la partie ! À bientôt 😘")
        except:
            pass
    game_states.pop(player1_id, None)

# === HANDLERS ===
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    sessions[user_id] = {}
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Jouer à deux 🔗", callback_data="multiplayer"))
    bot.send_message(user_id, "🔥 Bienvenue dans *Hot & Curious* !\n\nChoisis un mode :", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    data = call.data
    user_id = call.from_user.id

    if data == "multiplayer":
        token = str(user_id)
        link = f"https://t.me/{bot_username}?start={token}"
        invitations[token] = user_id
        bot.send_message(user_id, f"🔗 Partage ce lien avec ton/ta partenaire :\n{link}\n\nLa partie commencera dès qu’il/elle cliquera dessus.")
    
    elif data.startswith("level_"):
        level, player1_id = data.split("|")
        level = level.replace("level_", "")
        if int(player1_id) in game_states:
            send_question(int(player1_id), level)
            # Alterne le joueur
            gs = game_states[int(player1_id)]
            gs["current_turn"] = gs["players"][1] if gs["current_turn"] == gs["players"][0] else gs["players"][0]

    elif data.startswith("end"):
        player1_id = int(data.split("|")[1])
        end_game(player1_id)

@bot.message_handler(commands=['start'])
def join_game(message):
    args = message.text.split()
    if len(args) > 1 and args[1] in invitations:
        player1_id = int(args[1])
        player2_id = message.from_user.id
        game_states[player1_id] = {"players": (player1_id, player2_id), "current_turn": player1_id}
        bot.send_message(player1_id, f"🎮 Ton/ta partenaire a rejoint la partie ! C’est à toi de commencer 😏")
        bot.send_message(player2_id, f"🎮 Tu as rejoint la partie ! Prépare-toi 🔥")
        # Aucun envoi automatique de question ici

# === FLASK SETUP POUR WEBHOOK ===
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "", 200

@app.route('/')
def index():
    return 'Bot en ligne !'

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
