# API de atendimento, FAQ e gestão comercial — Fase 4

## Pública (sem conta)
- `GET /api/faqs/` e `GET /api/faqs/{id}/` — somente perguntas publicadas; não há respostas inventadas. A proprietária deve cadastrar pelo menos cinco FAQs reais antes do lançamento.
- `POST /api/contact/` — nome, email, assunto, mensagem, consent=true, website="" (campo honeypot). Resposta 202 genérica; registro no painel. **Não envia email**. Limite DRF: 5/hora por identidade identificada pelo DRF. Em produção exigir gateway/cache distribuído e proteção na borda.
- `GET /api/banners/` — somente banners ativos.
- `GET /api/shop/settings/` — branding e dados comerciais públicos explicitamente configurados (telefone, email, Instagram, retirada, anúncio, prazo de resposta opcional).

## Cliente autenticado
- `GET/POST /api/support/tickets/` — assunto, mensagem, `order_public_id` UUID opcional. O pedido deve pertencer ao solicitante.
- `GET /api/support/tickets/{id}/` — apenas dono; 404 para outros usuários.
- `POST /api/support/tickets/{id}/messages/` — `{"message":"texto"}`, apenas dono, bloqueado se encerrado.
- `GET/POST /api/quotes/` — título, descrição, sabor, porções e data desejada, sem preço no POST do cliente.
- `GET /api/quotes/{id}/` — apenas dono.
- `POST /api/quotes/{id}/accept/` e `/decline/` — aceite/recusa apenas do dono. Aceite exige proposta válida e não cria pedido; o fluxo comercial posterior precisa de confirmação separada.

## Comercial (superuser ativo)
- `/api/admin/faqs/` — CRUD, DELETE despublica.
- `GET /api/admin/contact/`, `POST /api/admin/contact/{id}/mark-handled/`.
- `GET /api/admin/support/tickets/`, `GET /api/admin/support/tickets/{id}/`, `POST /api/admin/support/tickets/{id}/reply/` com `message` e `close` opcional, `POST /api/admin/support/tickets/{id}/close/`.
- `GET /api/admin/quotes/`, `POST /api/admin/quotes/{id}/propose/` com preço Decimal, detalhes e `valid_until` futuro.
- `/api/admin/banners/` — CRUD protegido, imagem por `image_attachment_key` do uploader e link apenas interno, DELETE despublica.
- `GET/PATCH /api/admin/shop-settings/` — dados comerciais configuráveis; alterações auditadas.
- `GET /api/admin/dashboard/?start=AAAA-MM-DD&end=AAAA-MM-DD` — pedidos no período, valor de pedidos marcados pagos e não cancelados/rejeitados, contatos, tickets abertos, orçamentos pendentes e top produtos por quantidade. **Não equivale a conciliação bancária**.

## Garantias
- `is_staff` sem `is_superuser` recebe 403 em todas as rotas administrativas.
- Tickets e propostas privados com escopo filtrado por `request.user`; mensagens com sender autenticado, não enviado pelo cliente.
- Respostas administrativas e eventos comerciais ficam auditados sem copiar mensagens/PII para o registro.
- Prazo de resposta só aparece se alguém o configurar; cinco FAQs exigem conteúdo verdadeiro.
- Não gerar token de PIX, pagamento nem dados de avaliação/receita fictícios.

## Testes
```bash
pdm install
pdm run python manage.py makemigrations --check --dry-run
pdm run check
pdm run lint
pdm run test
```
Para deploy, verificar migração e restauração de banco, integração real das duas aplicações, HTTPS/cookies/CORS, rate limiting distribuído, política de retenção LGPD e aviso legal antes de ativar produção.
