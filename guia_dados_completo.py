# -*- coding: utf-8 -*-
"""
Arquivo: guia_dados_completo.py
Conteúdo: dicionários com todo o Guia de Devolução completo, incluindo tópicos 1 a 7, 8 (Tipos de RMA), 10 (Dúvidas Frequentes), 11 (Instruções NF-e Contribuintes) e 12 (Operações).
"""

# ------------------- DADOS DO GUIA DE DEVOLUÇÃO -------------------

# Conteúdo principal: tópicos 1 a 7, 8 e 10
conteudo = {
    "1. Cancelamento / Recusa de Pedidos": {
        "Quando usar?": '''
📋 **Cancelamento:** Quando o pedido e a NF ainda podem ser cancelados (prazo ≤ 7 dias, não expedido).  
❌ **Recusa/Desistência:** Quando o cliente recusa no ato da entrega ou desiste após a expedição.
''',
        "Procedimentos": '''
1. Emitir **RMA** no Oracle (sem transportadora e com FOB "Sem frete").  
2. Abrir **SAC** (Tipo: Solicitação; Assunto: "Cancelamento pedido XXX" ou "Pedido XXX recusado").  
3. Para LNE/Remessa Antecipada: não emitir RMA; abrir SAC com NF de remessa LNE.  
4. Logística Devolução emite NF de devolução, notifica CRM e gera crédito para abater NF original.
''',
        "Pontos Importantes": '''
⚠️ Cancelamentos fora do prazo ou pedidos já expedidos → devolução simbólica.  
✅ SAC deve conter todas as informações para agilidade.  
📌 Conferir se a NF original já foi baixada no sistema.
'''
    },
    "2. Emissão de NF e Coleta (Não Contribuinte)": {
        "Quando usar?": '''
- Cliente **sem IE** (Inscrição Estadual) sem autorização para emitir NF de devolução.  
- A empresa (ARCO) emite nota de entrada para retorno ao estoque.
''',
        "Procedimentos": '''
1. Emitir **RMA** após validação da solicitação.  
2. Abrir **SAC** (Assunto: "Solicitação NF e coleta (não contribuinte)").  
3. Logística Devolução emite NF de devolução, integra no Oracle e notifica CRM.  
4. Encaminha NF ao Transportes para coleta (acompanhamento via TMS).
''',
        "Pontos Importantes": '''
📌 Enviar NF de devolução ao cliente (transportador pode exigir).  
📦 Caixas lacradas, identificadas e com fácil acesso.  
⚠️ Coleta cancelada após 2 tentativas frustradas.
'''
    },
    "3. Solicitação de Coleta (Contribuinte)": {
        "Quando usar?": '''
- Cliente **com IE** emite a NF de devolução (espelho do RMA).  
- Frete por conta do destinatário (FOB).  
- Se cliente pagar frete, seguir procedimento de Devolução c/ Frete por Conta.
''',
        "Procedimentos": '''
1. Emitir **RMA** no Oracle (gera Autorização de Devolução).  
2. Cliente emite NF de devolução e envia ao solicitante.  
3. Abrir **SAC** (Assunto: "Solicitação NF e coleta contribuinte"; anexar PDF da NF).  
4. Logística confere NF, encaminha a Transportes (TMS).
''',
        "Pontos Importantes": '''
⚠️ Notas com emissão > 15 dias podem ser recusadas.  
📦 Caixas lacradas e mesmo número da NF.  
📞 Contato atualizado para manter Agendamento.
'''
    },
    "4. Emissão de NF e Coleta LNE": {
        "Quando usar?": '''
- Remessa antecipada / Loja na Escola (materiais em poder de terceiros).  
- Sobras não vendidas requerem baixa e recolhimento.
''',
        "Procedimentos": '''
1. Confrontar itens com relatórios SGE/Oracle.  
2. Preencher formulário "LNE" para emissão de NF e coleta.  
3. Abrir **SAC** (Assunto: "Emissão de NF e coleta LNE"; anexo: formulário + NF Remessa LNE).  
4. Logística emite NF, baixa estoque de terceiros e notifica CRM; Transportes agenda coleta via TMS.
''',
        "Pontos Importantes": '''
📌 Enviar NF de devolução ao cliente.  
📦 Mesma quantidade de caixas da NF, lacradas e acessíveis.  
⚠️ Coleta cancelada após 2 tentativas sem sucesso.
'''
    },
    "5. Devolução com Frete por Conta do Cliente": {
        "Quando usar?": '''
- Cliente deve arcar com o frete (por contrato ou acordo).  
- Pode usar transportadora da base ou própria.
''',
        "Procedimentos": '''
**Cenário A: Usa transportadora da base**  
- Emitir RMA (não contribuinte: FOB; contribuinte: CIF).  
- Abrir **SAC** ('Devolução com frete por conta do cliente'; frete contratado = Não).  

**Cenário B: Cliente contrata externa**  
- Verificar se transportadora já está na base; se não, informar dados manualmente.  
- Abrir SAC igual, mas 'Cliente irá contratar frete? Sim'.
''',
        "Pontos Importantes": '''
📌 Se externa, o cliente acompanha o transporte.  
✅ Se interna, Logística agenda coleta.  
📌 Sempre anexar NF se contribuinte.
'''
    },
    "6. Faturamento Vendas Fora do LNE": {
        "Quando usar?": '''
- Vendas negociadas diretamente na escola (fora do LNE).  
- Ajustar estoque e faturar contra a escola.
''',
        "Procedimentos": '''
1. Devolução simbólica dos itens vendidos fora para corrigir estoque.  
2. Emitir pedido no SGE (operação 067-3, sem movimentar estoque).  
3. Abrir **SAC** (Assunto: "Faturamento vendas fora do LNE"; informar nº pedido SGE e NF Remessa LNE).  
4. Logística emite nota simbólica, baixa saldo e fatura manualmente o pedido.
''',
        "Pontos Importantes": '''
📌 Solicitações monitoradas via CRM.  
📊 Verificar relatórios de vendas para evitar repetição.
'''
    },
    "7. Troca de NF para Correção de CNPJ / Desconto": {
        "Quando usar?": '''
- Processo virtual (sem coleta física).  
- Corrigir valores, desconto, CNPJ ou migrar tipo de venda.
''',
        "Procedimentos": '''
1. Emitir RMA sem transportadora (FOB “Sem frete”), observação "Devolução simbólica".  
2. Abrir **SAC** (Assunto: "Troca de NF para correção de desconto/CNPJ").  
3. Informar nº pedido SGE, RMA, NF p/ crédito.  
4. Logística gera crédito e provisão para novo faturamento correto.
''',
        "Pontos Importantes": '''
⚠️ Para faturamento antecipado + remessa futura, usar 2 RMAs.  
📌 RMA e faturamento devem estar na mesma solicitação.
'''
    },
    "8. Tipos de RMA (Referência Rápida)": {
        "Referência Rápida": '''
• **RMA DEV BONIF** – NF Remessa bonificação, doação ou brinde.  
• **RMA DEV SIMP FAT ENT FUT** – NF Simples Faturamento p/ entrega futura.  
• **RMA DEV VDA ENT FUT** – NF Venda de mercadoria p/ entrega futura.  
• **RMA DEV VENDA** – NF Venda de mercadoria e/ou recebida de terceiros.  
• **RMA SAIDAS DIVER C/ ICMS** – NF Outras saídas/remessas diversas.
'''
    },
    "9. Dúvidas Frequentes": {
        "Pergunta 1": "**Q:** SLA para emissão de etiqueta após abertura de chamado? **A:** 5 dias úteis para emissão de NF e etiqueta.",
        "Pergunta 2": "**Q:** Após geração, retornam ao atendimento ou mandam direto à escola? **A:** Retornamos ao time de atendimento; eles encaminham NF e etiqueta à escola.",
        "Pergunta 3": "**Q:** Prazo para coleta após envio de etiqueta? **A:** 3-5 dias úteis em capitais/metrópoles; 7-10 dias úteis interior.",
        "Pergunta 4": "**Q:** Quem confere material no CD e prazo? **A:** Recebido pela Posigraf; time interno faz conferência em até 10 dias úteis.",
        "Pergunta 5": "**Q:** Ajuste de estoque após triagem? **A:** PSD tem 10 dias úteis para devolução de compra; Posigraf tem 7 dias úteis p/ reintegração; materiais avariados são descartados."
    },
    "10. Instruções para Emissão de NF-e | Clientes Contribuintes": {
        "Instruções Gerais": '''
Clientes com **IE ativa** devem emitir NF-e de devolução.  
- Seguir dados do RMA: Natureza de Operação, CFOP, quantidade, valor unitário, desconto e total.  
- Informar no campo Observação: nº da NF de origem.  
- A mercadoria deve acompanhar NF + RMA em caixas apropriadas.
''',
        "Notas Especiais": '''
✍️ **Carta de correção aceita para:** CFOP, CST, dados do transportador, razão social parcial, dados adicionais (pedido, caixas, endereço no mesmo estado).  
🚫 **Não aceita:** valores fiscais, mudança de destinatário/remetente, impostos que alterem cálculo.  
📄 **Referências de operações:**  
- 623-8 (Simples Faturamento): não gera coleta.  
- 624-6 (Venda Entrega Futura): gera coleta e exige dados completos do transportador.
'''
    },
    "11. Operações (115-8, 067-3, 163-1)": {
        "Detalhamento": '''
🔢 **163-1:** Correções sistêmicas (CNPJ, descontos, erros SGE).  
🔁 **067-3:** Faturamento simbólico de vendas fora do LNE.  
💼 **115-8:** Devoluções sem movimentação financeira.
'''
    }
}

# Dados auxiliares: transportadoras e operações (separados no código principal)
transportadoras = {
    "Braspress": "CNPJ: 48.740.351/0003-27 — RUA JOAO BETTEGA, 3802, CURITIBA/PR",
    "Cruzeiro do Sul": "CNPJ: 03.232.675/0061-95 — AV. DEZ DE DEZEMBRO, 5680, LONDRINA/PR",
    "FL Brasil (Solistica)": "CNPJ: 18.233.211/0028-50 — ROD BR-116, 22301, TATUQUARA/PR",
    "Local Express": "CNPJ: 06.199.523/0001-95 — R FORMOSA, 131, PINHAIS/PR",
    "Rodonaves": "CNPJ: 44.914.992/0017-03 — RUA RIO GRANDE DO NORTE, 1200, LONDRINA/PR"
}

operacoes = {
    "Operação 163-1": "Correções sistêmicas (CNPJ, descontos, erros SGE)",
    "Operação 067-3": "Faturamento simbólico p/ vendas fora do LNE",
    "Operação 115-8": "Devoluções sem movimentação financeira"
}
