import streamlit as st

st.set_page_config(page_title="Verificador NF x RMA", layout="centered")

# ======================
# 🎯 Interface inicial
# ======================
st.title("✅ Verificador de Nota Fiscal x RMA (Versão Teste)")

st.markdown("""
Este app permite comparar automaticamente uma **Nota Fiscal** com uma **RMA**, ambos em PDF.

> 🔐 Esta versão foi **otimizada para rodar no Streamlit Cloud** sem travamentos.  
> Envie os dois arquivos para iniciar.
""")

# ======================
# ⬆️ Upload de arquivos
# ======================
col1, col2 = st.columns(2)

with col1:
    nf_file = st.file_uploader("📄 Enviar Nota Fiscal (PDF)", type=["pdf"], key="nf")

with col2:
    rma_file = st.file_uploader("📄 Enviar RMA (PDF)", type=["pdf"], key="rma")

# ======================
# ⛔ Bloqueia até envio
# ======================
if not nf_file or not rma_file:
    st.warning("👆 Envie **ambos os arquivos PDF** para iniciar.")
    st.stop()

# ======================
# ✅ Upload realizado
# ======================
st.success("✅ Arquivos enviados com sucesso!")

# Exibe informações básicas dos arquivos
st.markdown("### ℹ️ Informações dos arquivos recebidos:")
st.write("**NF:**", nf_file.name, f"({round(nf_file.size / 1024, 2)} KB)")
st.write("**RMA:**", rma_file.name, f"({round(rma_file.size / 1024, 2)} KB)")

# (Opcional) Mostrar conteúdo binário por debug
# st.code(nf_file.read(), language="binary")
# st.code(rma_file.read(), language="binary")

# ✅ Placeholder para evoluir com lógica de extração e comparação
st.markdown("---")
st.info("🧠 Pronto! Agora você pode adicionar a lógica de extração e verificação com `fitz` e `pandas` aqui.")
