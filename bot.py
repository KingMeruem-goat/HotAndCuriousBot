import os
import random
import logging
import uuid
import json
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
from flask import Flask, request

# --- Configuration du Logging ---
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- CONFIGURATION (via variables d'environnement pour la sécurité) ---
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    logger.critical("Erreur : Le token du bot Telegram (TELEGRAM_BOT_TOKEN) n'est pas défini dans les variables d'environnement.")
    exit(1)

bot = telebot.TeleBot(TOKEN, threaded=False)

try:
    bot_info = bot.get_me()
    bot_username = bot_info.username
    logger.info(f"Bot démarré avec succès. Nom d'utilisateur : @{bot_username}")
except telebot.apihelper.ApiTelegramException as e:
    logger.critical(f"Erreur lors de l'obtention des informations du bot : {e}. Vérifiez le token.")
    exit(1)

WEBHOOK_URL = os.environ.get("WEBHOOK_URL", f"https://votre-app-render.onrender.com/{TOKEN}")
if "votre-app-render.onrender.com" in WEBHOOK_URL:
    logger.warning("Attention : WEBHOOK_URL utilise une URL par défaut. Assurez-vous de définir la variable d'environnement WEBHOOK_URL sur Render.")

app = Flask(__name__)

# --- CONFIGURATION DES RESSOURCES VISUELLES/SONORES ---
# REMPLACEZ CES PLACEHOLDERS AVEC VOS VRAIS FILE_ID APRÈS LES AVOIR OBTENUS VIA @RawDataBot
# Vous aurez besoin d'envoyer le sticker/audio à @RawDataBot pour obtenir l'ID.
STICKER_PARTY_STARTED = "CAACAgUAAxkBAAE2Ta1oTe1ZXufjVY93_blgMi6DQpliQwACAhMAAik4iFQZz3jGZUU7JjYE" # Exemple: un sticker festif ou "coquin"
VOICE_TURN_NOTIFICATION = "BQACAgQAAxkBAAE2TdNoTfAqPE98K-dEeOXPApdGWzIUlgACsBkAAsSFcVKq_ncxSd6uoTYE" # Exemple: un audio très court/silencieux pour notification

# --- Persistance des données (avec fichier JSON) ---
DATA_FILE = 'game_data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                logger.warning(f"Fichier de données {DATA_FILE} corrompu ou vide. Initialisation des données.")
                return {'pending_games': {}, 'processed_updates': []}
    logger.info(f"Fichier de données {DATA_FILE} non trouvé. Création d'un nouveau fichier.")
    return {'pending_games': {}, 'processed_updates': []}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)
    logger.debug("Données sauvegardées dans game_data.json")

global_data = load_data()
pending_games = global_data.get('pending_games', {})
processed_updates = set(global_data.get('processed_updates', []))

# --- QUESTIONS PAR NIVEAU (inchangées pour l'instant) ---
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

# --- UTILITY FUNCTIONS ---
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
                logger.debug(f"Message supprimé: chat_id={chat_id}, message_id={message_id}")
            except telebot.apihelper.ApiTelegramException as e:
                logger.warning(f"Impossible de supprimer le message {message_id} dans le chat {chat_id}: {e}")
        del pending_games[game_id]
        save_data(global_data)
        logger.info(f"Partie {game_id} et ses messages supprimés.")

def get_game_by_user(user_id):
    for gid, game in pending_games.items():
        if user_id in game['players'] and game['active']:
            return gid, game
    return None, None

