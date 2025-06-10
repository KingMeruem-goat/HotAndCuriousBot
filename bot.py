import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random

# Remplace par ton vrai token ici
TOKEN = '7771606520:AAFp9ZonHi-MSgi1Jah_M9KmrgGKzH9v_Lk'
bot = telebot.TeleBot(TOKEN)

# Structure des questions
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
        "Que portes-tu généralement quand tu es seul.e à la maison ?",
        "Quel est le plus long message sexy que tu as déjà envoyé ?",
        "Quelle partie de mon corps as-tu le plus envie de découvrir en vrai ?",
        "Préfères-tu un strip-tease par visio ou un vocal très explicite ?",
        "Quelle est ta plus grande tentation quand tu me regardes à l’écran ?",
        "M’enverrais-tu une photo sexy si je te le demande gentiment ?",
        "Quel mot ou geste de ma part pourrait te rendre fou/folle même à distance ?",
        "T’as déjà fantasmé en plein appel vidéo ?"
    ],
    "Hot & Spicy": [
        "Décris-moi un fantasme qu’on pourrait réaliser même à distance.",
        "Tu m’envoies un vocal en murmurant une envie ?",
        "Si je te proposais un strip visio à tour de rôle, tu serais partant(e) ?",
        "Quelle est la chose la plus coquine que tu aies faite au téléphone ou en appel ?",
        "Quel est ton fantasme le plus réaliste à réaliser en ligne ?",
        "Si je te dis “on fait un jeu coquin par audio ce soir”, tu dis quoi ?",
        "Quel est le moment de la journée où tu es le plus chaud/chaude ?",
        "As-tu déjà joué avec toi-même en pensant à moi ? Raconte sans tabou.",
        "Que dirais-tu si je te proposais un appel vidéo torride maintenant ?",
        "Tu préfères me regarder ou m’écouter pendant un moment très hot ?","Quel est le truc le plus coquin que tu pourrais faire avec un objet près de toi ?",
        "Tu m’envoies un message audio sexy maintenant ? (ose 😈)",
        "T’as déjà fantasmé sur ce qu’on ferait si on était dans le même lit ce soir ?",
        "Envoie-moi une phrase hot que tu voudrais me dire les yeux dans les yeux."
    ],
    "Dare Time": [
        "Envoie une photo d’un endroit de ton corps que j’adore (sans montrer le visage).",
        "Enregistre un audio très très lent où tu dis ce que tu ferais si j’étais là.",
        "Vidéo de toi qui dis quelque chose de chaud avec un regard de tueur/tueuse.",
        "Choisis un mot, et chaque fois que tu l’entends aujourd’hui, tu penses à moi tout nu(e).",
        "Envoie un vocal où tu gémis discrètement pendant 10 secondes.",
        "Fais un strip-tease d’une pièce (ou deux) à la caméra.",
        "Envoie un selfie à moitié couvert.e (laisse deviner le reste).",
        "Écris une mini-histoire érotique avec nos deux prénoms.",
        "Envoie un message audio de 20 secondes où tu expliques ce que tu veux me faire.",
        "Simule un orgasme (avec ou sans caméra).",
        "Envoie-moi la photo de l’objet que tu utiliserais pour te donner du plaisir.",
        "Montre-moi (en photo ou en cam) ta tenue de “séduction maison”.",
        "Donne-moi un gage sexy à faire, et je dois l’exécuter aussi.",
        "Appelle-moi et dis-moi 3 fantasmes que tu veux réaliser avec moi.",
        "Envoie-moi une capture d’écran de ta dernière recherche coquine sur Google.",
        "Simule un rendez-vous coquin à distance pendant 1 minute en vocal.",
        "Mets une musique sexy et fais une mini danse pour moi (vidéo ou live).",
        "Envoie-moi un message hot que je devrais lire tout haut devant toi.",
        "Pendant les 5 prochaines minutes, réponds à tout ce que je dis avec une voix sensuelle."
    ]
}

# Stockage des parties
games = {}

# Start
@bot.message_handler(commands=['start'])
def start_game(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("👤 Solo", callback_data='solo'))
    markup.add(InlineKeyboardButton("👥 Multijoueur", callback_data='multi'))
    bot.send_message(message.chat.id, "Bienvenue dans *Hot & Curious* 🔥\n\nChoisis ton mode de jeu :", reply_markup=markup, parse_mode='Markdown')

# Choix de mode
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'solo':
        choose_level(call.message, call.message.chat.id)
    elif call.data == 'multi':
        games[call.message.chat.id] = {'players': [call.message.chat.id], 'turn': 0}
        bot.send_message(call.message.chat.id, "🔗 Envoie ce message à ton/ta partenaire pour qu’il/elle clique dessus et rejoigne :")
        bot.send_message(call.message.chat.id, f"https://t.me/{bot.get_me().username}?start={call.message.chat.id}")
    elif call.data in questions:
        q = random.choice(questions[call.data])
        bot.send_message(call.message.chat.id, f"🃏 *{call.data}*\n\n{q}", parse_mode='Markdown')

def choose_level(msg, chat_id):
    markup = InlineKeyboardMarkup()
    for level in questions:
        markup.add(InlineKeyboardButton(level, callback_data=level))
    bot.send_message(chat_id, "🧩 Choisis ton niveau :", reply_markup=markup)

@bot.message_handler(commands=['start'])
def handle_join(message):
    args = message.text.split()
    if len(args) > 1:
        host_id = int(args[1])
        if host_id in games:
            games[host_id]['players'].append(message.chat.id)
            bot.send_message(message.chat.id, "Tu as rejoint la partie ! 🎉")
            start_multiplayer_game(host_id)
        else:
            bot.send_message(message.chat.id, "Lien invalide ou expiré.")
    else:
        start_game(message)

def start_multiplayer_game(host_id):
    players = games[host_id]['players']
    for pid in players:
        bot.send_message(pid, "🎮 La partie commence ! On pioche une carte à tour de rôle.")
    ask_next_question(host_id)

def ask_next_question(host_id):
    game = games[host_id]player = game['players'][game['turn'] % len(game['players'])]
    level = random.choice(list(questions.keys()))
    q = random.choice(questions[level])
    bot.send_message(player, f"🃏 *{level}*\n\n{q}", parse_mode='Markdown')
    game['turn'] += 1

# Boucle
bot.infinity_polling()
