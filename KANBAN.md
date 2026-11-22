# Kanban — Pensei em Você Doces (Backend)

A conexão GitHub disponível gerencia issues e PRs, mas não cria um GitHub Project nativo; este arquivo acompanha o quadro.

## Concluído em dev — Fase 4
- [#18](https://github.com/LucasFontini1/Backend-PEVD/issues/18): FAQ pública e CRUD superuser.
- [#19](https://github.com/LucasFontini1/Backend-PEVD/issues/19): contato antispam básico, tickets privados, respostas, histórico e IDOR.
- [#20](https://github.com/LucasFontini1/Backend-PEVD/issues/20): orçamentos com proposta e aceite, sem criar pedido automaticamente.
- [#21](https://github.com/LucasFontini1/Backend-PEVD/issues/21): dashboard real, loja configurável, banners e auditoria.
- [PR #22](https://github.com/LucasFontini1/Backend-PEVD/pull/22): integrado na dev com CI Python 3.14 Ubuntu/Windows.

## Refatoração e gestão comercial — integrado em dev (22/11/2026)
- [#27](https://github.com/LucasFontini1/Backend-PEVD/issues/27): pedidos manuais WhatsApp para clientes sem conta; campos de contato sem senhas fictícias, itens e totais recalculados no servidor, opção de entrega/retirada, histórico, pagamento pendente, idempotência.
- [#28](https://github.com/LucasFontini1/Backend-PEVD/issues/28): relatório de pedidos concluídos por data de conclusão com receitas declaradas pagas/pendentes e CSV.
- Catálogo administrativo ganhou filtro server-side por nome; preços do navegador não são aceitos.
- [PR #29](https://github.com/LucasFontini1/Backend-PEVD/pull/29): squash merge em dev. CI Python 3.14 Ubuntu/Windows, 92 testes aprovados.
- [docs/MANUAL_ORDERS.md](docs/MANUAL_ORDERS.md): contrato e restrições.

## Em homologação / backlog
- [#23](https://github.com/LucasFontini1/Backend-PEVD/issues/23): antispam distribuído, email real opcional, retenção/privacidade.
- [#24](https://github.com/LucasFontini1/Backend-PEVD/issues/24): converter orçamento aceito em pedido apenas após confirmar valor/horário/entrega.
- [#17](https://github.com/LucasFontini1/Backend-PEVD/issues/17): validação Fase 3 em PostgreSQL e HTTPS.
- [#2](https://github.com/LucasFontini1/Backend-PEVD/issues/2), [#3](https://github.com/LucasFontini1/Backend-PEVD/issues/3), [#5](https://github.com/LucasFontini1/Backend-PEVD/issues/5): pendências de segurança/autenticação da Fase 1.

## Próxima fase
- Fase 5: PWA com cache público seguro, SEO, páginas legais revisadas, deploy e auditoria completa.

**main bloqueada até homologação.** Não assumir receita conciliada, prazo de resposta, email ou dados comerciais não configurados.
