from api.conta import Conta
from telegram.ext import Updater, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup  # noqa: F811

async def girar_handler(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type != "private":
        return
    else:
        user_id = update.message.from_user.id
        giros_conta = Conta.buscar_usuario(user_id)["giros"]
        if giros_conta > 0:
            Conta.remover_giro(user_id)
            texto_girar = f"""
🧺 Olá, {update.message.chat.first_name}! Tudo pronto para ir às compras? 

<i>Você tem <strong>{giros_conta - 1}</strong> de <strong>12</strong> pedidos restantes.</i>

🗳 Escolha algo da prateleira:
        """
            botao = [
    [
        InlineKeyboardButton("🍞 Panetunes", callback_data="Sortear_Música"),
        InlineKeyboardButton("🥣 Sereais", callback_data="Sortear_Série")
    ],
    [
        InlineKeyboardButton("🥖 Animapão", callback_data="Sortear_Animação"),
        InlineKeyboardButton("🍔 Burgames", callback_data="Sortear_Jogo")
    ],
    [
        InlineKeyboardButton("🧁 Muffilmes", callback_data="Sortear_Filme"),
        InlineKeyboardButton("🥪 Misto", callback_data="Sortear_Multi")
    ],
    ]
            teclado = InlineKeyboardMarkup(botao)

            padaria_img = "https://lh3.googleusercontent.com/u/0/drive-viewer/AKGpiha1-i6iYVuCpEGxzSp9W0N1YCkqvQob-YljDBuxSGzfj4MUTE1cLroe48H0g_mtiuyFLPmOSBzNVpiLWgfZBcKyTcao10WEpw0=w1280-h658"
            await update.message.reply_animation(padaria_img, caption=texto_girar, reply_markup=teclado, parse_mode="html")
        else:
            await update.message.reply_text(
                reply_to_message_id=update.message.message_id, text="<i><strong>A farinha de trigo está em falta.. Volte mais tarde!</strong></i>",
                parse_mode="html"
            )
