import os
import random
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request

# === CONFIGURATION ===
TOKEN = "7771606520:AAFp9ZonHi-MSgi1Jah_M9KmrgGKzH9v_Lk"
bot = telebot.TeleBot(TOKEN, threaded=False)
bot_username = bot.get_me().username
WEBHOOK_URL = f"https://TON-NOM-RENDER.onrender.com/{TOKEN}"  # Replace with your Render URL

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
        "Tu préfères me regarder ou m’écouter pendant un moment très hot ?",
        "Quel est le truc le plus coquin que tu pourrais faire avec un objet près de toi ?",
        "Tu m’envoies un message audio sexy maintenant ? (ose 😈)",
        "T’as déjà fantasmé sur ce qu’on ferait dans le même lit ?",
        "Envoie‑moi une phrase hot que tu voudrais me dire les yeux dans les yeux."
    ],
    "Dare Time": [
        "Envoie une photo d’un endroit de ton corps que j’adore (sans visage).",
        "Enregistre un audio très lent où tu dis ce que tu ferais si j’étais là.",
        "Vidéo : dis quelque chose de chaud avec un regard de tueur·euse.",
        "Choisis un mot, et chaque fois que tu l’entends aujourd’hui, pense à moi nu·e.",
        "Envoie un vocal où tu gémis discrètement pendant 10 secondes.",
        "Fais un strip‑tease d’une pièce à la caméra.",
        "Envoie un selfie à moitié couvert·e (laisse deviner le reste).",
        "Écris une mini‑histoire..."
    ]
}

# === GAME STATE STORAGE ===
pending_games = {}  # game_id: {
                   #   'host': user_id,
                   #   'players': [user_id1, user_id2],
                   #   'current_turn': int (index of player choosing question),
                   #   'messages': [(chat_id, message_id), ...],
                   #   'active': True/False
                   # }

# === UTILITY FUNCTIONS ===
def create_category_menu():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for category in questions.keys():
        markup.add(InlineKeyboardButton(category, callback_data=f"category_{category}"))
    markup.add(InlineKeyboardButton("Fin de partie", callback_data="end_game"))
    return markup

def create_end_game_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Fin de partie", callback_data="end_game"))
    return markup

def delete_game_messages(game_id):
    if game_id in pending_games:
        for chat_id, message_id in pending_games[game_id]['messages']:
            try:
                bot.delete_message(chat_id, message_id)
            except:
                pass
        del pending_games[game_id]

# === COMMANDES DE BASE ===
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    args = message.text.split()
    
    if len(args) >= 1 and args[1].startswith("join_"):
        game_id = args[1].replace("join_", "")
        if game_id in pending_games and len(pending_games[game_id]['players']) < 2:
            pending_games[game_id]['players'].append(user_id)
            bot.send_message(user_id, "Tu as rejoint la partie ! En attente du host pour commencer 😏")
            bot.send_message(
                pending_games[game_id]['host'], 
                "Ton partenaire a rejoint ! Clique pour démarrer la partie :",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton("Démarrer la partie", callback_data=f"start_game_{game_id}")]
                ])
            )
        else:
            bot.send_message(user_id, "Lien invalide ou partie déjà complète.")
    else:
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(
            InlineKeyboardButton("Jouer en solo 🎲", callback_data="solo"),
            InlineKeyboardButton("Jouer à deux ❤️", callback_data="multiplayer")
        )
        bot.send_message(user_id, "Bienvenue dans *Hot & Curious* 🔥\nChoisis un mode :", parse_mode='Markdown', reply_markup=markup)

# === DÉBUT DE PARTIE MULTIJOUEUR ===
@bot.callback_query_handler(func=lambda call: call.data == "multiplayer")
def multiplayer_mode(call):
    user_id = call.from_user.id
    game_id = str(user_id)
    pending_games[game_id] = {
        'host': user_id,
        'players': [user_id],
        'current_turn': 0,
        'messages': [],
        'active': False
    }
    invite_link = f"https://t.me/{bot_username}?start=join_{game_id}"
    bot.send_message(user_id, f"Envoie ce lien à ton/ta partenaire pour commencer :\n{invite_link}")

