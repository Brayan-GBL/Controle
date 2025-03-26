import streamlit as st

# ----------------- CSS (Firulas) ------------------
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

/* Subtítulo ou seções */
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

# ===================== CONTEÚDO =====================
# Vamos organizar cada tópico como um dicionário, contendo subitens ("Quando usar?", "Procedimentos", "Pontos Importantes").
# Para os tópicos 8 (Transportadoras) e 9 (Operações), podemos estruturar de forma levemente diferente.

conteudo = {
    "1. Cancelamento / Recusa de Pedidos": {
        "Quando usar?": """\
- **Cancelamento** se o pedido e NF puderem ser cancelados no sistema (até 7 dias). 
  O setor de Gestão de Pedidos confirma se não foi expedido.
- **Recusa/Desistência** se o cliente rejeitou o material no ato da entrega ou desistiu após expedição. 
  Acionar Transporte para retorno.
""",
        "Procedimentos": """\
1. **Emitir RMA** (se aplicável), sem transportadora e "FOB: Sem frete". Observações: "Pedido cancelado" ou "Pedido recusado".
2. **Abrir SAC** (Tipo: Solicitação; Assunto: "Cancelamento pedido X" ou "Pedido X recusado"). 
   Preencher Filial, RMA, NF, etc.
3. **Se LNE ou Remessa Antecipada**: Não emite RMA; siga o mesmo fluxo no SAC, marcando "Loja na Escola / Remessa antecipada" e NF da remessa LNE.
4. **Logística Devolução** emite NF de devolução, notifica via CRM e aplica crédito se for RMA.
""",
        "Pontos Importantes": """\
- Se exceder 7 dias ou já expedido, trata-se de devolução simbólica (não cancelamento).
- Em recusa no ato da entrega, o setor de Transportes deve acionar retorno da mercadoria.
- O financeiro usa o crédito p/ abater NF cancelada/recusada.
"""
    },

    "2. Emissão de NF e Coleta (Não Contribuinte)": {
        "Quando usar?": """\
- Cliente sem IE, impossibilitado de emitir NF de devolução.
- A empresa vendedora (PSD) emite nota de entrada para retorno ao estoque.
""",
        "Procedimentos": """\
1. **Verificar** se a devolução está dentro de regras (prazos, etc.).
2. **Emitir RMA** no ORACLE (ver "Devoluções Oracle - Como criar RMA").
3. **Abrir SAC** (Assunto: "Solicitação NF e coleta (não contribuinte)"), preenchendo Filial, RMA, NF, transportadora.
4. **Logística Devolução** emite NF, gera crédito, avisa CRM e Transportes para coleta (TMS).
""",
        "Pontos Importantes": """\
- Encaminhar NF ao cliente; o transportador pode exigir.
- A quantidade de caixas deve bater com a NF, lacradas e identificadas.
- Se houver 2 tentativas de coleta sem sucesso, cancela-se o agendamento.
"""
    },

    "3. Solicitação de Coleta (Contribuinte)": {
        "Quando usar?": """\
- Cliente com IE: ele emite a NF de devolução. 
- Frete normalmente FOB (destinatário). 
- Se o cliente pagar frete, veja "Devolução com Frete por Conta do Cliente".
""",
        "Procedimentos": """\
1. **Emitir RMA** no ORACLE (gera "Autorização de Devolução de Produto").
2. **Cliente** emite a NF de devolução, corrigindo se houver divergências.
3. **Abrir SAC** ("Solicitação NF e coleta contribuinte"), anexar PDF da NF se exigido.
4. **Logística Devolução** confere a NF; se correto, manda ao Transportes (TMS).
""",
        "Pontos Importantes": """\
- Notas acima de 15 dias podem ser recusadas.
- Caixas lacradas e identificadas (quantidade deve bater com a NF).
- Manter dados de contato atualizados p/ evitar falhas na coleta.
"""
    },

    "4. Emissão de NF e Coleta LNE": {
        "Quando usar?": """\
- Remessa antecipada / Loja na Escola (materiais em poder de terceiros).
- Sobras não vendidas precisam ser baixadas e recolhidas.
- Fluxo distinto, sem RMA (em geral).
""",
        "Procedimentos": """\
1. Confronte itens com relatórios SGE/Oracle.
2. Preencha formulário "LNE" com dados para emissão NF e coleta.
3. **Abra SAC** ("Emissão de NF e coleta LNE"), anexe formulário + NF Remessa LNE.
4. **Logística** emite NF, baixa estoque de terceiros, notifica CRM. 
   Transportes agenda coleta no TMS.
""",
        "Pontos Importantes": """\
- Encaminhar NF ao cliente p/ evitar problemas na coleta.
- Mesmo nº de caixas da NF, tudo lacrado e acessível.
- 2 tentativas sem sucesso cancelam a coleta.
"""
    },

    "5. Devolução c/ Frete por Conta do Cliente": {
        "Quando usar?": """\
- O cliente arca com frete (por contrato ou acordo). 
- Pode usar transportadora da base ou contratar própria.
""",
        "Procedimentos": """\
**Situação A: Cliente paga frete mas usa nossa transportadora**
1. Emita RMA (não contribuinte = FOB, contribuinte = CIF).
2. Abra SAC "Devolução com frete por conta do cliente," preencha Filial, RMA, NF. "Cliente irá contratar frete? Não."

**Situação B: Cliente contrata transportadora externa**
1. Se não contribuinte, ver se a transportadora está na base; se não, informe dados manualmente. Se contribuinte, ele define na NF.
2. Abra SAC igual acima, mas "Cliente irá contratar frete? Sim."
""",
        "Pontos Importantes": """\
- Se não contribuinte, Logística emite NF; se contribuinte, o cliente emite NF.
- Se usar nossa base, nós agendamos coleta. Se for outra, o cliente acompanha a mercadoria.
- Sempre encaminhar NF ao cliente; o transportador pode exigir.
"""
    },

    "6. Faturamento Vendas Fora do LNE": {
        "Quando usar?": """\
- Houve vendas por fora na escola (fora da plataforma).
- Precisamos ajustar estoque e faturar contra a escola.
""",
        "Procedimentos": """\
1. **Devolução simbólica** dos itens "fora" para corrigir estoque.
2. Emitir **pedido no SGE** (operação 067-3) sem movimentar estoque físico.
3. **Abrir SAC** p/ Logística Devolução, informar nº pedido SGE, NF Remessa LNE.
4. Logística emite nota de devolução simbólica, baixa saldo e fatura manualmente o pedido.
""",
        "Pontos Importantes": """\
- O solicitante é notificado via CRM quando concluído.
- Verifique sempre se há sobras ou divergências no SGE para não gerar mais devoluções.
"""
    },

    "7. Troca de NF (CNPJ/Desconto)": {
        "Quando usar?": """\
- Devolução simbólica/virtual, sem retorno físico. 
- Corrigir valores, desconto, CNPJ ou migrar tipo de venda (ex.: LNE → Direta).
""",
        "Procedimentos": """\
1. Emita RMA sem transportadora (FOB "Sem frete").
2. Observações: "Devolução simbólica."
3. Abra SAC ("Troca de NF p/ correção de desconto/CNPJ"), informe nº pedido SGE, NF p/ crédito.
4. Logística gera crédito para abater faturamento incorreto e cria novo faturamento.
""",
        "Pontos Importantes": """\
- Se for operação antecipada + remessa futura, podem ser 2 RMAs com mesmos itens.
- RMA e faturamento entram na mesma solicitação (tratativa sistêmica). 
- Verificar prazos; se muito tarde, pode ser recusado.
"""
    }
}

