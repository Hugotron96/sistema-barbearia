import streamlit as st
import sqlite3
from datetime import datetime

NOME_BANCO = "barbearia.db"

# Título Principal da Página
st.set_page_config(page_title="Barbearia do Chefe", layout="centered")
st.title("🪮 Barbearia do Chefe - Sistema de Agendamentos")

# Criação de abas na tela para separar o Cliente do Dono
aba_cliente, aba_dono = st.tabs(["🙋‍♂️ Área do Cliente", "💈 Painel do Barbeiro"])

# ----------------------------------------------------
# 1. TELA DO CLIENTE
# ----------------------------------------------------
with aba_cliente:
    st.header("Faça seu Agendamento")
    
    nome_cliente = st.text_input("Digite seu Nome:")
    data_escolhida = st.date_input("Escolha o Dia:", min_value=datetime.today())
    
    todos_horarios_expediente = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
    
    conexao = sqlite3.connect(NOME_BANCO)
    cursor = conexao.cursor()
    cursor.execute("SELECT dia_horario FROM agendamentos WHERE dia_horario LIKE ?", (f"{data_escolhida}%",))
    agendamentos_do_dia = cursor.fetchall()
    conexao.close()
    
    horas_ocupadas = []
    for registro in agendamentos_do_dia:
        hora_texto = registro[0].split(" ")[1]
        horas_ocupadas.append(hora_texto)
    
    horarios_filtrados = [hora for hora in todos_horarios_expediente if hora not in horas_ocupadas]
    
    if data_escolhida.weekday() == 6:
        st.error("Desculpe, a barbearia não abre aos domingos! Escolha outra data.")
    elif len(horarios_filtrados) == 0:
        st.warning("⚠️ Todos os horários deste dia já estão preenchidos! Tente outra data.")
    else:
        hora_escolhida = st.selectbox("Escolha o Horário Disponível:", horarios_filtrados)
        
        if st.button("Confirmar e Gerar PIX", type="primary"):
            if not nome_cliente:
                st.error("Por favor, digite seu nome antes de prosseguir.")
            else:
                data_hora_formatada = f"{data_escolhida} {hora_escolhida}"
                
                try:
                    conexao = sqlite3.connect(NOME_BANCO)
                    cursor = conexao.cursor()
                    cursor.execute("""
                        INSERT INTO agendamentos (cliente_name, dia_horario) 
                        VALUES (?, ?)
                    """, (nome_cliente, data_hora_formatada))
                    conexao.commit()
                    conexao.close()
                    
                    st.success(f"🎉 Horário pré-reservado com sucesso para {nome_cliente}!")
                    st.info("📌 **PAGAMENTO VIA PIX (Simulação):**")
                    st.code("00020101021126580014br.gov.bcb.pix0136barbeariachefe1234567890520400005303986540550.00", language="text")
                    
                    st.rerun()
                    
                except sqlite3.IntegrityError:
                    st.error("❌ Ops! Ocorreu um conflito. Escolha outra opção.")

# ----------------------------------------------------
# 2. TELA DO DONO DA BARBEARIA (COM OPÇÃO DE RECONHECER E REMOVER)
# ----------------------------------------------------
with aba_dono:
    st.header("Área Restrita")
    
    senha_digitada = st.text_input("Digite a senha do barbeiro:", type="password")
    SENHA_CORRETA = "admin123"
    
    if senha_digitada == SENHA_CORRETA:
        st.success("Acesso liberado, Chefe! 💈")
        
        conexao = sqlite3.connect(NOME_BANCO)
        conexao.row_factory = sqlite3.Row
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM agendamentos ORDER BY dia_horario ASC")
        agendamentos = [dict(linha) for linha in cursor.fetchall()]
        conexao.close()
        
        if not agendamentos:
            st.write("Nenhum agendamento marcado ainda.")
        else:
            for agen in agendamentos:
                with st.container(border=True):
                    # Dividimos o espaço em 4 colunas para incluir o botão de deletar
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.write(f"👤 **Cliente:** {agen['cliente_name']}")
                        st.write(f"📅 **Data/Hora:** {agen['dia_horario']}")
                    
                    with col2:
                        if agen['status_pagamento'] == 'Pago':
                            st.success("🟢 PAGO")
                        else:
                            st.error("🔴 PENDENTE")
                    
                    with col3:
                        if agen['status_pagamento'] == 'Pendente':
                            if st.button("Confirmar PIX", key=f"btn_pago_{agen['id']}", use_container_width=True):
                                conexao = sqlite3.connect(NOME_BANCO)
                                cursor = conexao.cursor()
                                cursor.execute("UPDATE agendamentos SET status_pagamento = 'Pago' WHERE id = ?", (agen['id'],))
                                conexao.commit()
                                conexao.close()
                                st.rerun()
                        else:
                            st.write("Concluído")
                    
                    with col4:
                        # Botão vermelho para excluir o agendamento
                        if st.button("🗑️ Remover", key=f"btn_del_{agen['id']}", type="secondary", use_container_width=True):
                            conexao = sqlite3.connect(NOME_BANCO)
                            cursor = conexao.cursor()
                            cursor.execute("DELETE FROM agendamentos WHERE id = ?", (agen['id'],))
                            conexao.commit()
                            conexao.close()
                            st.rerun() # Atualiza a tela imediatamente
                            
    elif senha_digitada != "":
        st.error("Senha incorreta! Tente novamente.")