# --- COMMANDES DE BASE ---
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    user_first_name = message.from_user.first_name if message.from_user.first_name else "Cher utilisateur"
    user_mention = f"[{user_first_name}](tg://user?id={user_id})"
    
    args = message.text.split()

    if len(args) > 1 and args[1].startswith("join_"):
        game_id = args[1].replace("join_", "")
        logger.info(f"Tentative de rejoindre: user_id={user_id}, game_id={game_id}")

        if game_id not in pending_games:
            bot.send_message(user_id, "❌ *Lien invalide :* la partie est introuvable ou a déjà été fermée.", parse_mode='Markdown')
            logger.warning(f"Lien invalide pour game_id={game_id} par user_id={user_id}")
            return

        game = pending_games[game_id]

        if user_id in game['players']:
            bot.send_message(user_id, "ℹ️ Tu es *déjà dans cette partie* ! Attends que l'hôte la démarre ou rejoigne un nouveau partenaire.", parse_mode='Markdown')
            return
        if user_id == game['host']:
            bot.send_message(user_id, "👋 Tu es *déjà l'hôte* de cette partie ! Attends que ton partenaire rejoigne.", parse_mode='Markdown')
            return
        if len(game['players']) >= 2:
            bot.send_message(user_id, "🚫 La partie est *déjà complète* ! Tu ne peux pas la rejoindre.", parse_mode='Markdown')
            return

        game['players'].append(user_id)
        game['players_info'][user_id] = {'first_name': user_first_name}
        save_data(global_data)
        logger.info(f"Joueur ajouté: user_id={user_id}, game_id={game_id}, joueurs={game['players']}")

        bot.send_message(user_id, "🎉 Tu as *rejoint la partie* ! En attente de l'hôte pour commencer… 😏", parse_mode='Markdown')
        bot.send_message(
            game['host'],
            f"🥳 Ton partenaire {user_mention} a rejoint la partie !\nClique sur le bouton ci-dessous pour démarrer le jeu :",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Démarrer la partie", callback_data=f"start_game_{game_id}")]
            ])
        )
        return

    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("🎲 Jouer en solo", callback_data="solo"),
        InlineKeyboardButton("👥 Jouer à deux", callback_data="multiplayer")
    )
    bot.send_message(user_id, "✨ Bienvenue dans *Hot & Curious* 🔥\nChoisis un mode de jeu :", parse_mode='Markdown', reply_markup=markup)

# --- DÉBUT DE PARTIE MULTIJOUEUR ---
@bot.callback_query_handler(func=lambda call: call.data == "multiplayer")
def multiplayer_mode(call):
    user_id = call.from_user.id
    user_first_name = call.from_user.first_name if call.from_user.first_name else "Hôte"

    for gid, game in pending_games.items():
        if game['host'] == user_id and not game['active'] and len(game['players']) < 2:
            bot.send_message(user_id, f"Tu as déjà une partie en attente ! Partage ce lien :\n`https://t.me/{bot_username}?start=join_{gid}`", parse_mode='Markdown')
            bot.answer_callback_query(call.id, "Tu as déjà une partie en cours de création.")
            return

    game_id = str(uuid.uuid4())
    pending_games[game_id] = {
        'host': user_id,
        'players': [user_id],
        'players_info': {user_id: {'first_name': user_first_name}},
        'current_chooser_idx': 0,
        'current_responder_id': None,
        'current_question_message_ids': [],
        'active': False,
        'messages': []
    }
    save_data(global_data)

    invite_link = f"https://t.me/{bot_username}?start=join_{game_id}"
    bot.send_message(user_id, f"🔗 Envoie ce lien à ton/ta partenaire pour qu'il/elle rejoigne la partie :\n`{invite_link}`\n\n_Tu peux aussi cliquer sur le lien toi-même pour le copier facilement._", parse_mode='Markdown')
    bot.answer_callback_query(call.id, "Partie multijoueur créée !")
    logger.info(f"Partie multijoueur créée: game_id={game_id} par user_id={user_id}")


