import streamlit as st

# ----------------- CSS (Firulas) ------------------
st.markdown("""
<style>
.main {
    background-color: #FAFAFA;
}
.big-title {
    font-size: 2.0em;
    color: #D35400;
    margin-bottom: 0.5em;
    font-weight: bold;
    text-align: center;
}
.highlight-box {
    background: #FFF7E6;
    border-left: 5px solid #FFA500;
    padding: 15px;
    border-radius: 5px;
    margin: 1em 0;
    font-size:1.05em;
}
.my-subtitle {
    font-size:1.15em;
    font-weight: bold;
    margin-top: 1em;
    color: #2C3E50;
}
</style>
""", unsafe_allow_html=True)

# ----------------- Título e introdução ------------------
st.markdown("<div class='big-title'>Guia Completo de Devolução e Procedimentos</div>", unsafe_allow_html=True)
st.markdown("""
<div class='highlight-box'>
Bem-vindo(a)! Aqui você encontra as principais regras, procedimentos e instruções 
relacionadas às devoluções, cancelamentos, coletas, faturamento, operações e mais.
</div>
""", unsafe_allow_html=True)

# ===================== CARREGAMENTO DOS DADOS =====================
from guia_dados_completo import conteudo, transportadoras, operacoes

# ===================== LÓGICA DE SELEÇÃO =====================
topicos_principais = list(conteudo.keys()) + ["9. Transportadoras", "10. Operações (115-8, 067-3, 163-1)"]
escolha_topico = st.selectbox("📌 Selecione o tópico principal:", ["" ] + topicos_principais)

if escolha_topico:

    if escolha_topico in conteudo:
        subitens = list(conteudo[escolha_topico].keys())
        escolha_sub = st.selectbox("\U0001F4DD Selecione a seção específica:", ["" ] + subitens)

        if escolha_sub:
            texto = conteudo[escolha_topico].get(escolha_sub)
            if texto:
                st.markdown(f"<div class='my-subtitle'>{escolha_sub}</div>", unsafe_allow_html=True)
                st.markdown(texto, unsafe_allow_html=True)
            else:
                st.warning("Este subitem não possui texto definido.")

    elif escolha_topico == "9. Transportadoras":
        nomes = list(transportadoras.keys())
        escolha_transp = st.selectbox("🚚 Selecione a Transportadora:", ["" ] + nomes)

        if escolha_transp:
            st.markdown(f"<div class='my-subtitle'>{escolha_transp}</div>", unsafe_allow_html=True)
            st.markdown(transportadoras[escolha_transp], unsafe_allow_html=True)

    elif escolha_topico == "10. Operações (115-8, 067-3, 163-1)":
        nomes_ops = list(operacoes.keys())
        escolha_op = st.selectbox("⚙️ Selecione a Operação:", ["" ] + nomes_ops)

        if escolha_op:
            st.markdown(f"<div class='my-subtitle'>{escolha_op}</div>", unsafe_allow_html=True)
            st.markdown(operacoes[escolha_op], unsafe_allow_html=True)

# ------------- RODAPÉ -------------
st.write("---")
st.info("Dúvidas adicionais? Contate o setor responsável ou consulte a documentação interna.")
