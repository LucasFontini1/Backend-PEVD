# Pedidos de WhatsApp e relatório (admin)

**Autorização:** apenas superusuário ativo. A rota não usa valores de preço, frete, status ou pagamento fornecidos pelo navegador.

- `POST /api/admin/orders/manual/` recebe `customer_name`, `customer_phone`, `customer_email` opcional (vincula conta **existente**, nunca cria conta com senha), `items: [{product_id,quantity,selected_option_ids}]`, `fulfillment_type` (pickup/delivery), `scheduled_at` ISO 8601, `notes`, `idempotency_key` UUID. Para delivery, `address` com CEP, rua, número, bairro, cidade e UF.
- Preços vêm do catálogo ativo, adicionais de opções passam pelas validações de grupo; agenda, antecedência e zona/valor mínimo de entrega são revalidados no servidor.
- Pedido nasce como `aguardando_confirmacao`, pagamento `pendente`, origem `whatsapp`, com snapshots e histórico. Marcar pago requer a rota separada já existente.
- Cliente sem conta fica com `user=null`; **não** se inventa e-mail nem se cria conta sem consentimento.
- Cliente existente pode ser associado por e-mail, mas **não há envio de SMS/WhatsApp**: o operador é responsável por confirmar dados com o cliente.
- Repetições com a mesma chave UUID retornam 200 se idênticas; outra carga gera 400.

## Relatório
- `GET /api/admin/orders/completed-report/?start=AAAA-MM-DD&end=AAAA-MM-DD` somente status `concluido`, filtrado pela **data de conclusão** registrada no histórico do pedido (fallback para criação se um registro antigo não tiver histórico de conclusão); pedidos cancelados e apenas confirmados não entram. O resumo separa total pago e pendente; valores são declarações do sistema, não comprovantes bancários.
- `GET /api/admin/orders/completed-report/?download=csv` retorna CSV separado por ponto e vírgula, com BOM UTF-8 para Excel.

Antes de produção: revisar dados pessoais guardados, fluxos de reembolso/cancelamento e conciliação real. Dados WhatsApp são inseridos pela administração e nunca importados automaticamente.
