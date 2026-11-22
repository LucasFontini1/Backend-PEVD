# Fase 1 — relatório de validação

O backend deriva do template original, mantendo `core.User`, migrations, DRF, PDM e uploader.

**Implementado em branch FEAT-2 (pendente de CI):** sessão JWT com refresh em cookie, blacklist, logout, cadastro com aceite explícito e endpoint superuser. Proteção de leitura de usuários e associação de foto agora utiliza superuser, não staff.

**Pendências bloqueantes:** verificação de e-mail, recuperação de senha, registro versionado do aceite legal, rate-limit robusto em cache compartilhado, testes Django reais em Python 3.14, schema OpenAPI validado, testes de CSRF em deploy HTTPS/cookies entre domínios.

**Política de branches:** PR para `dev`; jamais integrar `main` sem testes e revisão.
