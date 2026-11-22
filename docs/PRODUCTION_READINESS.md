# Checklist de prontidão profissional — Pensei em Você Doces

Revisão técnica baseada no código em 22/11/2026. **Não equivale a pentest, auditoria legal ou teste de produção.**

## Alterações desta entrega
- A rota do Django Admin é configurada por `DJANGO_ADMIN_PATH`, por exemplo `painel-interno-privado` sem barras. Em produção, se ausente, o Django Admin fica **desabilitado**; o painel Vue `/admin` e a API `/api/admin/` não mudam. O caminho não substitui autenticação/permissões.
- O nome de quem fez o pedido é retornado como `customer_display_name` **somente** no serializador administrativo. Priorizam-se nome do pedido, nome da conta e username.
- `Order.objects.select_related('user')` evita buscas repetitivas.

## Variáveis indispensáveis para produção
`DEBUG=False`, `SECRET_KEY` forte, `ALLOWED_HOSTS` com domínio da API, `FRONTEND_URLS` com URLs HTTPS das origens confiáveis, `DATABASE_URL`, `DATABASE_URL_MIGRATIONS`, `CLOUDINARY_URL`, `SECURE_SSL_REDIRECT=True`.
`DJANGO_ADMIN_PATH` é **Config** (não segredo criptográfico); escolha um caminho não óbvio, mas não dependa dele como defesa.
Se `DJANGO_ADMIN_PATH` não estiver preenchido, o acesso ao Django Admin fica indisponível em produção, sem prejudicar a API nem o painel Vue.

## Pendências para liberar vendas reais
1. Formalizar Termos de Uso e Política de Privacidade com responsável legal, identificação fiscal e comercial, endereço e canal para pedidos LGPD. A versão na interface é um **rascunho explicitamente sinalizado**.
2. Definir regras de taxa e elegibilidade para entregas fora de zonas cadastradas: atualmente a ausência de zona resulta em frete **R$ 0,00**.
3. Validar autenticação (inclusive cookies cross-site, CSRF e refresh) em celular, Chrome e Safari nos domínios reais.
4. Testar ciclo completo de pedidos, estoque/disponibilidade, mudanças de status, pagamentos externos e envio de mídia Cloudinary com registros reais.
5. Inspecionar tabelas, cópias de segurança e recuperação de banco Supabase, migrações Vercel e política de retenção/exclusão de dados.
6. Testar mobile 320/375/390/768px, desktop, navegação por teclado, leitores de tela e contraste; automatizar testes E2E.
7. Definir termos de retirada/entrega, cancelamento, reembolso e informações de alimentos/alergênicos; revisar fluxo de confirmação com a responsável.
8. Verificar rate limiting de autenticação, monitoramento de erros, logs sem dados pessoais, proteção de chaves, atualização de dependências e backups.
9. Publicar a identificação comercial exigida pelo Decreto 7.962/2013. Não presumir que o município basta.

### Conclusão
**Ainda não certificado como pronto para uso profissional.** Os testes automatizados cobrem apenas uma parcela do sistema; é necessária homologação operacional e jurídica, além de testes no deployment real.
