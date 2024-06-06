from api.conta import Conta
from api.carta import Carta
from telegram.ext import Updater, ContextTypes, CallbackContext, ConversationHandler
import json
from utils.file_size import tamanho_arquivo_aceitavel

STATE_WAITING = 1
job = ""

with open('config.json', 'r') as arquivo:
    dados_json = json.load(arquivo)

async def cancelar_gif(context: CallbackContext):
    chat = context.job
    await context.bot.send_message(chat_id=chat.chat_id, text="Bem, como você não me enviou a tempo o gif, eu cancelei a ação. Mas você pode tentar novamente. :)")
    return ConversationHandler.END

async def setar(update: Updater, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    global card_selected
    card_selected = Carta.buscar_carta(context.args[0], user_id)

    if "Nenhuma carta foi encontrada com esse ID." in card_selected['message']:
        await update.message.reply_text(reply_to_message_id=update.message.message_id, text="Irmão, essa carta sequer existe. Verifique pesquisando por ela.")
        return ConversationHandler.END

    if card_selected['quantidade_acumulada'] < 40:
        await update.message.reply_text(reply_to_message_id=update.message.message_id, text="<i>Infelizmente, você não possui a quantidade de cartas suficientes para ter um gif personalizado. Considere girar/trocar para atingir a meta!</i>", parse_mode="HTML")
        return ConversationHandler.END
    else:
        global job
        job = context.job_queue.run_once(cancelar_gif, 10, update.message.chat_id, chat_id=update.message.chat_id)
        await update.message.reply_text(reply_to_message_id=update.message.message_id, text="Ebaa! Você tem o suficiente. Agora, me envie em até <strong>1 minuto</strong> o link do gif desejado. Lembrando que ele precisa seguir as regras!", parse_mode="HTML")
        return STATE_WAITING

async def processar_gif(context: CallbackContext, sus=1):
    job.schedule_removal()
    if tamanho_arquivo_aceitavel(context.message.text):
        try:
            lnk = context.message.link_preview_options.url
            user = context.message.from_user.id
            pedido = Conta.criar_pedido_gif(user, context.message.message_id, card_selected['carta']['ID'], lnk)
            txt = f"Pedido #{pedido['mensagem']['id_pedido']}\n\nUser: {pedido['mensagem']['user_id']}\nCarta ID: {pedido['mensagem']['carta_id']}\nGif Link: {pedido['mensagem']['gif_link']}"
            await context._bot.send_message(chat_id=dados_json['aprovar_gif'], text=txt)         
            await context.message.reply_text(text="Gif recebido com sucesso! Aguarde o retorno.")
        except:
            await context.message.reply_text("Ocorreu um erro na tentativa de criar o pedido. Reporte para a administração ou @naftalino (De forma detalhada!).")
    else:
         await context.message.reply_text(text="Erro: verifique se o gif atende as regras. Ação cancelada.")
    return ConversationHandler.END