# --- START MULTIPLAYER GAME ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("start_game_"))
def start_multiplayer_game(call):
    user_id = call.from_user.id
    game_id = call.data.split("_")[2]

    if game_id not in pending_games or pending_games[game_id]['host'] != user_id:
        bot.send_message(user_id, "🚫 Tu n'es pas l'hôte de cette partie ou la partie n'existe plus.", parse_mode='Markdown')
        bot.answer_callback_query(call.id, "Action non autorisée.")
        return

    game = pending_games[game_id]
    if len(game['players']) != 2:
        bot.send_message(user_id, "⚠️ Attends que ton partenaire rejoigne la partie avant de la démarrer !", parse_mode='Markdown')
        bot.answer_callback_query(call.id, "Partenaire manquant.")
        return

    game['active'] = True
    save_data(global_data)

    # --- FEEDBACK VISUEL : STICKER POUR LE DÉBUT DE PARTIE ---
    for player_id in game['players']:
        if STICKER_PARTY_STARTED and STICKER_PARTY_STARTED != "CAACAgIAAxkBAAIDvWc_t-Z...": # Vérifie si l'ID a été mis à jour
            try:
                bot.send_sticker(player_id, STICKER_PARTY_STARTED)
            except telebot.apihelper.ApiTelegramException as e:
                logger.warning(f"Impossible d'envoyer le sticker {STICKER_PARTY_STARTED} à {player_id}: {e}")
        bot.send_message(player_id, "🎉 *La partie commence !* Amusez-vous bien ! 🔥", parse_mode='Markdown')

    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except telebot.apihelper.ApiTelegramException:
        pass

    chooser_id = game['players'][game['current_chooser_idx']]
    chooser_first_name = game['players_info'].get(chooser_id, {}).get('first_name', 'quelqu\'un')
    chooser_mention = f"[{chooser_first_name}](tg://user?id={chooser_id})"
    
    msg_chooser = bot.send_message(
        chooser_id,
        f"🎯 C'est à *{chooser_mention}* de choisir la première catégorie !", # Emoji amélioré
        parse_mode='Markdown',
        reply_markup=create_category_menu()
    )
    game['messages'].append((chooser_id, msg_chooser.message_id))
    
    other_player_id = game['players'][1 - game['current_chooser_idx']]
    msg_other = bot.send_message(
        other_player_id,
        f"C'est au tour de {chooser_mention} de choisir la catégorie. Prépare-toi à répondre ! 💭", # Emoji amélioré
        parse_mode='Markdown',
        reply_markup=create_end_game_button()
    )
    game['messages'].append((other_player_id, msg_other.message_id))
    
    bot.answer_callback_query(call.id, "Partie lancée !")
    logger.info(f"Partie {game_id} lancée par host {user_id}")


# --- SÉLECTION DE CATÉGORIE ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("category_"))
def select_category(call):
    user_id = call.from_user.id
    game_id, game = get_game_by_user(user_id)

    if not game_id:
        bot.send_message(user_id, "🚫 Tu n'es pas dans une partie active.", parse_mode='Markdown')
        bot.answer_callback_query(call.id, "Pas de partie active.")
        return

    if not game['active']:
        bot.send_message(user_id, "🚫 Cette partie n'a pas encore été démarrée par l'hôte.", parse_mode='Markdown')
        bot.answer_callback_query(call.id, "Partie non démarrée.")
        return

    chooser_id = game['players'][game['current_chooser_idx']]
    if user_id != chooser_id:
        bot.send_message(user_id, "⛔ Ce n'est *pas ton tour* de choisir la catégorie !", parse_mode='Markdown')
        bot.answer_callback_query(call.id, "Ce n'est pas ton tour.")
        return

    category = call.data.replace("category_", "")
    if category not in questions:
        bot.send_message(user_id, "🤔 Catégorie invalide. Veuillez réessayer.", parse_mode='Markdown')
        bot.answer_callback_query(call.id, "Catégorie inconnue.")
        return

    question = random.choice(questions[category])
    
    # Déterminer le répondeur (l'autre joueur)
    responder_idx = 1 - game['current_chooser_idx']
    responder_id = game['players'][responder_idx]
    responder_first_name = game['players_info'].get(responder_id, {}).get('first_name', 'quelqu\'un')
    responder_mention = f"[{responder_first_name}](tg://user?id={responder_id})"

    for chat_id, msg_id in game['current_question_message_ids']:
        try:
            bot.delete_message(chat_id, msg_id)
        except telebot.apihelper.ApiTelegramException:
            pass
    game['current_question_message_ids'] = []

    # --- FEEDBACK VISUEL : EMOJIS POUR LA QUESTION SELON LA CATÉGORIE ---
    category_emoji = {
        "Icebreaker Fun": "✨",
        "Deep & Curious": "🤔",
        "Flirty & Cheeky": "😏",
        "Hot & Spicy": "🌶️🔥",
        "Dare Time": "😈"
    }.get(category, "❓") # Emoji par défaut si catégorie non trouvée

    msg_text = f"{category_emoji} *Catégorie : {category}*\n\n❓ *Question :* {question}\n\n👉 C'est à *{responder_mention}* de répondre à cette question !"
    
    for player_id in game['players']:
        msg = bot.send_message(
            player_id,
            msg_text,
            parse_mode='Markdown',
            reply_markup=ForceReply() if player_id == responder_id else create_end_game_button()
        )
        game['current_question_message_ids'].append((player_id, msg.message_id))
        game['messages'].append((player_id, msg.message_id))

    game['current_responder_id'] = responder_id
    game['current_chooser_idx'] = responder_idx

    save_data(global_data)

    bot.answer_callback_query(call.id, "Question envoyée !")
    logger.info(f"Partie {game_id}: question '{question}' envoyée à {responder_id}")
    
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except telebot.apihelper.ApiTelegramException:
        pass


