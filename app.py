from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters, CallbackQueryHandler
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import threading
import json
import random
import logging
import asyncio

# Configuração do Flask
app = Flask(__name__)
CORS(app)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dicionários para armazenar os dados
referral_counts = {}
referrals = {}
used_referrals = {}
ad_counts = {}

# Configuração do Application
application = Application.builder().token('7707517421:AAGMYveOkr8gOgGKLOw8TFvSEsuLjtlJS3k').build()

# Configuração do banco de dados SQLite
def setup_db():
    conn = sqlite3.connect('saldos.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                     id INTEGER PRIMARY KEY,
                     saldo REAL DEFAULT 0.0
                 )''')
    conn.commit()
    conn.close()

# Função para adicionar um novo usuário ao banco de dados
def add_user(user_id):
    conn = sqlite3.connect('saldos.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

# Função para atualizar o saldo de um usuário
def update_balance(user_id, amount):
    conn = sqlite3.connect('saldos.db')
    c = conn.cursor()
    c.execute('UPDATE users SET saldo = saldo + ? WHERE id = ?', (amount, user_id))
    conn.commit()
    conn.close()

# Função para obter o saldo de um usuário
def get_balance(user_id):
    conn = sqlite3.connect('saldos.db')
    c = conn.cursor()
    c.execute('SELECT saldo FROM users WHERE id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0.0

# Função para formatar valor monetário
def format_currency(value):
    return f'R$ {value:.2f}'.replace('.', ',')

# Função para adicionar saldo a um usuário pelo administrador
async def add_saldo(update: Update, context: CallbackContext):
    if update.message.from_user.id != 1437993955:
        await update.message.reply_text("Você não tem permissão para usar este comando.")
        return

    try:
        user_id = int(context.args[0])
        amount = float(context.args[1])
    except (IndexError, ValueError):
        await update.message.reply_text("Uso: /add_saldo <user_id> <amount>")
        return

    add_user(user_id)
    update_balance(user_id, amount)
    await update.message.reply_text(f"Saldo de {format_currency(amount)} adicionado ao usuário {user_id}.")

# Função para iniciar o menu com botões inline
async def menu_bot(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    add_user(user_id)  # Adicionar usuário ao banco de dados
    message_text = (
        f'Olá {user_name}, seja bem-vindo ao AD PLAYY APP!\n'
    )
    image_url = 'https://www.bing.com/images/create/python2c-bot2c-and-telegram/1-66c3500df3d044319734bfed00a995e1?id=GIu3w%2BdeCA5t934ZF2Q8Ww.N9isGUKWkWp7MjIdcyBKUA&view=detailv2&idpp=genimg&idpclose=1&thid=OIG3.BEU6uVgYA.RQcu.T4QVz&skey=aK4prDKbfdHzR-38wpcRfT1Y_k5oV9fe1YATfQ8vYW8&form=SYDBIC&ssp=1&darkschemeovr=1&setlang=pt-br&cc=BR&safesearch=moderate'  # URL da imagem
    
    # Configuração dos botões inline com '👾 Painel Ad Pay App'
    keyboard_inline = [
        [InlineKeyboardButton("👾 Painel Ad Pay App", callback_data='painel_ad_pay_app')]
    ]
    reply_markup_inline = InlineKeyboardMarkup(keyboard_inline)

    # Envio da mensagem com a imagem e os botões inline
    await update.message.reply_photo(photo=image_url, caption=message_text, reply_markup=reply_markup_inline)

# Função para iniciar o teclado customizado (Reply Keyboard)
async def menu_customizado(update: Update, context: CallbackContext):
    # Configuração do teclado customizado com '▶️ Assistir anúncios' centralizado e os outros botões na linha abaixo
    keyboard_customizado = [
        ['▶️ Assistir anúncios'],  # Primeira linha com o botão centralizado
        ['📋 Menu do Bot', '🤝 Afiliados', '👥 Indicação'],  # Segunda linha com os outros botões
        ['⚙️ Outros', '💰 Saldo']  # Terceira linha com os demais botões
    ]
    reply_markup_customizado = ReplyKeyboardMarkup(keyboard_customizado, resize_keyboard=True)

    # Envio da mensagem com o teclado customizado
    await update.message.reply_text('Selecione uma opção:', reply_markup=reply_markup_customizado)

# Função para lidar com as ações dos botões inline
async def button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    # Tratar cada botão inline clicado
    if query.data == 'assistir_anuncios':
        message_text = "📊 Taxa de pagamento atual: R$ 0,12 a R$ 0,28 por anúncio\n\nClique no botão abaixo para começar a assistir aos anúncios\n👇🏽"
        keyboard_inline = [
            [InlineKeyboardButton("Assistir Anúncios", web_app=WebAppInfo(url=f'https://6693139e7ba079b061336837--chimerical-melomakarona-c9aafc.netlify.app/?user_id={query.from_user.id}'))]
        ]
        reply_markup_inline = InlineKeyboardMarkup(keyboard_inline)
        await query.edit_message_text(text=message_text, reply_markup=reply_markup_inline)
    elif query.data == 'afiliados':
        message_text = "🤝Olá, esses aqui são os afiliados do bot, que nos ajudam a mantê-lo funcionando corretamente:\n\n" \
                       "Acesse [este link](https://1wfwna.life/?open=register&p=1zhf) para realizar um rápido cadastro.\n" \
                       "Adicione este *CODIGO 6363834* ao entrar no site.\n" \
                       "Efetue um depósito no valor mínimo e faça qualquer aposta.\n" \
                       "Nós comprove no atendimeento FAQ, que adicionamos o *DOBRO* de saldo via Telegram.\n"

        image_url = 'https://static-pp.1win-cdn.com/promo-files-uploads/jjCDSvsC_2-mqwPC4YimbPjtB0-YxwVxDr6KX9OxdWOZNf76Da_vkTlVdoEua1l8lOFv4Yge6DFASGEm1N5hHQ0iImmRj-fuw8Vt.jpg'  # URL da imagem

        await query.message.reply_photo(photo=image_url, caption=message_text, parse_mode='Markdown')
    elif query.data == 'outros':
        ad_count = ad_counts.get(query.from_user.id, 0)
        message_text = f"⚙️ Outros\n\n" \
                       f"👥 Total de usuários: 9291\n" \
                       f"👀 Você assistiu a {ad_count} anúncios\n" \
                       f"💵 Total de fundos retirados: R$ 0"
        
        keyboard_inline = [
            [InlineKeyboardButton("💰 Histórico de Saques", callback_data='historico_saques')],
            [InlineKeyboardButton("📣 Notícias", callback_data='noticias')],
            [InlineKeyboardButton("📨 FAQ", callback_data='faq')],
            [InlineKeyboardButton("💬 Suporte", callback_data='suporte')]
        ]
        reply_markup_inline = InlineKeyboardMarkup(keyboard_inline)
        await query.edit_message_text(text=message_text, reply_markup=reply_markup_inline)
    elif query.data == 'historico_saques':
        message_text = "💰 Histórico de Saques\n\n" \
                       "Não há nada\n" \
                       "Você ainda não tem nenhuma operação para exibir."
        keyboard_inline = [
            [InlineKeyboardButton("📣 Notícias", callback_data='noticias')],
            [InlineKeyboardButton("📨 FAQ", callback_data='faq')],
            [InlineKeyboardButton("💬 Suporte", callback_data='suporte')]
        ]
        reply_markup_inline = InlineKeyboardMarkup(keyboard_inline)
        await query.edit_message_text(text=message_text, reply_markup=reply_markup_inline)
    elif query.data == 'noticias':
        await query.edit_message_text(text="Boa tarde!\n\n"
                                           "❌ Estamos enfrentando problemas com o hosting que, por sua vez, afetaram o banco de dados, resultando em falhas no funcionamento do bot.\n\n"
                                           "🔹A carga de vídeos foi completamente corrigida, incluindo a velocidade de upload\n"
                                           "🔹O sistema de referência foi restaurado (os valores das recompensas estão sendo creditados corretamente)\n"
                                           "🔹Os saldos de alguns usuários foram recalculados e corrigidos (foram encontrados erros)\n\n" 
                                           "Obrigado pela compreensão!")
    elif query.data == 'faq':
        message_text = (
            "1️⃣ O que é o EstrelaClip App?\n"
            "EstrelaClip App é um bot através do qual você pode assistir a anúncios e ganhar recompensas em dinheiro.\n\n"
            "2️⃣ Como eu ganho dinheiro usando o EstrelaClip App?\n"
            "Você assiste aos anúncios, nós recebemos dinheiro dos anunciantes e compartilhamos com você.\n\n"
            "3️⃣ Qual é a taxa de pagamento atual?\n"
            "A taxa de pagamento atual é de R$ 0,12 a R$ 0,28 por anúncio assistido.\n\n"
            "4️⃣ Quanto eu posso ganhar?\n"
            "Sua renda depende da quantidade de anúncios assistidos e de referências convidadas.\n\n"
            "5️⃣ Como funciona o programa de indicação?\n"
            "Ao convidar novos usuários para o EstrelaClip App através do seu link de indicação, você ganha R$ 1,00 por cada novo usuário e 5% de cada anúncio que eles assistirem.\n\n"
            "6️⃣ Como posso retirar meu dinheiro?\n"
            "Você pode retirar seu dinheiro seguindo as instruções na seção 'Saldo'. Valor mínimo para retirada: R$ 30,00\n\n"
            "7️⃣ Métodos de retirada de fundos?\n"
            "Pix, bancos brasileiros, Perfect Money, criptomoeda.\n\n"
            "8️⃣ O EstrelaClip App é seguro?\n"
            "Sim, o EstrelaClip App segue todas as diretrizes de segurança para proteger seus dados e suas transações.\n\n"
            "Se você tiver mais perguntas, entre em contato com nosso suporte ao cliente."
        )
        await query.edit_message_text(text=message_text)
    elif query.data == 'suporte':
        message_text = (
            "💬Para dúvidas relacionadas ao bot acesse https://t.me/AtendimentodepagamentoAdPlayApp - Seg a Sex das 9:00 as 17:00\n"
            "ou\n"
            "💬Para Atendimento relacionado ao Saque acesse https://t.me/lcs2683 - Ter a Sex das 9:00 as 17:00 💸"
        )
        await query.edit_message_text(text=message_text)
    elif query.data == 'painel_ad_pay_app':
        # Aqui chamamos o comando /menu
        await menu_customizado(query, context)
    elif query.data == 'retirada_fundos':
        user_id = query.from_user.id
        saldo = get_balance(user_id)
        
        if (saldo < 30):
            await query.edit_message_text("❌Valor mínimo de saque é de R$30,00❌")
            return
        
        message_text = "💰 Selecione o método de retirada:"
        keyboard_inline = [
            [InlineKeyboardButton("Pix", callback_data='retirada_pix')],
            [InlineKeyboardButton("Bancos Brasileiros", callback_data='retirada_bancos')],
            [InlineKeyboardButton("Perfect Money", callback_data='retirada_pm')],
            [InlineKeyboardButton("Criptomoeda", callback_data='retirada_crypto')]
        ]
        reply_markup_inline = InlineKeyboardMarkup(keyboard_inline)
        await query.edit_message_text(text=message_text, reply_markup=reply_markup_inline)
    elif query.data in ['retirada_pix', 'retirada_bancos', 'retirada_pm', 'retirada_crypto']:
        message_text = (
            "🤝Indique 10 amigos / Amigos indicados:0\n"
            "(Prazo de até 48 horas após a solicitação) - Válido somente ao primeiro saque.\n\n"
            "Ou\n\n"
            "💰Efetue o pagamento da taxa transferência rotacional no valor de R$ 5,00.\n"
            "(Prazo de até 12 horas após o pagamento)\n\n"
            "Saque mínimo: R$ 30,00\n"
            "Saque máximo: R$ 300,00 (Por saque)"
        )
        keyboard_inline = [
            [InlineKeyboardButton("🤝Saque por Indicação", callback_data='saque_indicacao')],
            [InlineKeyboardButton("💰Saque via pagamento", callback_data='saque_pagamento')]
        ]
        reply_markup_inline = InlineKeyboardMarkup(keyboard_inline)
        await query.edit_message_text(text=message_text, reply_markup=reply_markup_inline)
    elif query.data == 'saque_indicacao':
        message_text = "🤝Número de indicação insuficiente - Gere seu link no menu de indicação e indique 10 amigos para efetuar o saque."
        await query.edit_message_text(text=message_text)
    elif query.data == 'saque_pagamento':
        message_text = (
            "💰PIX CHAVE ALEATÓRIA👇\n\n"
            "b7facb16-1aa5-4da3-890e-53cca52a7dbd\n\n"
            "Dono do Bot: Pedro Henrique Costa Sousa\n\n"
            "Após efetuar o pagamento envie em https://t.me/AtendimentodepagamentoAdPlayApp o seguinte formulário:\n\n"
            "Comprovante de pagamento: (Print)\n"
            "Nome completo:\n"
            "Valor de saque:\n"
            "Forma de pagamento desejado:\n\n"
            "Após aguarde seu Ticket de Atendimento."
        )
        await query.edit_message_text(text=message_text)

# Função para listar usuários e mostrar saldo
async def listar_usuarios(update: Update, context: CallbackContext):
    if update.message.from_user.id != 1437993955:
        await update.message.reply_text("Você não tem permissão para usar este comando.")
        return

    conn = sqlite3.connect('saldos.db')
    c = conn.cursor()
    c.execute('SELECT id FROM users')
    users = c.fetchall()
    conn.close()

    if not users:
        await update.message.reply_text("Nenhum usuário encontrado.")
        return

    keyboard = [[InlineKeyboardButton(str(user[0]), callback_data=f'show_balance_{user[0]}')] for user in users]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Selecione um usuário para ver o saldo:", reply_markup=reply_markup)

async def show_balance(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_id = int(query.data.split('_')[2])
    balance = get_balance(user_id)
    await query.edit_message_text(f"O saldo do usuário {user_id} é: {format_currency(balance)}")

# Função para enviar bônus diário para todos os usuários
async def send_bonus_diario(update: Update, context: CallbackContext):
    if update.message.from_user.id != 1437993955:
        await update.message.reply_text("Você não tem permissão para usar este comando.")
        return

    conn = sqlite3.connect('saldos.db')
    c = conn.cursor()
    c.execute('SELECT id FROM users')
    users = c.fetchall()
    conn.close()

    if not users:
        await update.message.reply_text("Nenhum usuário encontrado.")
        return

    for user in users:
        user_id = user[0]
        message_text = "❤️ Aqui está seu bônus diário no valor de R$ 1,00"
        keyboard_inline = [
            [InlineKeyboardButton("❤️ Coletar", callback_data=f'coletar_bonus_{user_id}')]
        ]
        reply_markup_inline = InlineKeyboardMarkup(keyboard_inline)
        await context.bot.send_message(chat_id=user_id, text=message_text, reply_markup=reply_markup_inline)

async def coletar_bonus(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_id = int(query.data.split('_')[2])
    
    # Atualiza o saldo do usuário
    update_balance(user_id, 1.00)
    
    # Remove as mensagens anteriores
    await query.message.delete()
    
    # Envia mensagem de confirmação
    await context.bot.send_message(chat_id=user_id, text="❤️ Valor de R$ 1,00 adicionado com sucesso")

# Função para lidar com o menu customizado
async def handle_custom_menu(update: Update, context: CallbackContext):
    if update.message.text == '📋 Menu do Bot':
        await menu_bot(update, context)
    elif update.message.text == '▶️ Assistir anúncios':
        message_text = "📊 Taxa de pagamento atual: R$ 0,12 a R$ 0,28 por anúncio\n\nClique no botão abaixo para começar a assistir aos anúncios\n👇🏽"
        keyboard_inline = [
            [InlineKeyboardButton("Assistir Anúncios", web_app=WebAppInfo(url=f'https://6693139e7ba079b061336837--chimerical-melomakarona-c9aafc.netlify.app/?user_id={update.message.from_user.id}'))]
        ]
        reply_markup_inline = InlineKeyboardMarkup(keyboard_inline)
        await update.message.reply_text(text=message_text, reply_markup=reply_markup_inline)
    elif update.message.text == '🤝 Afiliados':
        message_text = "🤝Olá, esses aqui são os afiliados do bot, que nos ajudam a mantê-lo funcionando corretamente:\n\n" \
                       "Acesse [este link](https://1wfwna.life/?open=register&p=1zhf) para realizar um rápido cadastro.\n" \
                       "Adicione este codigo 6363834 ao entrar no site.\n" \
                       "Efetue um depósito no valor mínimo e faça qualquer aposta.\n" \
                       "Nós comprove no atendimeento FAQ, que adicionamos o dobro de saldo via Telegram.\n"

        image_url = 'https://static-pp.1win-cdn.com/promo-files-uploads/jjCDSvsC_2-mqwPC4YimbPjtB0-YxwVxDr6KX9OxdWOZNf76Da_vkTlVdoEua1l8lOFv4Yge6DFASGEm1N5hHQ0iImmRj-fuw8Vt.jpg'  # URL da imagem

        await update.message.reply_photo(photo=image_url, caption=message_text, parse_mode='Markdown')
    elif update.message.text == '👥 Indicação':
        referral_link = generate_referral_link(update.message.from_user.id)  # Gera um link de indicação exclusivo para o usuário
        referral_count = referral_counts.get(update.message.from_user.id, 0)  # Obtém o número de pessoas que usaram o link do usuário
        message_text = f"👥 Indicação\n\n" \
                       f"Convide seus amigos para usar o bot e ganhe R$ 1,00 por cada novo usuário que se cadastrar!\n\n" \
                       f"Seu link de indicação é: {referral_link}\n\n" \
                       f"Até agora, {referral_count} pessoas se cadastraram usando o seu link."
        
        await update.message.reply_text(text=message_text)
    elif update.message.text == '⚙️ Outros':
        ad_count = ad_counts.get(update.message.from_user.id, 0)
        message_text = f"⚙️ Outros\n\n" \
                       f"👥 Total de usuários: 92913\n" \
                       f"👀 Você assistiu a {ad_count} anúncios\n" \
                       f"💵 Total de fundos retirados: R$ 0"
        keyboard_inline = [
            [InlineKeyboardButton("💰 Histórico de Saques", callback_data='historico_saques')],
            [InlineKeyboardButton("📣 Notícias", callback_data='noticias')],
            [InlineKeyboardButton("📨 FAQ", callback_data='faq')],
            [InlineKeyboardButton("💬 Suporte", callback_data='suporte')]
        ]
        reply_markup_inline = InlineKeyboardMarkup(keyboard_inline)
        await update.message.reply_text(text=message_text, reply_markup=reply_markup_inline)
    elif update.message.text == '💰 Saldo':
        user_id = update.message.from_user.id
        saldo = get_balance(user_id)  # Obter saldo do banco de dados
        message_text = f"💰 Seu saldo atual é: {format_currency(saldo)}"
        keyboard_inline = [
            [InlineKeyboardButton("💰 Retirada dos fundos", callback_data='retirada_fundos')]
        ]
        reply_markup_inline = InlineKeyboardMarkup(keyboard_inline)
        await update.message.reply_text(text=message_text, reply_markup=reply_markup_inline)

# Função para gerar links de indicação únicos
def generate_referral_link(user_id):
    return f'https://t.me/AdPlayy_bot?start={user_id}'

# Função para lidar com novos usuários que entram pelo link de indicação
async def handle_new_user_via_referral(update: Update, context: CallbackContext):
    args = context.args
    if args:
        referrer_id = int(args[0])
        new_user_id = update.message.from_user.id

        if new_user_id == referrer_id:
            await update.message.reply_text("Você não pode usar seu próprio link de indicação.")
            return

        if new_user_id in used_referrals:
            await update.message.reply_text("Você já utilizou um link de indicação anteriormente.")
            return

        if new_user_id not in referrals:
            referrals[new_user_id] = referrer_id
            referral_counts[referrer_id] = referral_counts.get(referrer_id, 0) + 1

            update_balance(referrer_id, 1.00)  # Adiciona R$ 1,00 ao saldo do referenciador
            used_referrals[new_user_id] = True

            await update.message.reply_text('Obrigado por se cadastrar! Seu referenciador foi recompensado.')
            await context.bot.send_message(chat_id=referrer_id, text="Você Ganhou R$ 1,00 Por Indicar Uma Pessoa ❤️")
        else:
            await update.message.reply_text('Você já foi registrado anteriormente.')
    else:
        await update.message.reply_text('Bem-vindo!')

# Função para enviar a mensagem de recompensa antes do vídeo terminar
async def send_reward_message(user_id):
    reward_amount = random.choice([0.12, 0.15, 0.22, 0.25, 0.27])
    update_balance(user_id, reward_amount)
    message_text = f"Você ganhou {format_currency(reward_amount)} por assistir ao anúncio."

    # Incrementar contagem de anúncios assistidos
    if user_id in ad_counts:
        ad_counts[user_id] += 1
    else:
        ad_counts[user_id] = 1

    keyboard_inline = [
        [InlineKeyboardButton("Continuar assistindo aos anúncios", web_app=WebAppInfo(url=f'https://6693139e7ba079b061336837--chimerical-melomakarona-c9aafc.netlify.app/?user_id={user_id}'))]
    ]
    reply_markup_inline = InlineKeyboardMarkup(keyboard_inline)

    await application.bot.send_message(chat_id=user_id, text=message_text, reply_markup=reply_markup_inline)

# Função para o comando /start
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    # Verificar se há dados de referência
    if context.args:
        referrer_id = int(context.args[0])
        if referrer_id in referral_counts:
            referral_counts[referrer_id] += 1
        else:
            referral_counts[referrer_id] = 1

        referrals[user_id] = referrer_id  # Adicionar referência do usuário atual

    add_user(user_id)  # Adicionar usuário ao banco de dados

    # Exibir o menu_bot inicial
    await menu_bot(update, context)

# Iniciar o Flask em uma thread separada
def run_flask():
    @app.route('/reward', methods=['POST'])
    def reward_user():
        try:
            data = request.json
            user_id = data['user_id']
            logger.info(f'Recebido pedido de recompensa para user_id: {user_id}')

            # Cria uma nova thread para rodar o loop do asyncio
            def run_send_reward_message():
                asyncio.run(send_reward_message(user_id))

            threading.Thread(target=run_send_reward_message).start()
            return jsonify({'status': 'success'})
        except Exception as e:
            logger.error(f'Erro ao processar o pedido de recompensa: {e}')
            return jsonify({'status': 'error', 'message': str(e)})

    app.run(host='0.0.0.0', port=5000)

# Adicionar os handlers de comando e mensagem
application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('menu', menu_customizado))
application.add_handler(CommandHandler('add_saldo', add_saldo))  # Adicionar o comando /add_saldo
application.add_handler(CommandHandler('listar_usuarios', listar_usuarios))  # Comando para listar usuários
application.add_handler(CommandHandler('send_bonus_diario', send_bonus_diario))  # Comando para enviar bônus diário
application.add_handler(CallbackQueryHandler(button_click))
application.add_handler(CallbackQueryHandler(show_balance, pattern=r'^show_balance_'))
application.add_handler(CallbackQueryHandler(coletar_bonus, pattern=r'^coletar_bonus_'))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_menu))

# Configurar o banco de dados
setup_db()

# Iniciar o Flask em uma thread separada
threading.Thread(target=run_flask).start()

# Iniciar o bot
application.run_polling()
