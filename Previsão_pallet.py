import streamlit as st

# ---------- CSS (Firulas) ----------
st.markdown("""
<style>
.main {
    background-color: #FAFAFA;
}

/* Título grande */
.big-title {
    font-size: 2.0em;
    color: #D35400; /* Laranja escuro */
    margin-bottom: 0.5em;
    font-weight: bold;
    text-align: center;
}

/* Caixa de destaque */
.highlight-box {
    background: #FFF7E6;
    border-left: 5px solid #FFA500;
    padding: 15px;
    border-radius: 5px;
    margin: 1em 0;
    font-size:1.05em;
}

/* Expander style */
.streamlit-expanderHeader {
    font-weight: bold;
    color: #2C3E50;
    font-size:1.1em;
}
</style>
""", unsafe_allow_html=True)

# ---------- Título e introdução ----------
st.markdown("<div class='big-title'>Guia Completo de Devolução e Procedimentos</div>", unsafe_allow_html=True)
st.markdown("""
<div class='highlight-box'>
Bem-vindo(a)! Aqui você encontra as principais regras, procedimentos e instruções 
relacionadas às devoluções, cancelamentos, coletas, faturamento, operações e mais.
</div>
""", unsafe_allow_html=True)

# ---------- Lista de Tópicos (via RADIO) ----------
topicos = [
    "1. Cancelamento / Recusa de Pedidos",
    "2. Emissão de NF e Coleta (Não Contribuinte)",
    "3. Solicitação de Coleta (Contribuinte)",
    "4. Emissão de NF e Coleta LNE",
    "5. Devolução c/ Frete por Conta do Cliente",
    "6. Faturamento Vendas Fora do LNE",
    "7. Troca de NF (CNPJ/Desconto)",
    "8. Transportadoras",
    "9. Operações (115-8, 067-3, 163-1)"
]

escolha = st.radio("Selecione o tópico:", topicos)

# ---------- CONTEÚDO DE CADA TÓPICO ----------
if escolha == "1. Cancelamento / Recusa de Pedidos":
    st.subheader("1. CANCELAMENTO | RECUSA DE PEDIDOS")

    with st.expander("Quando usar?"):
        st.write("""\
- **Cancelamento** se o pedido e NF puderem ser cancelados no sistema (até 7 dias). 
  O setor de Gestão de Pedidos confirma se não foi expedido.
- **Recusa/Desistência** se o cliente rejeitou o material no ato da entrega ou desistiu após expedição. 
  Acionar Transporte para retorno.
""")

    with st.expander("Procedimentos"):
        st.write("""\
1. **Emitir RMA** (se aplicável), sem transportadora e "FOB: Sem frete". Observações: "Pedido cancelado" ou "Pedido recusado".
2. **Abrir SAC** (Tipo: Solicitação; Assunto: "Cancelamento pedido X" ou "Pedido X recusado"). 
   Preencher Filial, RMA, NF, etc.
3. **Se LNE ou Remessa Antecipada**: Não emite RMA; siga o mesmo fluxo no SAC, marcando "Loja na Escola / Remessa antecipada" e NF da remessa LNE.
4. **Logística Devolução** emite NF de devolução, notifica via CRM e aplica crédito se for RMA.
""")

    with st.expander("Pontos Importantes"):
        st.write("""\
- Se exceder 7 dias ou já expedido, trata-se de devolução simbólica (não cancelamento).
- Em recusa no ato da entrega, o setor de Transportes deve acionar retorno da mercadoria.
- O financeiro usa o crédito p/ abater NF cancelada/recusada.
""")

elif escolha == "2. Emissão de NF e Coleta (Não Contribuinte)":
    st.subheader("2. EMISSÃO DE NF E COLETA (CLIENTE NÃO CONTRIBUINTE)")

    with st.expander("Quando usar?"):
        st.write("""\
- Cliente sem IE, impossibilitado de emitir NF de devolução.
- A empresa vendedora (PSD) emite nota de entrada para retorno ao estoque.
""")

    with st.expander("Procedimentos"):
        st.write("""\
1. **Verificar** se a devolução está dentro de regras (prazos, etc.).
2. **Emitir RMA** no ORACLE (ver "Devoluções Oracle - Como criar RMA").
3. **Abrir SAC** (Assunto: "Solicitação NF e coleta (não contribuinte)"), preenchendo Filial, RMA, NF, transportadora.
4. **Logística Devolução** emite NF, gera crédito, avisa CRM e Transportes para coleta (TMS).
""")

    with st.expander("Pontos Importantes"):
        st.write("""\
- Encaminhar NF ao cliente; o transportador pode exigir.
- A quantidade de caixas deve bater com a NF, lacradas e identificadas.
- Se houver 2 tentativas de coleta sem sucesso, cancela-se o agendamento.
""")

