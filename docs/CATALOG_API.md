# API catálogo — Fase 2

## Leitura pública
- `GET /api/categories/` — categorias ativas, paginadas
- `GET /api/categories/{slug}/`
- `GET /api/products/` — produtos ativos em categorias ativas; `search`, `category` (slug), `available=true`, `featured=true`, `min_price`, `max_price`, `ordering`, `page`
- `GET /api/products/{slug}/` — descrição, preços decimais, fotos/alt, alergênicos, ingredientes, conservação, opções

## Administração — JWT Bearer, conta ativa e superuser
- `/api/admin/categories/` e `/api/admin/products/` — GET, POST, PATCH/PUT, DELETE (desativa)
- `/api/admin/product-images/` — associar mídia do uploader pelo campo `image_attachment_key`; GET/POST/PATCH/DELETE
- `/api/admin/option-groups/` e `/api/admin/options/` — GET/POST/PATCH/DELETE
- Upload preservado do template: `POST /api/media/images/` com `file` e Bearer; retorna `attachment_key`.

O uploader valida imagens e associa proprietário; a associação ao catálogo exige mídia enviada pela mesma conta superuser. Categorias/produtos em uso nunca são excluídos fisicamente via DELETE (is_active=false).
Não existem produtos de demonstração, entrega, carrinho ou pedidos na Fase 2.