# Transportadoras e Operações, vamos tratar diferente
transportadoras = {
    "Braspress": """\
**CNPJ**: 48.740.351/0003-27  
Endereço: RUA JOAO BETTEGA, 3802 – CIDADE INDUSTRIAL, CURITIBA/PR
""",
    "Cruzeiro do Sul": """\
**CNPJ**: 03.232.675/0061-95  
No Oracle: "03232675006195-PR-PARCEL-Padrao"  
Endereço: AV. DEZ DE DEZEMBRO, 5680 – JARDIM PIZA, LONDRINA/PR
""",
    "FL BRASIL (SOLISTICA)": """\
**CNPJ**: 18.233.211/0028-50  
IE: 9076066008  
Endereço: RODOVIA BR 116, 22301 – TATUQUARA, CURITIBA/PR
""",
    "Local Express": """\
**CNPJ**: 06.199.523/0001-95  
IE: 9030307558  
Endereço: R FORMOSA, 131 – PLANTA PORTAL DA SERRA, PINHAIS/PR
""",
    "Rodonaves": """\
**CNPJ**: 44.914.992/0017-03  
IE: 6013031914  
Endereço: RUA RIO GRANDE DO NORTE, 1200, CENTRO, LONDRINA/PR
"""
}

operacoes = {
    "Operação 163-1": """Exclusiva para correções sistêmicas, como ajustes de CNPJ, descontos incorretos e erros de operação no SGE.""",
    "Operação 067-3": """Agora destinada apenas à correção de vendas realizadas fora da plataforma Loja na Escola.""",
    "Operação 115-8": """Permanecerá ativa para casos que não necessitam de movimentação financeira."""
}

# ===================== LÓGICA DE SELEÇÃO =====================

topicos_principais = list(conteudo.keys()) + ["8. Transportadoras", "9. Operações (115-8, 067-3, 163-1)"]

escolha_topico = st.selectbox("Selecione o tópico principal:", ["" ] + topicos_principais)

if escolha_topico:

    if escolha_topico in conteudo:
        # É um tópico normal (1 a 7) com subitens (Quando usar?, Procedimentos, Pontos Importantes)
        subitens = ["Quando usar?", "Procedimentos", "Pontos Importantes"]
        escolha_sub = st.selectbox("Selecione o subitem:", ["" ] + subitens)

        if escolha_sub:
            texto = conteudo[escolha_topico].get(escolha_sub)
            if texto:
                st.markdown(f"<div class='my-subtitle'>{escolha_sub}</div>", unsafe_allow_html=True)
                st.write(texto)
            else:
                st.write("Este subitem não possui texto definido.")

    elif escolha_topico == "8. Transportadoras":
        # Aqui temos um dict com cada transportadora
        nomes = list(transportadoras.keys())
        escolha_transp = st.selectbox("Selecione a Transportadora:", ["" ] + nomes)

        if escolha_transp:
            st.markdown(f"<div class='my-subtitle'>{escolha_transp}</div>", unsafe_allow_html=True)
            st.write(transportadoras[escolha_transp])

    elif escolha_topico == "9. Operações (115-8, 067-3, 163-1)":
        nomes_ops = list(operacoes.keys())
        escolha_op = st.selectbox("Selecione a Operação:", ["" ] + nomes_ops)

        if escolha_op:
            st.markdown(f"<div class='my-subtitle'>{escolha_op}</div>", unsafe_allow_html=True)
            st.write(operacoes[escolha_op])

# ------------- RODAPÉ -------------
st.write("---")
st.info("Dúvidas adicionais? Contate o setor responsável ou consulte a documentação interna.")