elif escolha == "3. Solicitação de Coleta (Contribuinte)":
    st.subheader("3. SOLICITAÇÃO DE COLETA (CLIENTE CONTRIBUINTE)")

    with st.expander("Quando usar?"):
        st.write("""\
- Cliente com IE: ele emite a NF de devolução. 
- Frete normalmente FOB (destinatário). 
- Se o cliente pagar frete, veja "Devolução com Frete por Conta do Cliente".
""")

    with st.expander("Procedimentos"):
        st.write("""\
1. **Emitir RMA** no ORACLE (gera "Autorização de Devolução de Produto").
2. **Cliente** emite a NF de devolução, corrigindo se houver divergências.
3. **Abrir SAC** ("Solicitação NF e coleta contribuinte"), anexar PDF da NF se exigido.
4. **Logística Devolução** confere a NF; se correto, manda ao Transportes (TMS).
""")

    with st.expander("Pontos Importantes"):
        st.write("""\
- Notas acima de 15 dias podem ser recusadas.
- Caixas lacradas e identificadas (quantidade deve bater com a NF).
- Manter dados de contato atualizados p/ evitar falhas na coleta.
""")

elif escolha == "4. Emissão de NF e Coleta LNE":
    st.subheader("4. EMISSÃO DE NF E COLETA LNE")

    with st.expander("Quando usar?"):
        st.write("""\
- Remessa antecipada / Loja na Escola (materiais em poder de terceiros).
- Sobras não vendidas precisam ser baixadas e recolhidas.
- Fluxo distinto, sem RMA (em geral).
""")

    with st.expander("Procedimentos"):
        st.write("""\
1. Confronte itens com relatórios SGE/Oracle.
2. Preencha formulário "LNE" com dados para emissão NF e coleta.
3. **Abra SAC** ("Emissão de NF e coleta LNE"), anexe formulário + NF Remessa LNE.
4. **Logística** emite NF, baixa estoque de terceiros, notifica CRM. 
   Transportes agenda coleta no TMS.
""")

    with st.expander("Pontos Importantes"):
        st.write("""\
- Encaminhar NF ao cliente p/ evitar problemas na coleta.
- Mesmo nº de caixas da NF, tudo lacrado e acessível.
- 2 tentativas sem sucesso cancelam a coleta.
""")

elif escolha == "5. Devolução c/ Frete por Conta do Cliente":
    st.subheader("5. DEVOLUÇÃO COM FRETE POR CONTA DO CLIENTE")

    with st.expander("Quando usar?"):
        st.write("""\
- O cliente arca com frete (por contrato ou acordo). 
- Pode usar transportadora da base ou contratar própria.
""")

    with st.expander("Procedimentos"):
        st.write("""\
**Situação A: Cliente paga frete mas usa nossa transportadora**
1. Emita RMA (não contribuinte = FOB, contribuinte = CIF).
2. Abra SAC "Devolução com frete por conta do cliente," preencha Filial, RMA, NF. "Cliente irá contratar frete? Não."

**Situação B: Cliente contrata transportadora externa**
1. Se não contribuinte, ver se a transportadora está na base; se não, informe dados manualmente. Se contribuinte, ele define na NF.
2. Abra SAC igual acima, mas "Cliente irá contratar frete? Sim."
""")

    with st.expander("Pontos Importantes"):
        st.write("""\
- Se não contribuinte, Logística emite NF; se contribuinte, o cliente emite NF.
- Se usar nossa base, nós agendamos coleta. Se for outra, o cliente acompanha a mercadoria.
- Sempre encaminhar NF ao cliente; o transportador pode exigir.
""")

