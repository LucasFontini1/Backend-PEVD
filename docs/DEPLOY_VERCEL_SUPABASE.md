# Deploy de produção — Pensei em Você Doces

## 1. Supabase (PostgreSQL)
Crie um projeto em https://supabase.com/dashboard e abra **Connect**.
- **DATABASE_URL**: URL do *Transaction Pooler*, porta 6543, com `?sslmode=require`.
- **DATABASE_URL_MIGRATIONS**: URL do *Session Pooler*, porta 5432, com `?sslmode=require`.
- Substitua o campo de senha pela senha de banco definida na criação do projeto.
- Se a senha contiver caracteres reservados de URL, faça percent-encoding.
- Não use URLs fictícias nem exponha essas strings no frontend.

## 2. Vercel — Backend
Importe **LucasFontini1/Backend-PEVD**, defina `main` como Production Branch.
O Django é reconhecido pelo `manage.py` e dependências em `pyproject.toml`.
Cadastre em **Settings → Environment Variables**:
- `SECRET_KEY` — gere por `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- `DEBUG=False`
- `ALLOWED_HOSTS=seu-backend.vercel.app` (sem protocolo)
- `FRONTEND_URLS=https://seu-frontend.vercel.app`
- `DATABASE_URL=<transaction-pooler>`
- `DATABASE_URL_MIGRATIONS=<session-pooler>`
- `CLOUDINARY_URL=<sua-url-cloudinary>` — obtenha no painel Cloudinary; necessária para uploads persistentes em serverless
- `SECURE_SSL_REDIRECT=True` — opcional, após conferir o proxy de HTTPS.

`[tool.vercel.scripts].build` executa as migrações automaticamente apenas em Production, recusando build sem `DATABASE_URL_MIGRATIONS`. **Não configure outro Build Command no dashboard ou vercel.json**, pois ele prevalece sobre o pyproject.
O frontend necessita `VITE_API_BASE_URL=https://seu-backend.vercel.app/api/` (incluindo `/api/`).

## 3. Vercel — Frontend
Importe **LucasFontini1/Frontend-PEVD**, com framework Vite, Build `npm run build` e Output `dist`.
Defina `VITE_API_BASE_URL` conforme acima, em **Settings → Environment Variables**.
Arquivo `vercel.json` já possui fallback para Vue Router.
Ao alterar qualquer `VITE_*`, gere novo deployment.

## Segurança
- `VITE_*` é público no navegador; nunca inserir senhas ou segredos.
- Para login entre domínios, backend usa cookies Secure/SameSite=None em produção e endpoint de bootstrap `GET /api/token/csrf/`. Cookies de terceiros podem sofrer bloqueio pelos navegadores; domínios personalizados no mesmo site ou proxy de API são preferíveis.
- Não reutilize `DATABASE_URL_MIGRATIONS` em previews ligados ao banco de produção.
- Rotas administrativas exigem `is_superuser` no backend.
- Crie conta administradora com `python manage.py createsuperuser` contra o banco correto, em ambiente controlado; não adicione credenciais ao Git.