# === START MULTIPLAYER GAME ===
@bot.callback_query_handler(func=lambda call: call.data.startswith("start_game_"))
def start_multiplayer_game(call):
    user_id = call.from_user.id
    game_id = call.data.split("_")[2]
    if game_id not in pending_games or pending_games[game_id]['host'] != user_id:
        bot.send_message(user_id, "Tu n'es pas l'hôte de cette partie.")
        return
    if len(pending_games[game_id]['players']) != 2:
        bot.send_message(user_id, "Attends que ton partenaire rejoigne la partie !")
        return
    
    pending_games[game_id]['active'] = True
    for player_id in pending_games[game_id]['players']:
        msg = bot.send_message(
            player_id,
            f"La partie commence ! <@{pending_games[game_id]['players'][0]}> choisit la première catégorie.",
            parse_mode='Markdown',
            reply_markup=create_category_menu()
        )
        pending_games[game_id]['messages'].append((player_id, msg.message_id))
    bot.answer_callback_query(call.id)

# === SÉLECTION DE CATÉGORIE ===
@bot.callback_query_handler(func=lambda call: call.data.startswith("category_"))
def select_category(call):
    user_id = call.from_user.id
    game_id = None
    for gid, game in pending_games.items():
        if user_id in game['players'] and game['active']:
            game_id = gid
            break
    
    if not game_id:
        bot.send_message(user_id, "Aucune partie active trouvée.")
        return
    
    game = pending_games[game_id]
    current_player_idx = game['current_turn'] % 2
    if user_id != game['players'][current_player_idx]:
        bot.send_message(user_id, "Ce n'est pas ton tour de choisir !")
        return
    
    category = call.data.replace("category_", "")
    if category not in questions:
        bot.send_message(user_id, "Catégorie invalide.")
        return
    
    question = random.choice(questions[category])
    responder_idx = (current_player_idx + 1) % 2
    responder_id = game['players'][responder_idx]
    
    # Send question to both players
    for player_id in game['players']:
        msg_text = f"*{category}*\n{question}\n<@{responder_id}> répond à cette question !"
        msg = bot.send_message(
            player_id,
            msg_text,
            parse_mode='Markdown',
            reply_markup=create_end_game_button()
        )
        game['messages'].append((player_id, msg.message_id))
    
    # Prompt responder to answer
    bot.send_message(responder_id, "Envoie ta réponse dans le chat !")
    
    # Update turn
    game['current_turn'] += 1
    next_chooser_idx = game['current_turn'] % 2
    next_chooser_id = game['players'][next_chooser_idx]
    msg = bot.send_message(
        next_chooser_id,
        f"Ton tour de choisir une catégorie, <@{next_chooser_id}> !",
        parse_mode='Markdown',
        reply_markup=create_category_menu()
    )
    game['messages'].append((next_chooser_id, msg.message_id))
    
    bot.answer_callback_query(call.id)

# === FIN DE PARTIE ===
@bot.callback_query_handler(func=lambda call: call.data == "end_game")
def end_game(call):
    user_id = call.from_user.id
    game_id = None
    for gid, game in pending_games.items():
        if user_id in game['players'] and game['active']:
            game_id = gid
            break
    
    if not game_id:
        bot.send_message(user_id, "Aucune partie active trouvée.")
        return
    
    # Notify players
    for player_id in pending_games[game_id]['players']:
        msg = bot.send_message(player_id, "Partie terminée ! À bientôt pour un autre round 🔥")
        try:
            bot.delete_message(player_id, msg.message_id)
        except:
            pass
    
    # Delete messages
    delete_game_messages(game_id)
    bot.answer_callback_query(call.id)

# === DÉBUT DE PARTIE SOLO ===
@bot.callback_query_handler(func=lambda call: call.data == "solo")
def solo_mode(call):
    user_id = call.from_user.id
    send_question(user_id)

# === ENVOI QUESTION SOLO ===
def send_question(user_id):
    niveau = random.choice(list(questions.keys()))
    question = random.choice(questions[niveau])
    bot.send_message(user_id, f"*{niveau}*\n{question}", parse_mode='Markdown')

# === FLASK WEBHOOK ===
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return '', 200

@app.route('/')
def index():
    return 'Bot en ligne !'

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
