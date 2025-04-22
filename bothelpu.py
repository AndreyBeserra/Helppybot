from dotenv import load_dotenv
import os
import telebot
from telebot import types

# ===== CONFIGURAÇÃO =====
load_dotenv()
TOKEN = os.getenv('TOKEN_BOT')

if not TOKEN:
    raise ValueError("❌ Token não encontrado! Verifique o arquivo .env")

bot = telebot.TeleBot(TOKEN)

# ===== CONSTANTES =====
DESCRICAO_BOT = """
🤖 *Helppy - Seu Assistente Técnico Digital*

*O que eu faço?*
- Resolvo problemas comuns em celulares
- Explico soluções em linguagem simples
- Mostro tutoriais passo a passo com imagens
- Estou disponível 24 horas por dia
"""

EQUIPE = """
👨💻 *Equipe Help-U*

*Lucas* - Líder do Projeto
*Andrey* - Desenvolvedor
*Débora* - Designer
*Vinícius* - Marketing
*Gustavo* - Financeiro
"""

TUTORIAIS = {
    "internet": {
        "titulo": "📶 Problemas com Internet",
        "passos": """
1. Acesse *Configurações > Wi-Fi*
2. Ative o Wi-Fi
3. Selecione sua rede
4. Digite a senha correta
5. Tente acessar um site""",
        "pasta_imagens": "internet"
    },
    "bateria": {
        "titulo": "🔋 Bateria Acabando Rápido",
        "passos": """
1. Reduza o *brilho da tela*
2. Ative o *modo economia de energia*
3. Feche aplicativos não utilizados
4. Desative *GPS e Bluetooth*
5. Verifique aplicativos que consomem bateria""",
        "pasta_imagens": "bateria"
    },
    "armazenamento": {
        "titulo": "🗃️ Armazenamento Cheio",
        "passos": """
1. Vá em *Configurações > Armazenamento*
2. Toque em *Liberar espaço*
3. Exclua *arquivos temporários*
4. Desinstale aplicativos não usados
5. Limpe o *cache* dos aplicativos""",
        "pasta_imagens": "armazenamento"
    }
}


# ===== FUNÇÕES AUXILIARES =====
def enviar_imagens(chat_id, nome_pasta):
    """Envia todas as imagens de uma pasta específica"""
    try:
        caminho_base = os.path.join(os.getcwd(), ".assets", nome_pasta)
        caminho_base = os.path.normpath(caminho_base)

        print(f"\n🔍 Procurando imagens em: {caminho_base}")

        if not os.path.exists(caminho_base):
            print(f"❌ Pasta não encontrada: {caminho_base}")
            bot.send_message(chat_id, "📷 As imagens estarão disponíveis em breve!")
            return

        for nome_arquivo in sorted(os.listdir(caminho_base)):
            if nome_arquivo.lower().endswith(('.png', '.jpg', '.jpeg')):
                caminho_completo = os.path.join(caminho_base, nome_arquivo)
                try:
                    print(f"🔄 Processando: {nome_arquivo}")
                    with open(caminho_completo, 'rb') as img:
                        bot.send_photo(chat_id, img)
                    print(f"✅ {nome_arquivo} enviado com sucesso!")
                except Exception as e:
                    print(f"⚠️ Falha ao enviar {nome_arquivo}: {str(e)}")
                    bot.send_message(chat_id, f"⚠️ Não foi possível carregar {os.path.splitext(nome_arquivo)[0]}")

    except Exception as e:
        print(f"⛔ ERRO: {str(e)}")
        bot.send_message(chat_id, "😕 Ocorreu um erro inesperado. Por favor, tente novamente mais tarde!")


def criar_teclado(opcoes, botoes_por_linha=2):
    """Cria teclado inline de forma dinâmica"""
    markup = types.InlineKeyboardMarkup(row_width=botoes_por_linha)
    botoes = [types.InlineKeyboardButton(text, callback_data=key)
              for key, text in opcoes.items()]
    markup.add(*botoes)
    return markup


# ===== HANDLERS PRINCIPAIS =====
@bot.message_handler(commands=['start', 'help'])
def comando_start(message):
    """Handler para comandos iniciais"""
    markup = criar_teclado({"menu_principal": "👉 Começar"})
    bot.send_message(
        message.chat.id,
        "🖐️ Olá! Eu sou o *Helppy*, seu assistente técnico pessoal.\n\n"
        "Estou aqui para te ajudar com problemas no seu celular!",
        reply_markup=markup,
        parse_mode='Markdown'
    )


@bot.callback_query_handler(func=lambda call: call.data == "menu_principal")
def menu_principal(call):
    """Menu principal interativo"""
    opcoes = {
        "assistencia": "🔧 Assistência Técnica",
        "sobre_bot": "🤖 Sobre o Bot",
        "equipe": "👥 Conheça a Equipe"
    }
    bot.edit_message_text(
        "🎛️ *Menu Principal*: Escolha uma opção abaixo",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=criar_teclado(opcoes),
        parse_mode='Markdown'
    )


@bot.callback_query_handler(func=lambda call: call.data == "assistencia")
def menu_assistencia(call):
    """Menu de problemas técnicos"""
    opcoes = {key: val["titulo"] for key, val in TUTORIAIS.items()}
    opcoes["menu_principal"] = "🔙 Voltar"

    bot.edit_message_text(
        "🔧 *Assistência Técnica*: Selecione o problema",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=criar_teclado(opcoes),
        parse_mode='Markdown'
    )


