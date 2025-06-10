import os
import random
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request

# === CONFIGURATION ===
TOKEN = "7771606520:AAFp9ZonHi-MSgi1Jah_M9KmrgGKzH9v_Lk"
bot = telebot.TeleBot(TOKEN, threaded=False)
bot_username = bot.get_me().username
WEBHOOK_URL = f"https://hotandcuriousbot.onrender.com/{TOKEN}"  # remplace par ton URL Render

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
        "Écris une mini‑histoire érotique avec nos prénoms.",
        "Envoie un message audio de 20 secondes où tu expliques ce que tu veux me faire.",
        "Simule un orgasme (avec ou sans caméra).",
        "Envoie une photo de l’objet que tu utiliserais pour te donner du plaisir.",
        "Montre ta tenue de “séduction maison” (photo ou cam).",
        "Donne-moi un gage sexy à faire, et je l’exécuterai aussi.",
        "Appelle-moi et dis-moi 3 fantasmes que tu veux réaliser avec moi.",
        "Envoie une capture d’écran de ta dernière recherche coquine sur Google.",
        "Simule un rendez-vous coquin à distance pendant 1 min en vocal.",
        "Mets une musique sexy et fais une mini danse pour moi (vidéo/live).",
        "Envoie un message hot que je devrai lire à haute voix.",
        "Pendant 5 minutes, réponds à tout ce que je dis avec une voix sensuelle."
    ]
}

# === GESTION DES SESSIONS ===
waiting = {}       # user_id -> (mode="solo"/"duo", category)
active = {}        # user_id -> (partner_id_opt, category, index)

# === COMMANDE /START ===
@bot.message_handler(commands=["start"])
def cmd_start(message):
    user = message.from_user.id
    args = message.text.split()
    if len(args) > 1:
        sid = args[1]
        # Rejoindre session duo
        for uid, sess in active.items():
            pass  # n'utilisé : on recrée ci‑dessous
        if sid in waiting and waiting[sid][0] == "duo":
            mode, cat = waiting.pop(sid)
            partner = int(sid)
            # initialiser sessions actives
            active[user] = (partner, cat, 0)
            active[partner] = (user, cat, 0)
            bot.send_message(user, "✅ Tu as rejoint ! Le jeu commence...")
            bot.send_message(partner, "✅ Partenaire arrivé ! Lancement...")
            send_question_to_pair(user, cat, 0)
            return

    # Sinon : menu principal
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🎲 Solo", callback_data="solo"),
        InlineKeyboardButton("👥 À deux", callback_data="duo"),
    )
    bot.send_message(user, "Mode de jeu ?", reply_markup=markup)

# === CALLBACKS BOUTONS ===
@bot.callback_query_handler(func=lambda c: True)
def btn_handler(call):
    uid = call.from_user.id
    data = call.data

    if data == "solo":
        markup = InlineKeyboardMarkup()
        for cat in questions:
            markup.add(InlineKeyboardButton(cat, callback_data=f"solo|{cat}"))
        bot.send_message(uid, "Choisis ton niveau :", reply_markup=markup)

    elif data == "duo":
        # mets en attente et envoie lien avec ton user_id
        waiting[str(uid)] = ("duo", None)
        link = f"https://t.me/{bot_username}?start={uid}"
        bot.send_message(uid, f"En attente d'un joueur…\nEnvoie ce lien à quelqu’un :\n{link}")

    elif "|" in data:
        m, cat = data.split("|", 1)
        if m == "solo":
            send_question_single(uid, cat)
        elif m == "duo":
            # attendre 2ème + lancer partie
            waiting[str(uid)] = ("duo", cat)

    elif data == "next":
        if uid in active:
            partner, cat, idx = active[uid]
            idx += 1
            active[uid] = (partner, cat, idx)
            active[partner] = (uid, cat, idx)
            send_question_to_pair(uid, cat, idx)

def send_question_single(uid, category):
    q = random.choice(questions[category])
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Question suivante", callback_data="next"))
    bot.send_message(uid, f"🎯 {category} :\n{q}", reply_markup=markup)

def send_question_to_pair(uid, category, idx):
    q = random.choice(questions[category])
    partner, _, _ = active[uid]
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Question suivante", callback_data="next"))
    bot.send_message(uid, f"🎯 {category} :\n{q}", reply_markup=markup)
    bot.send_message(partner, f"🎯 {category} :\n{q}", reply_markup=markup)

# === Webhook & FLASK ===
@app.route(f"/{TOKEN}", methods=["POST"])
def site_webhook():
    update = telebot.types.Update.de_json(request.data.decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "Bot en ligne 😊", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