elif escolha == "6. Faturamento Vendas Fora do LNE":
    st.subheader("6. FATURAMENTO VENDAS FORA DO LNE")

    with st.expander("Quando usar?"):
        st.write("""\
- Houve vendas por fora na escola (fora da plataforma).
- Precisamos ajustar estoque e faturar contra a escola.
""")

    with st.expander("Procedimentos"):
        st.write("""\
1. **Devolução simbólica** dos itens "fora" para corrigir estoque.
2. Emitir **pedido no SGE** (operação 067-3) sem movimentar estoque físico.
3. **Abrir SAC** p/ Logística Devolução, informar nº pedido SGE, NF Remessa LNE.
4. Logística emite nota de devolução simbólica, baixa saldo e fatura manualmente o pedido.
""")

    with st.expander("Pontos Importantes"):
        st.write("""\
- O solicitante é notificado via CRM quando concluído.
- Verifique sempre se há sobras ou divergências no SGE para não gerar mais devoluções.
""")

elif escolha == "7. Troca de NF (CNPJ/Desconto)":
    st.subheader("7. TROCA DE NF PARA CORREÇÃO DE CNPJ / DESCONTO")

    with st.expander("Quando usar?"):
        st.write("""\
- Devolução simbólica/virtual, sem retorno físico. 
- Corrigir valores, desconto, CNPJ ou migrar tipo de venda (ex.: LNE → Direta).
""")

    with st.expander("Procedimentos"):
        st.write("""\
1. Emita RMA sem transportadora (FOB "Sem frete").
2. Observações: "Devolução simbólica."
3. Abra SAC ("Troca de NF p/ correção de desconto/CNPJ"), informe nº pedido SGE, NF p/ crédito.
4. Logística gera crédito para abater faturamento incorreto e cria novo faturamento.
""")

    with st.expander("Pontos Importantes"):
        st.write("""\
- Se for operação antecipada + remessa futura, podem ser 2 RMAs com mesmos itens.
- RMA e faturamento entram na mesma solicitação (tratativa sistêmica). 
- Verificar prazos; se muito tarde, pode ser recusado.
""")

elif escolha == "8. Transportadoras":
    st.subheader("8. TRANSPORTADORAS (ENDEREÇOS)")

    with st.expander("Braspress"):
        st.write("""**CNPJ**: 48.740.351/0003-27  
Endereço: RUA JOAO BETTEGA, 3802 – CIDADE INDUSTRIAL, CURITIBA/PR
""")

    with st.expander("Cruzeiro do Sul"):
        st.write("""**CNPJ**: 03.232.675/0061-95  
No Oracle: "03232675006195-PR-PARCEL-Padrao"  
Endereço: AV. DEZ DE DEZEMBRO, 5680 – JARDIM PIZA, LONDRINA/PR
""")

    with st.expander("FL BRASIL (SOLISTICA)"):
        st.write("""**CNPJ**: 18.233.211/0028-50  
IE: 9076066008  
Endereço: RODOVIA BR 116, 22301 – TATUQUARA, CURITIBA/PR
""")

    with st.expander("Local Express"):
        st.write("""**CNPJ**: 06.199.523/0001-95  
IE: 9030307558  
Endereço: R FORMOSA, 131 – PLANTA PORTAL DA SERRA, PINHAIS/PR
""")

    with st.expander("Rodonaves"):
        st.write("""**CNPJ**: 44.914.992/0017-03  
IE: 6013031914  
Endereço: RUA RIO GRANDE DO NORTE, 1200, CENTRO, LONDRINA/PR
""")

elif escolha == "9. Operações (115-8, 067-3, 163-1)":
    st.subheader("9. OPERAÇÕES (115-8, 067-3, 163-1)")

    with st.expander("Operação 163-1"):
        st.write("""Exclusiva para correções sistêmicas, como ajustes de CNPJ, descontos incorretos e erros de operação no SGE.""")

    with st.expander("Operação 067-3"):
        st.write("""Agora destinada apenas à correção de vendas realizadas fora da plataforma Loja na Escola.""")

    with st.expander("Operação 115-8"):
        st.write("""Permanecerá ativa para casos que não necessitam de movimentação financeira.""")

# --------------------- Rodapé ou qualquer extra -------------
st.write("---")
st.info("Dúvidas adicionais? Contate o setor responsável ou consulte a documentação interna.")
