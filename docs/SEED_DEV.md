# Dump de desenvolvimento — administrador local

> Apenas para ambiente **descartável** e `DEBUG=True`. Nunca usar o seed em produção.

Foi adicionado `fixtures/dev_superuser.json` com um registro `core.User` contendo:
- email: `a@a.com`
- username: `admin.dev`
- `is_superuser=True`, `is_staff=True`, `is_active=True`
- senha **inutilizável** (`password="!"`) no arquivo versionado

A senha real **não está armazenada no Git nem no dump**. O dump/fixture é um arquivo estático de desenvolvimento, não contém produtos/preços fictícios nem dados reais de clientes.

## Como configurar a senha localmente

Após configurar o backend e o banco local:

```bash
pdm install
pdm run migrate
# Opcional: importar o dump, somente em banco vazio/descartável:
pdm run python manage.py loaddata fixtures/dev_superuser.json
# Informe a senha solicitada no ambiente local (não salve no Git):
export DEV_SEED_ADMIN_PASSWORD='<senha-local>'
pdm run python manage.py seed_dev --confirm-local
unset DEV_SEED_ADMIN_PASSWORD
```

No PowerShell:

```powershell
$env:DEV_SEED_ADMIN_PASSWORD = '<senha-local>'
pdm run python manage.py seed_dev --confirm-local
Remove-Item Env:DEV_SEED_ADMIN_PASSWORD
```

O comando também pode ser executado **sem** `loaddata`: nesse caso cria o usuário diretamente. Se a conta já existir, redefine sua senha e garante as permissões; rodar duas vezes não duplica.

**Atenção:** o fixture usa a chave primária `900001`. Faça `loaddata` exclusivamente em banco de teste vazio. Em banco existente, use somente o comando. Não compartilhe dumps de produção nem execute seed de administrador fora do ambiente local.

### Validação

```bash
pdm run python manage.py test core.tests.test_seed_dev
pdm run python manage.py check
```

O login usa `POST /api/token/` com `{"login":"a@a.com","password":"<senha-local>"}`. Nunca publique tokens ou senhas reais em issues/PRs.
