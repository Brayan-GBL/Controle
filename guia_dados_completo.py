conteudo = {
    "1. Cancelamento / Recusa de Pedidos": {
        "Quando usar?": """
        📋 **Cancelamento:** Quando o pedido e a NF ainda podem ser cancelados (prazo ≤ 7 dias, não expedido).
        O setor de **Gestão de Pedidos** realiza a validação e baixa automática.
        
        ❌ **Recusa/Desistência:** Cliente recusa no ato da entrega ou desiste após expedição.
        Acionar o setor de **Transportes** para retorno imediato da mercadoria.
        """,
        "Procedimentos": """
        1. **Emitir RMA** no Oracle:
           - Transportadora: vazio; Frete: “Sem frete”.
           - Observação: “Pedido cancelado” ou “Pedido recusado pelo cliente”.
        2. **Abrir SAC**:
           - Tipo: Solicitação
           - Assunto: “Cancelamento pedido XXX” ou “Pedido XXX recusado”
           - Informar: Área/Processo, Origem, Responsável, Tipo de Venda, RMA, NF e Filial.
        3. **Exceções LNE/Remessa:** Sem RMA; abra SAC e selecione “Loja na Escola / Remessa antecipada” e informe NF de remessa LNE.
        4. **Tratativa Logística:** Emite NF de devolução, notifica pelo CRM e o financeiro aplica crédito para abater a NF cancelada/recusada.
        5. **Comunicação:** Avisar o cliente sobre o status da devolução e previsão de crédito.
        """,
        "Pontos Importantes": """
        1. ⚠️ Cancelamentos fora do prazo ou pedidos expedidos → deve usar devolução simbólica.
        2. ✅ SAC completo e correto acelera todo o processo.
        3. 📌 Verificar no sistema se a NF original já foi baixada antes de abrir o SAC.
        4. 🔔 Notificar sempre o solicitante sobre a confirmação do retorno de mercadoria.
        """
    },
    "2. Emissão de NF e Coleta (Não Contribuinte)": {
        "Quando usar?": """
        - Cliente sem **Inscrição Estadual (IE)**; não pode emitir NF de entrada.
        - A PSD emite **nota de entrada** para retorno ao estoque da gráfica.
        - Uso: devoluções de bonificações, remessas de teste e pedidos cancelados fora de prazo.
        """,
        "Procedimentos": """
        1. **Conferir regras:** Quantidades, prazos e itens conforme política de devolução.
        2. **Emitir RMA** no Oracle seguindo o manual “Devoluções Oracle - Como criar RMA”.
        3. **Abrir SAC**:
           - Assunto: “Solicitação NF e coleta (não contribuinte)”
           - Informar: RMA, NF para crédito, nome da transportadora, Filial e demais campos.
        4. **Tratativa Logística:**
           - Emite NF de devolução/entrada e integra no Oracle para crédito.
           - Encaminha NF ao setor de Transportes; coleta agendada e acompanhada via TMS.
        5. **Confirmação:** Enviar cópia da NF ao cliente e ao solicitante para garantir que transportador tenha o documento.
        """,
        "Pontos Importantes": """
        📌 Enviar NF e RMA ao cliente ANTES da coleta; transportadora pode solicitar no momento.
        📦 Caixas lacradas, identificadas e em local acessível.
        ⏳ Coleta cancelada após 2 tentativas sem retorno ou itens não conformes.
        🔍 Verificar no TMS se a coleta foi confirmada e informar o solicitante.
        """
    },
    "3. Solicitação de Coleta (Contribuinte)": {
        "Quando usar?": """
        - Cliente com **IE ativa**; ele emite a NF de devolução.
        - Frete normalmente **FOB** (frete por conta do destinatário).
        - Em casos de frete pago pelo cliente, seguir procedimento “Devolução com Frete por Conta do Cliente”.
        """,
        "Procedimentos": """
        1. **Emitir RMA** no Oracle (gera “Autorização de Devolução de Produto”).
        2. **Cliente emite NF**:
           - Validar CFOP, quantidade, valores e dados de transporte.
           - Enviar PDF da NF ao solicitante.
        3. **Abrir SAC**:
           - Assunto: “Solicitação NF e coleta contribuinte”.
           - Anexar PDF da NF e preencher dados: RMA, transportadora, Filial.
        4. **Tratativa Logística:**
           - Conferir NF vs RMA; recusar SAC se houver divergências.
           - Enviar à Transportes para coleta no TMS após conferência.
        5. **Pós-coleta:** Confirmar retorno ao CD e gerar nota de entrada simbólica para estoque.
        """,
        "Pontos Importantes": """
        ⚠️ Notas com emissão > 15 dias podem ser recusadas.
        📦 Caixas lacradas e identificadas; quantidade igual à NF.
        📞 Confirmar dados de contato e porta/recepção antes da coleta.
        🔄 Em caso de recusa de SAC, documentar motivo e instruir cliente para correção rápida.
        """
    },
    "4. Emissão de NF e Coleta LNE": {
        "Quando usar?": """
        - Materiais em poder de terceiros (Loja na Escola / Remessa antecipada).
        - Itens não vendidos devem ser recolhidos e baixados do sistema.
        """,
        "Procedimentos": """
        1. **Confrontar dados** com relatórios SGE/Oracle para identificar quantidades.
        2. **Preencher formulário LNE** (disponível no CRM), incluindo dados de NF e coleta.
        3. **Abrir SAC**:
           - Assunto: “Emissão de NF e coleta LNE”.
           - Anexar formulário LNE e informar NF Remessa LNE.
        4. **Tratativa Logística:**
           - Emite NF de coleta, baixa estoque de terceiros e notifica CRM.
           - Coleta gerenciada pelo TMS.
        5. **Follow-up:** Verificar no TMS se a coleta ocorreu e informar o solicitante.
        """,
        "Pontos Importantes": """
        📌 Sempre enviar NF e formulário ao cliente; transportadora exige no local.
        📦 Mesma quantidade e tipo de embalagens descritas na NF.
        ⏳ Coleta cancelada após 2 tentativas sem sucesso.
        🔔 Registrar histórico de solicitações em CRM para rastreabilidade.
        """
    },
    "5. Devolução c/ Frete por Conta do Cliente": {
        "Quando usar?": """
        - Cliente assume o frete (contrato ou escolha própria).
        - Pode usar transportadora da base ou outra de escolha do cliente.
        """,
        "Procedimentos": """
        **A. Cliente paga via nossa transportadora**
        1. Emitir RMA: Não contribuinte = **FOB**; Contribuinte = **CIF**.
        2. Abrir SAC: Assunto “Devolução com frete por conta do cliente”; Informar RMA e NF.
        - Cliente contrata? “Não”.

        **B. Cliente contrata transportadora externa**
        1. Verificar se a transportadora externa está cadastrada; se não, informe dados (Nome/CNPJ/IE/Endereço).
        2. Emitir RMA com campo de transportadora em branco e frete “FOB”.
        3. Abrir SAC: Cliente contrata? “Sim”; preencher dados da transportadora.
        4. Logística: Emite ou integra NF, envia coleta ou instruções ao cliente.
        """,
        "Pontos Importantes": """
        📌 Confirmar pagamento do frete antes de emitir RMA.
        ⏳ Acompanhar coleta: nossa base vs transportadora externa.
        📄 Manter cópia da NF e comprovante de frete no CRM.
        🔔 Notificar solicitante sobre prazos de coleta e eventuais atrasos.
        """
    },
    "6. Faturamento Vendas Fora do LNE": {
        "Quando usar?": """
        - Vendas negociadas diretamente na escola (fora do sistema oficial).
        - Ajuste de estoque via devolução simbólica e faturamento contra a escola.
        """,
        "Procedimentos": """
        1. Emitir **devolução simbólica** para ajustar estoque (sem movimentação física).
        2. Criar pedido no SGE (operação **067-3**) que não mexe no estoque.
        3. Abrir SAC: Assunto “Faturamento vendas fora do LNE”; incluir nº pedido SGE e NF Remessa LNE.
        4. Logística: Emite nota de devolução simbólica, baixa estoque em poder de terceiros e fatura pedido.
        5. Validar no CRM e enviar confirmação ao solicitante.
        """,
        "Pontos Importantes": """
        ⚠️ Usar operação correta (067-3) para não gerar inconsistência de estoque.
        ⏳ Prazo de processamento: até 3 dias úteis após triagem.
        📌 Garantir que NF Remessa LNE esteja anexada e conferida.
        """
    },
    "7. Troca de NF p/ Correção de CNPJ / Desconto": {
        "Quando usar?": """
        - Processo **virtual** sem retorno de mercadoria.
        - Corrigir valores, descontos, CNPJ ou migrar tipo de venda (ex.: LNE → Direta).
        """,
        "Procedimentos": """
        1. Emitir RMA simbólica sem transportadora (FOB “Sem frete”).
        2. Adicionar observação “Devolução simbólica – correção de desconto/CNPJ”.
        3. Abrir SAC: Assunto “Troca de NF p/ correção de desconto/CNPJ”; informar nº pedido SGE e NF p/ crédito.
        4. Logística: Emite nota de devolução simbólica, abate crédito e gera novo faturamento.
        5. Para operações antecipadas (623-8/624-6), podem ser **2 RMAs** – remessa futura & faturamento.
        """,
        "Pontos Importantes": """
        📌 RMA e novo faturamento devem ser enviados na mesma solicitação.
        ⚠️ Carta de correção não abrange valores fiscais ou mudança de remetente.
        🔄 Conferir operação correta (115-8, 067-3 ou 163-1) antes de reaplicar.
        """
    },
    "Tipos de RMA (Referência Rápida)": {
        "Referência Rápida": '''
        • **P15-RMA DEV BONIF** – NF Remessa bonificação, doação ou brinde.  
        • **P15-RMA DEV SIMP FAT ENT FUT** – NF Simples Faturamento p/ entrega futura.  
        • **P15-RMA DEV VDA ENT FUT** – NF Venda de mercadoria p/ entrega futura.  
        • **P15-RMA DEV VENDA** – NF Venda de mercadoria e/ou recebida de terceiros.  
        • **P15-RMA SAIDAS DIVER C/ ICMS** – NF Outras saídas/remessas diversas.
        '''
    },

    "Dúvidas Frequentes": {
        "Sla SAC": "**P:** SLA para emissão de Nota e etiqueta após abertura de chamado? \n**R:** 5 dias úteis para emissão de NF e etiqueta.",
        "Prazo de coleta": "**P:** Prazo para coleta após envio de etiqueta? **R:** 3-5 dias úteis em capitais/metrópoles; 7-10 dias úteis interior.",
        "Conferência de material": "**P:** Quem confere material no CD e prazo? **R:** Recebido pela Posigraf; time interno faz conferência em até 10 dias úteis.",
        "Prazo de internalização": "**P:** Ajuste de estoque após triagem? **R:** PSD tem 10 dias úteis para devolução de compra; Posigraf tem 7 dias úteis p/ reintegração; materiais avariados são descartados.",
"Geração da NF de coleta/devolução": """
        A geração da NF é feita pelo time de Devolução.
        - Em casos de venda direta (venda de mercadoria, bonificação, outras saídas – remessas diversas), ela é emitida através da RMA.
        - Para remessas à escola, utilizamos uma ordem gerada a partir do pedido de origem.
        Se a escola tiver e-mail cadastrado, recebe a NF por e-mail; além disso, inserimos a NF no SAC do Zoho, e o Analista encaminha para a escola junto com a etiqueta de devolução.
        """,
    "Geração de etiquetas para as caixas": """
        A geração é feita pelo EBS:
        - Usamos o número da NF para clientes não-contribuintes e B2C.
        - Usamos o número da RMA para clientes contribuintes.
        Colocamos essa informação na solicitação de coleta e orientamos o Analista sobre o que deve ser encaminhado para a escola, garantindo a assertividade no ato da coleta.
        """,
    "Solicitação de coleta ao time de transportes": """
        Após finalizar o SAC, alteramos o status para Log Tracking.
        O time de Transporte tem acesso aos SACs processados no dia anterior via relatório extraído diretamente do Zoho.
        A partir daí, eles conferem todas as solicitações e entram em contato com as transportadoras responsáveis para agendar as coletas.
        """,
    "Pós-conferência e baixa de saldo no EBS": """
        - Para coleta LNE e clientes não-contribuintes: o saldo é baixado antes de finalizarmos a solicitação de coleta.
          • Escrituramos a NF no RI (Recebimento Integrado) no Oracle para baixar o saldo e enviar ao nosso subventário P15-DEV.CLIENT.
          • Quando o material chega na gráfica, o saldo já está no sistema para efetuar a devolução à Posigraf.
        - Para clientes contribuintes: como o cliente emite a NF, precisamos aguardar o recebimento dessa NF na gráfica antes de escriturar e lançar o saldo no subventário.
        O lançamento dos itens fica vinculado à RMA criada pelo Analista na solicitação de coleta.
        """,
    "Tratamento de divergências": """
        - Materiais enviados a mais (sobra) são direcionados para descarte.
        - Para materiais não enviados, sinalizados como falta ou avariados, ainda estamos construindo o processo de cobrança das escolas (nível Arco).
        """,
    "Cobrança e operações especiais": """
        - Não cobrar da escola (falta/avaria): o Analista deve cadastrar um pedido na operação 115-8 (que não movimenta financeiro, apenas estoque) e abrir um SAC de “Troca de NF” no Zoho para Logística Devolução.
        - Venda irregular (fora do LNE): antes de gerar a NF de devolução, o Analista envia o formulário LNE com os itens vendidos fora do LNE e abre uma solicitação de “Faturamento de vendas fora do LNE” para cobrar esses itens da escola.
        """
    },

    "Instruções para Emissão de NF-e | Clientes Contribuintes": {
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
        - 623-8 (Simples Faturamento): não gera coleta e não há necessidade de inserir os dados do transportador.  
        - 624-6 (Venda Entrega Futura): gera coleta e exige dados completos do transportador.
        '''
    },
    "Malha Transportadora": {
        "MALHA TRANSPORTADORA PARA COLETA REVERSA": '''
        LOCALIDADE | TRANSPORTADORA  
        - AC | BRASPRESS
        - AL | BRASPRESS
        - AM | BRASPRESS
        - AP | BRASPRESS
        - BA | BRASPRESS
        - CE | BRASPRESS
        - DF | RODONAVES
        - ES | RODONAVES
        - GO | RODONAVES
        - MA | BRASPRESS
        - MG | EAGLE
        - MS | RODONAVES
        - MT | EAGLE
        - PA | BRASPRESS
        - PB | BRASPRESS
        - PE | BRASPRESS
        - PI | BRASPRESS
        - PR | LOCAL
        - RJ | RODONAVES
        - RN | BRASPRESS
        - RO | BRASPRESS
        - RR | BRASPRESS
        - RS | LOCAL
        - SC | LOCAL
        - SE | BRASPRESS
        - SP | RODONAVES
        - TO | BRASPRESS
        '''
    }
}

transportadoras = {
    "Braspress": """
    **Razão Social:** BRASPRESS TRANSPORTES URGENTES LTDA
    **CNPJ:** 48.740.351/0003-27
    **IE:** 9030546625
    **Endereço:** RUA JOAO BETTEGA, 3802 – CIDADE INDUSTRIAL
    **Cidade/UF:** CURITIBA/PR
    **Contato:** Central de Coletas (41) XXXXX-XXXX
    """,
    "Cruzeiro do Sul": """
    **Razão Social:** VIAÇÃO CRUZEIRO DO SUL LTDA
    **CNPJ (Oracle):** 03232675006195-PR-PARCEL-Padrao
    **IE:** (sem IE cadastrado)
    **Endereço:** AV. DEZ DE DEZEMBRO, 5680 – JARDIM PIZA
    **Cidade/UF:** LONDRINA/PR
    **Observação:** Necessário usar CNPJ completo no Oracle para localização.
    """,
    "FL Brasil (Solistica)": """
    **Razão Social:** FL BRASIL HOLDING, LOGÍSTICA
    **CNPJ:** 18.233.211/0028-50
    **IE:** 9076066008
    **Endereço:** RODOVIA BR-116, KM 22301 – TATUQUARA
    **Cidade/UF:** CURITIBA/PR
    """,
    "Local Express": """
    **Razão Social:** LOCAL EXPRESS TRANSPORTES E LOGÍSTICA
    **CNPJ:** 06.199.523/0001-95
    **IE:** 9030307558
    **Endereço:** RUA FORMOSA, 131 – PLANTA PORTAL DA SERRA
    **Cidade/UF:** PINHAIS/PR
    """,
    "Rodonaves": """
    **Razão Social:** RODONAVES TRANSPORTES E ENCOMENDAS LTDA
    **CNPJ:** 44.914.992/0017-03
    **IE:** 6013031914
    **Endereço:** RUA RIO GRANDE DO NORTE, 1200 – CENTRO
    **Cidade/UF:** LONDRINA/PR
    """
}

operacoes = {
    "Operação 163-1": """
    Correções sistêmicas (CNPJ, descontos incorretos, configurações no SGE).
    Usar para ajustes internos sem movimentação física.
    """,
    "Operação 067-3": """
    Correção de vendas realizadas fora da plataforma Loja na Escola
    (devolução simbólica + faturamento específico).
    E faturamento de materiais não enviados na devolução.""",
    "Operação 115-8": """
    Casos de trocas ou devoluções sem necessidade de movimentação financeira
    (fluxo rápido, sem geração de créditos complexos)."""
}
