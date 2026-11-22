# Contrato de API — Fase 1

- `POST /api/registro/`: email, username, name opcional, password, accepted_terms=true. Retorna 201. **Aceite ainda não versionado; publicação bloqueada até revisão legal.**
- `POST /api/token/`: login (email ou username) e password. Retorna `{ "access": "..." }`; define cookies `pv_refresh` HttpOnly e `pv_csrf`.
- `POST /api/token/refresh/`: usa cookie `pv_refresh` e header `X-CSRFToken`; rotaciona e revoga refresh; retorna access.
- `POST /api/token/logout/`: header CSRF e cookie refresh; invalida sessão, retorna 204.
- `GET /api/usuarios/me/`: requer Bearer access; perfil somente do usuário.
- `GET /api/admin/access/`: 401 anônimo, 403 usuário comum/staff, 200 superuser ativo.
- `POST /api/media/images/`: endpoint do uploader original, com permissões do modelo.
- `GET /api/schema/`, `GET /api/doc/`: OpenAPI e Swagger.

Pendências: verificação de e-mail, recuperação de senha, rate limit em cache compartilhado, prova em staging HTTPS e consentimento versionado.
