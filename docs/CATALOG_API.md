# API REST — Catálogo da Fase 2

Todos os valores monetários são retornados como strings decimais. Produtos não publicados e produtos de categorias inativas não aparecem na API pública.

## Pública — sem login
- `GET /api/categories/` — categorias ativas com paginação (`results`, `page`, `total_pages`)
- `GET /api/categories/{slug}/` — categoria ativa
- `GET /api/products/?search=&category=&available=true&featured=true&min_price=&max_price=&ordering=&page=&page_size=`
- `GET /api/products/{slug}/` — preço, ingredientes, alergênicos, conservação, galeria, grupos de opções
- `GET /api/shop/settings/` — nome, cores e logo (sem dados privados)

Ordenação permitida: `sort_order`, `name`, `-name`, `price`, `-price`. Preços `min_price` e `max_price` com Decimal. O parâmetro category recebe **slug**.

## Administração — superuser ativo autenticado
- `GET/POST /api/admin/categories/` e `GET/PATCH/PUT/DELETE /api/admin/categories/{id}/`
- `GET/POST /api/admin/products/` e `GET/PATCH/PUT/DELETE /api/admin/products/{id}/`
- `GET/POST/PATCH/DELETE /api/admin/product-images/` — galeria via `image_attachment_key`
- `GET/POST/PATCH/DELETE /api/admin/option-groups/` — opções vinculadas ao produto
- `GET/POST/PATCH/DELETE /api/admin/options/` — preço adicional Decimal
- `GET/PATCH /api/admin/shop-settings/` — logo e cores configuráveis

Os detalhes das APIs administrativas relacionadas acima usam `{id}/`, exceto as configurações da marca, que têm recurso único. `DELETE` de produto/categoria **desativa**, preservando referências. Demais entidades são removíveis, pois pedidos ainda não existem.

Upload: `POST /api/media/images/` do template Django, multipart `file`, Bearer JWT. Recebe-se `attachment_key`. Só é possível associar ao catálogo uma imagem enviada pela conta superuser ativa na requisição. A mídia continua obedecendo à validação original de MIME, tamanho e propriedade.

## Para testar
```sh
pdm install
pdm run python manage.py makemigrations --check --dry-run
pdm run migrate
pdm run check
pdm run lint
pdm run test
pdm run createsuperuser
pdm run dev
```

No painel Vue, acessar `/admin` com essa conta; criar categoria, criar produto, publicar, adicionar foto e opções; confirmar `/cardapio` como visitante.

**Ainda pendente:** validação da proprietária sobre cardápio, preços, fotos autorizadas e logo definitiva. Esta fase não cria pedidos/carrinho nem dados fictícios.