@bot.callback_query_handler(func=lambda call: call.data in TUTORIAIS.keys())
def mostrar_tutorial(call):
    """Exibe tutorial completo com imagens"""
    tutorial = TUTORIAIS[call.data]

    bot.edit_message_text(
        f"*{tutorial['titulo']}*\n\n{tutorial['passos']}",
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown'
    )

    enviar_imagens(call.message.chat.id, tutorial["pasta_imagens"])

    bot.send_message(
        call.message.chat.id,
        "Precisa de mais ajuda?",
        reply_markup=criar_teclado({"assistencia": "🔙 Voltar para Assistência"})
    )


@bot.callback_query_handler(func=lambda call: call.data == "sobre_bot")
def sobre_bot(call):
    """Informações detalhadas sobre o bot"""
    bot.edit_message_text(
        DESCRICAO_BOT,
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown'
    )

    markup = criar_teclado({
        "equipe": "👥 Ver Equipe",
        "menu_principal": "🔙 Menu Principal"
    })
    bot.send_message(call.message.chat.id, "Saiba mais:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "equipe")
def mostrar_equipe(call):
    """Exibe informações da equipe com fotos e descrições individuais"""
    try:
        bot.edit_message_text(
            EQUIPE,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )

        # Dados dos membros com caracteres escapados
        membros = [
            {
                "foto": "lucas.png",
                "descricao": "Lucas Ryan Albuquerque: Ele é o PO da Help-U, uma pessoa muito dedicada e envolvida em todos os projetos da startup, sendo sua visão crucial para o desenvolvimento do bot! 🧐"
            },
            {
                "foto": "andrey.png",
                "descricao": "Andrey Beserra: Nosso CTO e desenvolvedor Backend, a mente por trás da criação do bot, programando novas funcionalidades. Sua criatividade gera novas ideias! 😎"
            },
            {
                "foto": "debora.png",
                "descricao": "Débora Rodrigues: Designer e Social Media da startup, parte de uma dupla incrível ✨ que trabalha na criação de textos, slides e gerencia nosso Instagram helpu\\_assist. 🙆‍♀"
            },
            {
                "foto": "vinicius.png",
                "descricao": "Vinícius de Azevedo: Designer e Social Media da startup, parte de uma dupla incrível ✨ que trabalha na criação de textos, slides e gerencia nosso Instagram helpu\\_assist. 🙆‍♂"
            },
            {
                "foto": "gustavo.png",
                "descricao": "Gustavo de Lima: Nosso gerente financeiro 💰, responsável pelas planilhas, controle de custos e por discutir com a equipe as melhores opções para aplicar nosso orçamento! 😎💵✨"
            }
        ]

        caminho_base = os.path.join(os.getcwd(), ".assets", "equipe")
        caminho_base = os.path.normpath(caminho_base)

        if not os.path.exists(caminho_base):
            bot.send_message(call.message.chat.id, "⚠️ Pasta da equipe não encontrada!")
            return

        for membro in membros:
            caminho_foto = os.path.join(caminho_base, membro["foto"])

            if os.path.exists(caminho_foto):
                try:
                    with open(caminho_foto, 'rb') as img:
                        # Envia sem parse_mode para evitar erros de formatação
                        bot.send_photo(
                            call.message.chat.id,
                            img,
                            caption=membro["descricao"]
                        )
                except Exception as e:
                    print(f"⚠️ Erro ao enviar {membro['foto']}: {str(e)}")
                    # Envia só o texto se houver erro com a foto
                    bot.send_message(
                        call.message.chat.id,
                        membro["descricao"]
                    )
            else:
                bot.send_message(
                    call.message.chat.id,
                    membro["descricao"] + "\n\n⚠️ Foto temporariamente indisponível"
                )

        markup = criar_teclado({
            "sobre_bot": "🤖 Sobre o Bot",
            "menu_principal": "🔙 Menu Principal"
        })
        bot.send_message(
            call.message.chat.id,
            "O que gostaria de fazer agora?",
            reply_markup=markup
        )

    except Exception as e:
        print(f"⛔ ERRO: {str(e)}")
        bot.send_message(
            call.message.chat.id,
            "😕 Estamos com dificuldades técnicas. Por favor, tente novamente mais tarde."
        )

# ===== INICIALIZAÇÃO =====
if __name__ == "__main__":
    print("""
    ========================
       HELPPY BOT INICIANDO
    ========================
    Verificando recursos...
    """)

    # Verificação de pastas
    pastas_necessarias = ["equipe", "internet", "bateria", "armazenamento"]
    for pasta in pastas_necessarias:
        caminho = os.path.normpath(os.path.join(os.getcwd(), ".assets", pasta))
        if os.path.exists(caminho):
            num_arquivos = len([f for f in os.listdir(caminho) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
            print(f"✅ {pasta.upper()}: {num_arquivos} imagens")
        else:
            print(f"⚠️ ATENÇÃO: Pasta '{pasta}' não encontrada!")

    print("\n⚡ Bot pronto para receber comandos...")
    bot.polling(none_stop=True)