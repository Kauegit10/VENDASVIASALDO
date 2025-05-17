import telebot
import threading
import time
from config import BOT_TOKEN, ADMIN_USERNAME
from database import *

bot = telebot.TeleBot(BOT_TOKEN)
init_db()

# Mensagem inicial
def menu_inicial():
    return (
        "🔥 Bem-vindo ao *BOT DE VENDAS DE CONTAS*! 🔥\n"
        "Aqui você pode comprar contas de vários jogos e redes sociais usando seu saldo!\n\n"
        "🧾 *Comandos disponíveis:*\n"
        "📲 /start - Criar seu perfil\n"
        "💰 /saldo - Ver seu saldo atual\n"
        "🛒 /loja - Comprar contas com seu saldo\n"
        "👤 /minhaconta - Ver suas informações\n"
        "🆘 /help - Ver instruções de uso\n"
    )

@bot.message_handler(commands=['start'])
def start(message):
    criar_usuario(message.from_user.id, message.from_user.username)
    bot.reply_to(message, f"{menu_inicial()}")

@bot.message_handler(commands=['saldo'])
def saldo(message):
    saldo = get_saldo(message.from_user.username)
    bot.reply_to(message, f"💵 Seu saldo é: R${saldo:.2f}")

@bot.message_handler(commands=['minhaconta'])
def minha_conta(message):
    user = get_usuario(message.from_user.username)
    if user:
        bot.reply_to(message, f"👤 Usuário: @{user[1]}\n💰 Saldo: R${user[2]:.2f}\n🛍️ Compras: {user[3]}")
    else:
        bot.reply_to(message, "Você ainda não tem perfil. Use /start.")

@bot.message_handler(commands=['help'])
def ajuda(message):
    bot.reply_to(message, menu_inicial() + "\n"
                   "❓ *Como adicionar saldo:*\n"
                   "Fale com o admin (@" + ADMIN_USERNAME + ") e envie o comprovante de pagamento.\n\n"
                   "❓ *Como comprar uma conta:*\n"
                   "Use o comando /loja e siga as instruções para escolher e comprar sua conta.")

@bot.message_handler(commands=['loja'])
def loja(message):
    categorias = listar_categorias()
    if not categorias:
        bot.reply_to(message, "❌ Nenhuma conta disponível no momento.")
        return
    texto = "🛒 *Categorias disponíveis:*\n"
    for i, cat in enumerate(categorias, 1):
        texto += f"{i}. {cat}\n"
    texto += "\nDigite o número da categoria que deseja acessar."
    bot.send_message(message.chat.id, texto)
    bot.register_next_step_handler(message, escolher_categoria, categorias)

def escolher_categoria(message, categorias):
    try:
        escolha = int(message.text) - 1
        categoria = categorias[escolha]
        contas = listar_contas_por_categoria(categoria)
        if not contas:
            bot.reply_to(message, "❌ Nenhuma conta nesta categoria.")
            return
        texto = f"📂 Contas em *{categoria}*:\n"
        for conta in contas:
            texto += f"ID {conta[0]} - {conta[1]} - R${conta[2]:.2f}\n"
        texto += "\nDigite o *ID* da conta que deseja comprar."
        bot.send_message(message.chat.id, texto)
        bot.register_next_step_handler(message, processar_compra)
    except (IndexError, ValueError):
        bot.reply_to(message, "❌ Opção inválida.")

def processar_compra(message):
    try:
        conta_id = int(message.text)
        status, dados = comprar_conta(message.from_user.username, conta_id)
        if dados:
            bot.reply_to(message, f"✅ {status}\n\n🔑 Dados da conta:\n{dados}")
        else:
            bot.reply_to(message, f"❌ {status}")
    except ValueError:
        bot.reply_to(message, "❌ ID inválido.")

# MENU ADMIN
def admin_menu():
    while True:
        print("\n--- PAINEL ADMIN ---")
        print("1. Adicionar saldo")
        print("2. Remover saldo")
        print("3. Ver saldo de usuário")
        print("4. Adicionar conta para venda")
        print("5. Sair")
        escolha = input("Escolha uma opção: ")

        if escolha == "1":
            user = input("Digite o @username (sem @): ")
            valor = float(input("Valor a adicionar: "))
            atualizar_saldo(user, valor)
            print(f"R${valor:.2f} adicionado ao saldo de @{user}")
        elif escolha == "2":
            user = input("Digite o @username (sem @): ")
            valor = float(input("Valor a remover: "))
            atualizar_saldo(user, -valor)
            print(f"R${valor:.2f} removido do saldo de @{user}")
        elif escolha == "3":
            user = input("Digite o @username (sem @): ")
            saldo = get_saldo(user)
            if saldo is not None:
                print(f"Saldo de @{user}: R${saldo:.2f}")
            else:
                print("Usuário não encontrado.")
        elif escolha == "4":
            cat = input("Categoria (ex: Free Fire, Instagram...): ")
            usr = input("Usuário da conta: ")
            senha = input("Senha da conta: ")
            preco = float(input("Preço: "))
            adicionar_conta(cat, usr, senha, preco)
            print("Conta adicionada com sucesso!")
        elif escolha == "5":
            print("Saindo do painel.")
            break
        else:
            print("Opção inválida.")

menu_thread = threading.Thread(target=admin_menu)
menu_thread.daemon = True
menu_thread.start()

print("Bot está rodando...")
bot.infinity_polling()
