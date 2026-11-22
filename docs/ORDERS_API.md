# Fase 3 — API de pedidos

Implementação em `orders/` (models, serializers, views, services, tests), preservando `core.User`, auth JWT e `catalog`.

## Leitura pública
- `GET /api/schedule/` — janelas comerciais cadastradas; não revela endereços de clientes.

## Cliente autenticado (Bearer access)
- `GET/POST /api/addresses/`; `GET/PATCH/DELETE /api/addresses/{id}/` — exclusivamente do proprietário.
- `POST /api/orders/quote/` — cotação e disponibilidade **calculadas no servidor**, retorna preços, frete e `quote_hash`.
- `POST /api/orders/` — cria pedido a partir da mesma seleção, com `idempotency_key` UUID e `quote_hash`, retorna 201; replay idêntico retorna 200 sem segundo pedido.
- `GET /api/orders/` — somente próprios.
- `GET /api/orders/{public_id}/` — somente proprietário; recursos de terceiros retornam 404.
- `POST /api/orders/{public_id}/cancel-request/` — cancela o próprio pedido se ainda estiver em `aguardando_confirmacao`, registrando histórico; outros estados exigem atendimento.

### Exemplo de cotação (IDs ilustrativos, não são produtos reais)
```json
{
  "items": [{"product_id": 1, "quantity": 2, "selected_option_ids": [1]}],
  "fulfillment_type": "pickup",
  "scheduled_at": "2026-12-04T14:00:00-03:00",
  "notes": "Separar embalagens"
}
```
Confirmar usando **o mesmo corpo**, mais `idempotency_key` UUID e `quote_hash` retornado pela cotação. Enviar `total` ou `price` não substitui cálculo feito pelo backend.

## Administração (is_superuser ativo)
- `GET /api/admin/orders/` e `GET /api/admin/orders/{id}/`.
- `POST /api/admin/orders/{id}/transitions/`: `{"status":"confirmado","reason":"..."}`; sequência permitida, salva ator, hora e motivo.
- `POST /api/admin/orders/{id}/confirm-payment/`: `{"reason":"Comprovante conferido"}`; confirmação manual explícita. Nenhum pagamento é realizado pela API.
- `/api/admin/business-hours/`, `/api/admin/blocked-dates/`, `/api/admin/delivery-zones/`: CRUD para agenda e entrega.

Estados: `aguardando_confirmacao` → `confirmado` ou `rejeitado`/ `cancelado`; `confirmado` → `em_preparo`/ `cancelado`; `em_preparo` → `pronto`; `pronto` → `concluido`. Pagamento é separado: `pendente`/ `pago`.

## Regras
- Sem janela real cadastrada, recusar pedidos; entrega exige janela habilitada, endereço próprio e CEP coberto por zona ativa.
- Frete definido pela zona cadastrada e nunca pelo frontend. Sem zona ativa, entrega indisponível.
- Pedido tem subtotal, frete e total calculados por Decimal em transação atômica, snapshots de nome, preço, opções e endereço, UUID público e índice único para `(user, idempotency_key)`.
- Histórico não pode ser editado pelo cliente. O Django Admin não permite edição de preços históricos.
- Revalida disponibilidade de produto, opções, quantidade mínima e antecedência ao confirmar. Alterações invalidam a cotação.
- Sem gateway ou PIX fictício; estado inicial do pagamento é `pendente`.

## Validar
```bash
pdm install
pdm run python manage.py makemigrations --check --dry-run
pdm run migrate
pdm run check
pdm run lint
pdm run test
pdm run dev
```

Em outro terminal:
```bash
npm install
npm run lint
npm test
npm run build
npm run dev
```

Antes de integrar `main`: testar em PostgreSQL real concorrência/retries, cookies e CORS HTTPS, usar horários/CEP/preços reais aprovados pela proprietária, políticas comerciais/cancelamento e testes E2E cliente→admin.