# --- GESTION DES RÉPONSES AUX QUESTIONS (Messages texte et média) ---
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'video', 'voice', 'audio', 'document'])
def handle_player_response(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    game_id, game = get_game_by_user(user_id)

    is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id

    if not game_id or not game['active'] or game['current_responder_id'] != user_id or not is_reply_to_bot:
        return

    responder_first_name = message.from_user.first_name if message.from_user.first_name else "Quelqu'un"
    responder_mention = f"[{responder_first_name}](tg://user?id={user_id})"
    
    # --- FEEDBACK SONORE : ENVOI DU VOCAL DE NOTIFICATION ---
    for player_id in game['players']:
        try:
            # Envoie le vocal de notification (même s'il est vide)
            if VOICE_TURN_NOTIFICATION and VOICE_TURN_NOTIFICATION != "AwACAgIAAxkBAAIDyWc_uAb...": # Vérifie si l'ID a été mis à jour
                bot.send_voice(player_id, VOICE_TURN_NOTIFICATION)
        except telebot.apihelper.ApiTelegramException as e:
            logger.warning(f"Impossible d'envoyer la notification vocale {VOICE_TURN_NOTIFICATION} à {player_id}: {e}")

        # --- FEEDBACK VISUEL : EMOJI POUR LA RÉPONSE + TRANSFÈRE ---
        bot.send_message(player_id, f"Réponse de {responder_mention} : 💌✅", parse_mode='Markdown') # Emoji amélioré
        bot.forward_message(
            chat_id=player_id,
            from_chat_id=chat_id,
            message_id=message.message_id
        )

    for c_id, m_id in game['current_question_message_ids']:
        try:
            bot.delete_message(c_id, m_id)
        except telebot.apihelper.ApiTelegramException:
            pass
    game['current_question_message_ids'] = []
    game['current_responder_id'] = None

    next_chooser_id = game['players'][game['current_chooser_idx']]
    next_chooser_first_name = game['players_info'].get(next_chooser_id, {}).get('first_name', 'quelqu\'un')
    next_chooser_mention = f"[{next_chooser_first_name}](tg://user?id={next_chooser_id})"

    msg_chooser_prompt = bot.send_message(
        next_chooser_id,
        f"🎯 C'est maintenant au tour de *{next_chooser_mention}* de choisir la prochaine catégorie !",
        parse_mode='Markdown',
        reply_markup=create_category_menu()
    )
    game['messages'].append((next_chooser_id, msg_chooser_prompt.message_id))
    
    other_player_id = game['players'][1 - game['current_chooser_idx']]
    msg_other_info = bot.send_message(
        other_player_id,
        f"*{next_chooser_mention}* est en train de choisir la prochaine question. Prépare-toi pour la prochaine ! ⏳", # Emoji amélioré
        parse_mode='Markdown',
        reply_markup=create_end_game_button()
    )
    game['messages'].append((other_player_id, msg_other_info.message_id))
    
    save_data(global_data)
    logger.info(f"Partie {game_id}: Réponse de {user_id} traitée. Prochain à choisir: {next_chooser_id}")


# --- FIN DE PARTIE ---
@bot.callback_query_handler(func=lambda call: call.data == "end_game")
def end_game(call):
    user_id = call.from_user.id
    game_id, game = get_game_by_user(user_id)

    if not game_id:
        bot.send_message(user_id, "ℹ️ Tu n'es pas dans une partie active à terminer.", parse_mode='Markdown')
        bot.answer_callback_query(call.id, "Pas de partie à terminer.")
        return

    for player_id in game['players']:
        bot.send_message(player_id, "👋 La partie est *terminée* ! Merci d'avoir joué à Hot & Curious 🔥\n\nN'hésitez pas à démarrer une nouvelle partie quand vous voulez !", parse_mode='Markdown')
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except telebot.apihelper.ApiTelegramException:
            pass

    delete_game_messages(game_id)
    bot.answer_callback_query(call.id, "Partie terminée !")
    logger.info(f"Partie {game_id} terminée par user {user_id}.")


# --- DÉBUT DE PARTIE SOLO ---
@bot.callback_query_handler(func=lambda call: call.data == "solo")
def solo_mode(call):
    user_id = call.from_user.id
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for category in questions.keys():
        markup.add(InlineKeyboardButton(category, callback_data=f"solo_category_{category}"))
    bot.send_message(user_id, "📚 Choisis une catégorie pour ta question solo :", parse_mode='Markdown', reply_markup=markup)
    bot.answer_callback_query(call.id)

# --- SÉLECTION DE NIVEAU SOLO ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("solo_category_"))
def select_solo_category(call):
    user_id = call.from_user.id
    category = call.data.replace("solo_category_", "")
    if category not in questions:
        bot.send_message(user_id, "🤔 Catégorie invalide. Veuillez réessayer.", parse_mode='Markdown')
        bot.answer_callback_query(call.id, "Catégorie inconnue.")
        return
    question = random.choice(questions[category])

    # --- FEEDBACK VISUEL : EMOJIS POUR LA QUESTION SOLO ---
    category_emoji = {
        "Icebreaker Fun": "✨",
        "Deep & Curious": "🤔",
        "Flirty & Cheeky": "😏",
        "Hot & Spicy": "🌶️🔥",
        "Dare Time": "😈"
    }.get(category, "❓")

    bot.send_message(user_id, f"{category_emoji} *Catégorie : {category}*\n\n❓ *Question :* {question}\n\n_Réfléchis bien à ta réponse !_ 😉", parse_mode='Markdown')
    
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for cat in questions.keys():
        markup.add(InlineKeyboardButton(cat, callback_data=f"solo_category_{cat}"))
    bot.send_message(user_id, "Envie d'une autre question ? Choisis une autre catégorie :", reply_markup=markup)
    bot.answer_callback_query(call.id, "Question solo générée.")


# --- FLASK WEBHOOK ---
@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_data = request.get_json(force=True)
        if not json_data:
            logger.warning("Webhook: JSON vide ou invalide reçu.")
            return '', 200

        try:
            update = telebot.types.Update.de_json(json_data)
            
            if not hasattr(update, 'update_id'):
                logger.warning("Webhook: Update sans 'update_id'. Ignoré.")
                return '', 200

            if update.update_id in processed_updates:
                logger.info(f"Skipping duplicate update: update_id={update.update_id}")
                return '', 200
            
            processed_updates.add(update.update_id)
            if len(processed_updates) > 1000:
                sorted_updates = sorted(list(processed_updates), reverse=True)[:1000]
                processed_updates.clear()
                processed_updates.update(sorted_updates)

            global_data['processed_updates'] = list(processed_updates)
            save_data(global_data)

            bot.process_new_updates([update])
            logger.info(f"Update {update.update_id} traitée avec succès.")
            return '', 200
        except Exception as e:
            logger.error(f"Erreur lors du traitement du webhook: {e}", exc_info=True)
            return '', 500
    else:
        logger.warning(f"Webhook: Requête avec Content-Type inattendu: {request.headers.get('content-type')}")
        return '', 403


@app.route('/')
def index():
    return 'Bot Hot & Curious est en ligne !'

if __name__ == "__main__":
    logger.info("Démarrage du bot...")
    try:
        bot.remove_webhook()
        bot.set_webhook(url=WEBHOOK_URL)
        logger.info(f"Webhook défini sur : {WEBHOOK_URL}")
    except telebot.apihelper.ApiTelegramException as e:
        logger.critical(f"Impossible de définir le webhook : {e}. Vérifiez l'URL et le token.")
        exit(1)

    port = int(os.environ.get("PORT", 10000))
    logger.info(f"Lancement de l'application Flask sur le port {port}...")
    app.run(host="0.0.0.0", port=port)
