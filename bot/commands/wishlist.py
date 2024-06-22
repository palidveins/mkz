from api.conta import Conta
from api.carta import Carta
from api.wishlist import *
from telegram.ext import (
    Updater,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup  # noqa: F811

INICIAR, DAR_NOME_WL, CARTAS_PARA_WL = range(3)

infos = []

class Formatar:
    def formatar_lista():
        return True

    def formatar_mensagem_final():
        return True

    def formatar_wishlists(json):
        if len(json['wishlists']) < 1:
            return "<i>Você ainda não tem nenhuma lista. Que tal criar uma com <code>/cwl</code> ?</i>"
        usuario_id = json['wishlists'][0]['user_id']
        total_listas = len(json['wishlists'])
        listagem = f"👤 Usuário: [<code>{usuario_id}</code>]\n🔢 Total: <code>{total_listas}</code>\n\n"
        for lista in json['wishlists']:
            listagem += f"<code>{lista['WishlistID']}</code>. <strong>{lista['nome']}</strong>\n"
        return listagem

async def nomear_wl(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    n = update.message.from_user.first_name
    infos.append(update.message.text)
    await update.message.reply_text("Nome bonito, nome formoso! Agora, me envie até 30 IDs que você esteja procurando, em formato de lista separado por espaço.\n⚠️ Mas atenção! Apenas 10 deles podem ser de pães que você já tem.")
    return CARTAS_PARA_WL

async def inserir_cartas_wl(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    n = update.message.from_user.first_name
    cartas = update.message.text.split()
    if len(cartas) > 30:
        await update.message.reply_text("Você pode inserir somente 30 ingredientes. Tente novamente!")
        return ConversationHandler.END
    for carta in cartas:
        c = Carta.buscar_carta(carta, user_id)
        if "Nenhuma carta" in c['message']:
            await update.message.reply_text("Tem algum ID aí que não existe. Verifique se está tudo certinho, ok? Você pode tentar novamente.")
            return ConversationHandler.END
    
    n_id = Wishlist.criar_wishlist(user_id, infos[0])['retorno']['WishlistID']
    c_inseridas = Wishlist.inserir_item_wishlist(user_id, n_id, cartas)
    await update.message.reply_text(f"🆔 Wishlist ID: <code>{n_id}</code>\n🥞 Ingredientes: <code>{len(cartas)}</code>\n\nVocê pode ver os itens da lista com <code>/wl {n_id}</code>.", reply_markup="HTML")
    return ConversationHandler.END

async def criar_wl(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    n = update.message.from_user.first_name
    
    if update.message.chat.type != "private":
        await update.message.reply_text("Você não pode utilizar esse comando aqui. Somente no privado.")
        return

    premium = Conta.buscar_usuario(user_id)['premium']
    quantidade_wl = len(Wishlist.wishlists_usuario(user_id)['wishlists'])

    if premium != True and quantidade_wl >= 1:
        print(1) # TODO: impedir de criar mais de uma lista, pois, o usuário não é premium.
        await update.message.reply_text("<i>Infelizmente, o limite de criação de wishlist é 1. Considere fazer uma pequena doação para obter até 5 wishlists!</i>", parse_mode="HTML")
        return
    elif premium and quantidade_wl == 5:
        await update.message.reply_text("<i>Você é doador, não o Papa. Seu limite de wishlist foi atingido.</i>", parse_mode="HTML")
        return

    elif premium and quantidade_wl < 5:
        await update.message.reply_text("😼 Eba, vamos criar uma lista de compras! 📝\nPrimeiro de tudo, preciso que você me envie o nome da wishlist.", parse_mode="HTML")
        return DAR_NOME_WL
    elif premium != True and quantidade_wl < 1:
        await update.message.reply_text("😼 Eba, vamos criar uma lista de compras! 📝\nPrimeiro de tudo, preciso que você me envie o nome da wishlist.", parse_mode="HTML")
        return DAR_NOME_WL

# precisa paginar a porra da listaaaaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
async def buscar_wl(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    n = update.message.from_user.first_name

async def listar_wl(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    n = update.message.from_user.first_name
    # aqui não precisa paginar
    listado = Wishlist.wishlists_usuario(user_id)
    txt = Formatar.formatar_wishlists(listado)
    botao = [
    [
        InlineKeyboardButton("➕ Adicionar", callback_data="add_itens_wl"),
        InlineKeyboardButton("➖ Excluir", callback_data="rm_itens_wl")
    ],
    [
        InlineKeyboardButton("🗑 Deletar lista", callback_data="delete_wl"),
    ],
    ]
    teclado = InlineKeyboardMarkup(botao)

    await update.message.reply_text(txt, parse_mode="HTML", reply_markup=teclado)
