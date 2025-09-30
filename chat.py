import streamlit as st
import psycopg2
import datetime
import re
import time

# --- Configuração do Banco de Dados ---
DB_CONFIG = {
    "dbname": "satisfacao",
    "user": "postgres",
    "password": "123456",
    "host": "localhost",
    "port": "5432"
}

# --- Funções Auxiliares ---
def conectar_db():
    """Tenta conectar ao banco de dados e retorna a conexão."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

def salvar_feedback(nome, email, nota, comentario):
    """Salva o feedback no banco de dados."""
    conn = conectar_db()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO feedbacks (nome, email, nota, comentario, data_resposta)
                    VALUES (%s, %s, %s, %s, %s)
                """, (nome, email, nota, comentario, datetime.datetime.now()))
                conn.commit()
            st.success("✅ Resposta registrada com sucesso! Obrigado pelo seu tempo.")
            return True
        except Exception as e:
            st.error(f"Erro ao salvar no banco: {e}")
            return False
        finally:
            conn.close()
    return False

def is_valid_email(email):
    """Verifica se o e-mail tem um formato válido."""
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email)

# --- Configuração da Página ---
st.set_page_config(page_title="Pesquisa de Satisfação", page_icon="📝")
st.image("logo-sm.jpg", width=150) 
st.title("Pesquisa de Satisfação")

# --- Inicialização do Chat ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Olá! A sua opinião é muito importante para nós. Gostaríamos de convidá-lo(a) a responder à nossa pesquisa de satisfação. Levará apenas alguns minutos do seu tempo e nos ajudará a aprimorar nossos serviços e produtos para oferecer uma experiência ainda melhor. Sua participação é fundamental para que possamos entender suas necessidades e expectativas. Contamos com você!"}]
    
    st.session_state.stage = "inicio"
    st.session_state.feedback_data = {}

# --- Exibir histórico do chat ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Lógica do Chat ---
if prompt := st.chat_input("Sua resposta"):
    # Adicionar mensagem do usuário ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Lógica de resposta do assistente baseada no estágio da conversa
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        resposta_assistente = ""  # <- variável para armazenar a resposta do bot

        # Estágio 0: Início
        if st.session_state.stage == "inicio":
            resposta_assistente = "Ótimo! Para começar, qual é o seu nome?"
            st.session_state.stage = "get_name"

        # Estágio 1: Obter Nome
        elif st.session_state.stage == "get_name":
            st.session_state.feedback_data['nome'] = prompt
            resposta_assistente = f"Prazer, {prompt}! 😊 Agora, por favor, me informe o seu melhor e-mail."
            st.session_state.stage = "get_email"

        # Estágio 2: Obter Email
        elif st.session_state.stage == "get_email":
            if is_valid_email(prompt):
                st.session_state.feedback_data['email'] = prompt
                resposta_assistente = "Obrigado! Em uma escala de 0 (péssima) a 10 (excelente), qual a sua satisfação geral com nossos serviços?"
                st.session_state.stage = "get_nota"
            else:
                resposta_assistente = "❌ Parece que este e-mail não é válido. Poderia tentar novamente, por favor?"

        # Estágio 3: Obter Nota
        elif st.session_state.stage == "get_nota":
            try:
                nota = int(prompt)
                if 0 <= nota <= 10:
                    st.session_state.feedback_data['nota'] = nota
                    resposta_assistente = "Entendido. Você gostaria de deixar algum comentário ou sugestão adicional? (Se não, pode apenas dizer 'não')"
                    st.session_state.stage = "get_comentario"
                else:
                    resposta_assistente = "Por favor, insira um número inteiro entre 0 e 10."
            except ValueError:
                resposta_assistente = "❌ Ops, isso não parece ser um número. Por favor, digite um valor de 0 a 10."

        # Estágio 4: Obter Comentário
        elif st.session_state.stage == "get_comentario":
            comentario = prompt.strip()
            if comentario.lower() in ['nao', 'não', 'n', 'no']:
                st.session_state.feedback_data['comentario'] = ""
                comentario_text = "Nenhum comentário."
            else:
                st.session_state.feedback_data['comentario'] = comentario
                comentario_text = st.session_state.feedback_data['comentario']

            resposta_assistente = f"""
            Certo, vamos confirmar suas respostas:
            - **Nome:** {st.session_state.feedback_data['nome']}
            - **Email:** {st.session_state.feedback_data['email']}
            - **Nota:** {st.session_state.feedback_data['nota']}
            - **Comentário:** {comentario_text}

            Posso registrar essas informações? (Sim/Não)
            """
            st.session_state.stage = "confirmacao"

        # Estágio 5: Confirmação
        elif st.session_state.stage == "confirmacao":
            if prompt.lower() in ['sim', 's', 'yes', 'y']:
                resposta_assistente = "Registrando suas respostas..."
                if salvar_feedback(**st.session_state.feedback_data):
                    resposta_assistente = "Pronto! Suas respostas foram salvas com sucesso. Agradecemos muito sua colaboração! ✨"
                else:
                    resposta_assistente = "Houve um problema ao salvar suas respostas. Por favor, tente novamente mais tarde."
                st.session_state.stage = "fim"
            else:
                resposta_assistente = "Tudo bem. Se quiser, podemos recomeçar. Basta me dizer 'olá' ou recarregar a página."
                st.session_state.stage = "inicio"
                st.session_state.feedback_data = {}
        
        # Estágio Final
        elif st.session_state.stage == "fim":
            resposta_assistente = "A pesquisa foi finalizada. Se precisar de algo mais, estou à disposição!"

        # Mostrar resposta do assistente
        message_placeholder.markdown(resposta_assistente)

    # Adicionar resposta do assistente ao histórico e recarregar
    st.session_state.messages.append({"role": "assistant", "content": resposta_assistente})
    st.rerun()
