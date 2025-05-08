conteudo = {
    "1. Cancelamento / Recusa de Pedidos": {
        "Quando usar?": """
        📋 **Cancelamento:** Quando o pedido e a NF ainda podem ser cancelados (prazo ≤ 7 dias, não expedido).
        O setor de **Gestão de Pedidos** é o responsável por essa validação.

        ❌ **Recusa/Desistência:** Quando o cliente recusa no ato da entrega ou desiste após a expedição.
        O setor de **Transportes** deve ser acionado para retorno da mercadoria.
        """,
        "Procedimentos": """
        1. Emitir **RMA** no Oracle (sem transportadora e frete \"Sem frete\").
           - Observação: \"Pedido cancelado\" ou \"Pedido recusado pelo cliente\".
        2. Abrir **SAC**:
           - Tipo: Solicitação
           - Assunto: \"Cancelamento pedido xxx\" ou \"Pedido xxx recusado\"
           - Informar: Área, Origem, Responsável, Tipo de venda, RMA, NF, Filial.
        3. Para **LNE/Remessa Antecipada**, não emitir RMA. Abrir SAC normalmente e informar a NF remessa.
        4. Logística Devolução:
           - Emite a NF de devolução e notifica pelo CRM.
           - Crédito será usado para abater a NF cancelada/recusada (financeiro).
        """,
        "Pontos Importantes": """
        ⚠️ Cancelamentos fora do prazo ou pedidos expedidos → Devolução simbólica.
        ✅ SAC deve estar com todas informações completas para agilidade no processo.
        📌 Sempre checar se a NF original já foi baixada no sistema.
        """
    },

    "2. Emissão de NF e Coleta (Não Contribuinte)": {
        "Quando usar?": """
        - Cliente sem **Inscrição Estadual (IE)**, sem permissão para emitir NF de devolução.
        - A empresa (PSD) emite **nota de entrada** para retorno ao estoque.
        """,
        "Procedimentos": """
        1. Emitir **RMA** após verificar elegibilidade da devolução.
        2. Abrir **SAC** com:
           - Assunto: \"Solicitação NF e coleta (não contribuinte)\"
           - Informar: RMA, NF, transportadora, filial, etc.
        3. Logística Devolução:
           - Emite NF de entrada e gera o crédito.
           - Encaminha ao Transportes para coleta (acompanhamento via TMS).
        """,
        "Pontos Importantes": """
        📌 NF deve ser enviada ao cliente antes da coleta.
        📦 Caixas devem estar lacradas, identificadas, com acesso facilitado.
        ⚠️ Coleta cancelada após 2 tentativas frustradas de contato.
        """
    },

    "3. Solicitação de Coleta (Contribuinte)": {
        "Quando usar?": """
        - Cliente com **Inscrição Estadual (IE)**: é o emissor da NF de devolução.
        - Utiliza-se CFOP e dados da RMA. Frete normalmente **FOB** (por conta da empresa).
        """,
        "Procedimentos": """
        1. Emitir **RMA** no Oracle → Gera Autorização de Devolução.
        2. Cliente emite **NF de devolução** com base na autorização.
        3. Abrir **SAC**:
           - Assunto: \"Solicitação NF e coleta contribuinte\"
           - Anexar PDF da NF emitida.
        4. Logística Devolução:
           - Confere NF, notifica CRM, e envia ao Transportes (TMS).
        """,
        "Pontos Importantes": """
        ⚠️ NF com mais de 15 dias pode ser recusada.
        📌 Checar se CFOP e dados da nota estão corretos.
        ✅ Manter dados de contato atualizados para evitar falhas.
        """
    },

    "4. Emissão de NF e Coleta LNE": {
        "Quando usar?": """
        - Para materiais em poder de terceiros (LNE / Remessa Antecipada).
        - Quando há sobras não vendidas e é necessário recolher.
        """,
        "Procedimentos": """
        1. Validar os itens com relatórios do SGE / Oracle.
        2. Preencher o formulário LNE com todas as informações.
        3. Abrir SAC: \"Emissão de NF e coleta LNE\" e anexar formulário + NF Remessa.
        4. Logística Devolução:
           - Emite a NF, baixa saldo de terceiros, avisa CRM e aciona coleta via TMS.
        """,
        "Pontos Importantes": """
        📦 Caixas lacradas, identificadas e acessíveis.
        ⚠️ A coleta será cancelada após 2 tentativas sem sucesso.
        ✅ Enviar NF ao cliente antes da coleta.
        """
    },

    "5. Devolução com Frete por Conta do Cliente": {
        "Quando usar?": """
        - Cliente arca com o frete (conforme contrato ou exceção).
        - Pode usar transportadora parceira ou própria.
        """,
        "Procedimentos": """
        1. Emitir RMA:
           - Não contribuinte: frete FOB
           - Contribuinte: frete CIF
        2. Abrir SAC:
           - Assunto: \"Devolução com frete por conta do cliente\"
           - Informar: RMA, tipo, transportadora, se o cliente irá contratar frete, PDF da NF (contribuinte).
        """,
        "Pontos Importantes": """
        ✅ NF deve ser enviada ao cliente.
        ⚠️ Cliente com transportadora própria: responsabilidade total pela logística.
        📦 Caixas conforme NF, lacradas e acessíveis.
        """
    },

    "6. Faturamento de Vendas Fora do LNE": {
        "Quando usar?": """
        - Identificadas vendas fora dos canais oficiais da Loja na Escola.
        - Ajuste necessário no estoque e faturamento.
        """,
        "Procedimentos": """
        1. Gerar pedido no SGE com operação 067-3 (sem movimentar estoque).
        2. Abrir SAC com número do pedido e NF remessa LNE.
        3. Logística emite NF simbólica e fatura o pedido.
        """,
        "Pontos Importantes": """
        📌 Evita divergência de estoque e cobrança indevida.
        ✅ Sempre verificar registros de vendas com a escola.
        """
    },

    "7. Troca de NF por Correção de CNPJ/Desconto": {
        "Quando usar?": """
        - Ajustes como:
            • Correção de valores e descontos
            • CNPJ incorreto
            • Migração de venda (ex: LNE → Direta)
        """,
        "Procedimentos": """
        1. Emitir RMA simbólica (sem transportadora, "Sem frete").
        2. Informar observação: \"Devolução simbólica\".
        3. Abrir SAC:
           - Assunto: \"Troca de NF para correção de desconto/CNPJ\"
           - Informar pedido SGE, NF original, tipo de venda, etc.
        4. Logística realiza crédito e emite novo faturamento.
        """,
        "Pontos Importantes": """
        ⚠️ Faturamento virtual exige itens/quantidades idênticos à nota original.
        ✅ Pedido e RMA devem ser processados no mesmo dia.
        """
    }
}

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
