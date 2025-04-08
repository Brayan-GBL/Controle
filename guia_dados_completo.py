conteudo = {
    "1. Cancelamento / Recusa de Pedidos": {
        "Quando usar?": """
        📋 **Cancelamento:** Quando o pedido e a NF ainda podem ser cancelados (prazo ≤ 7 dias, não expedido).<br>
        O setor de **Gestão de Pedidos** é o responsável por essa validação.<br><br>
        ❌ **Recusa/Desistência:** Quando o cliente recusa no ato da entrega ou desiste após a expedição.<br>
        O setor de **Transportes** deve ser acionado para retorno da mercadoria.
        """,
        "Procedimentos": """
        1. Emitir **RMA** no Oracle (sem transportadora e frete \"Sem frete\").<br>
           - Observação: \"Pedido cancelado\" ou \"Pedido recusado pelo cliente\".<br>
        2. Abrir **SAC**:<br>
           - Tipo: Solicitação<br>
           - Assunto: \"Cancelamento pedido xxx\" ou \"Pedido xxx recusado\"<br>
           - Informar: Área, Origem, Responsável, Tipo de venda, RMA, NF, Filial.<br>
        3. Para **LNE/Remessa Antecipada**, não emitir RMA. Abrir SAC normalmente e informar a NF remessa.<br>
        4. Logística Devolução:<br>
           - Emite a NF de devolução e notifica pelo CRM.<br>
           - Crédito será usado para abater a NF cancelada/recusada (financeiro).
        """,
        "Pontos Importantes": """
        ⚠️ Cancelamentos fora do prazo ou pedidos expedidos → Devolução simbólica.<br>
        ✅ SAC deve estar com todas informações completas para agilidade no processo.<br>
        📌 Sempre checar se a NF original já foi baixada no sistema.
        """
    },

    "2. Emissão de NF e Coleta (Não Contribuinte)": {
        "Quando usar?": """
        - Cliente sem **Inscrição Estadual (IE)**, sem permissão para emitir NF de devolução.<br>
        - A empresa (PSD) emite **nota de entrada** para retorno ao estoque.
        """,
        "Procedimentos": """
        1. Emitir **RMA** após verificar elegibilidade da devolução.<br>
        2. Abrir **SAC** com:<br>
           - Assunto: \"Solicitação NF e coleta (não contribuinte)\"<br>
           - Informar: RMA, NF, transportadora, filial, etc.<br>
        3. Logística Devolução:<br>
           - Emite NF de entrada e gera o crédito.<br>
           - Encaminha ao Transportes para coleta (acompanhamento via TMS).
        """,
        "Pontos Importantes": """
        📌 NF deve ser enviada ao cliente antes da coleta.<br>
        📦 Caixas devem estar lacradas, identificadas, com acesso facilitado.<br>
        ⚠️ Coleta cancelada após 2 tentativas frustradas de contato.
        """
    },

    "11. Instruções para Emissão de NF-e | Clientes Contribuintes": {
        "Regras Obrigatórias": """
        🧾 Todo cliente com **Inscrição Estadual ativa** deve obrigatoriamente emitir NF de devolução.<br><br>
        - Seguir rigorosamente as informações da **Autorização de Devolução (RMA)**.<br>
        - A NF deve refletir exatamente os dados da RMA (quantidade, CFOP, valores, descontos etc).<br>
        - Informar no campo de **Observações** o número da NF de origem.<br>
        - Enviar a mercadoria acompanhada da NF + RMA, em caixas apropriadas para transporte.
        """,
        "Correções por Carta de Correção": """
        ✍️ **Podem ser corrigidos:**<br>
        - CFOP (desde que não altere natureza de imposto)<br>
        - CST (sem alteração de valores)<br>
        - Dados do transportador<br>
        - Inserções adicionais: número do pedido, caixas, endereço (mesmo estado)<br><br>
        ❌ **Não podem ser corrigidos:**<br>
        - Valores fiscais (quantidade, preço)<br>
        - Mudanças cadastrais que alterem remetente/destinatário<br>
        - Impostos que alterem o cálculo final
        """,
        "Notas 623-8 e 624-6": """
        📌 **Nota 623-8 (Simples Faturamento)**<br>
        - Não gera coleta<br>
        - Não inserir dados de transportador<br><br>
        🚛 **Nota 624-6 (Venda Entrega Futura)**<br>
        - Gera coleta<br>
        - Inserir: Razão social, CNPJ, IE, Endereço c/ CEP<br>
        - Preencher: Quantidade de volumes, tipo (caixas), peso bruto e líquido
        """
    }
}

# Mantemos as transportadoras e operações como estão abaixo:

transportadoras = {
    "Braspress": """
    **CNPJ:** 48.740.351/0003-27  
    **Endereço:** RUA JOAO BETTEGA, 3802 – CIDADE INDUSTRIAL, CURITIBA/PR
    """,
    "Cruzeiro do Sul": """
    **CNPJ:** 03.232.675/0061-95  
    **Oracle:** 03232675006195-PR-PARCEL-Padrao  
    **Endereço:** AV. DEZ DE DEZEMBRO, 5680 – JARDIM PIZA, LONDRINA/PR
    """,
    "FL BRASIL (SOLISTICA)": """
    **CNPJ:** 18.233.211/0028-50  
    **IE:** 9076066008  
    **Endereço:** RODOVIA BR 116, 22301 – TATUQUARA, CURITIBA/PR
    """,
    "Local Express": """
    **CNPJ:** 06.199.523/0001-95  
    **IE:** 9030307558  
    **Endereço:** R FORMOSA, 131 – PLANTA PORTAL DA SERRA, PINHAIS/PR
    """,
    "Rodonaves": """
    **CNPJ:** 44.914.992/0017-03  
    **IE:** 6013031914  
    **Endereço:** RUA RIO GRANDE DO NORTE, 1200, CENTRO, LONDRINA/PR
    """
}

operacoes = {
    "Operação 163-1": """
⚙️ **Correções sistêmicas** como:  
- Ajuste de CNPJ  
- Descontos incorretos  
- Erros operacionais no SGE
""",
    "Operação 067-3": """
📘 **Exclusiva para**:  
- Vendas fora da Loja na Escola  
- Utilizada para regularização fiscal, sem movimentar estoque físico
""",
    "Operação 115-8": """
✅ **Sem movimentação financeira**  
- Fins administrativos ou ajustes sem impacto fiscal
"""
}
