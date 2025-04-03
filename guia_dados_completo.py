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

    "3. Solicitação de Coleta (Contribuinte)": {
        "Quando usar?": """
        - Cliente com **Inscrição Estadual (IE)**: é o emissor da NF de devolução.<br>
        - Utiliza-se CFOP e dados da RMA. Frete normalmente **FOB** (por conta da empresa).
        """,
        "Procedimentos": """
        1. Emitir **RMA** no Oracle → Gera Autorização de Devolução.<br>
        2. Cliente emite **NF de devolução** com base na autorização.<br>
        3. Abrir **SAC**:<br>
           - Assunto: \"Solicitação NF e coleta contribuinte\"<br>
           - Anexar PDF da NF emitida.<br>
        4. Logística Devolução:<br>
           - Confere NF, notifica CRM, e envia ao Transportes (TMS).
        """,
        "Pontos Importantes": """
        ⚠️ NF com mais de 15 dias pode ser recusada.<br>
        📌 Checar se CFOP e dados da nota estão corretos.<br>
        ✅ Manter dados de contato atualizados para evitar falhas.
        """
    },

    "4. Emissão de NF e Coleta LNE": {
        "Quando usar?": """
        - Para materiais em poder de terceiros (LNE / Remessa Antecipada).<br>
        - Quando há sobras não vendidas e é necessário recolher.
        """,
        "Procedimentos": """
        1. Validar os itens com relatórios do SGE / Oracle.<br>
        2. Preencher o formulário LNE com todas as informações.<br>
        3. Abrir SAC: \"Emissão de NF e coleta LNE\" e anexar formulário + NF Remessa.<br>
        4. Logística Devolução:<br>
           - Emite a NF, baixa saldo de terceiros, avisa CRM e aciona coleta via TMS.
        """,
        "Pontos Importantes": """
        📦 Caixas lacradas, identificadas e acessíveis.<br>
        ⚠️ A coleta será cancelada após 2 tentativas sem sucesso.<br>
        ✅ Enviar NF ao cliente antes da coleta.
        """
    },

    "8. Tipos de RMA (Referência Rápida)": {
        "Tabela de Tipos de Nota e RMA": """
        | Tipo de Nota                                      | Tipo de Ordem (RMA)              |
        |--------------------------------------------------|----------------------------------|
        | Remessa bonificação, doação ou brinde            | P15 - RMA DEV BONIF              |
        | Venda de mercadoria de encomenda futura         | P15 - RMA DEV VDA ENT FUT        |
        | Devolução de Vendas                              | P15 - RMA DEV VENDA              |
        | Outras Saídas – Remessas Diversas                | P15 - RMA SAIDAS DIVER C/ ICMS   |
        """,
        "Significado dos Códigos": """
        - **RMA DEV BONIF** → NF de Remessa bonificação, doação ou brinde<br>
        - **RMA DEV SIMP FAT ENT FUT** → NF de Simples Faturamento para Entrega Futura<br>
        - **RMA DEV VDA ENT FUT** → NF de Venda de mercadoria Orig. de Encomenda Futura<br>
        - **RMA DEV VENDA** → NF de Venda de Mercadoria e/ou recebida de terceiros<br>
        - **RMA SAIDAS DIVER C/ICMS** → NF de Outras Saídas / Remessas Diversas
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
