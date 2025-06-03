# Padrão de Persistência MCP

Objetivo

Garantir que todos os layouts e callbacks da aplicação usem funções utilitárias para ler e gravar dados do MCP (Master Control Program), evitando repetição de código e conflitos de persistência.

Não usar persistence=True nos componentes Dash
Nunca utilize os atributos persistence ou persistence_type nos inputs, dropdowns ou outros componentes Dash.
A persistência deve ser feita exclusivamente via backend/MCP.

Leitura de dados (ao montar o layout ou carregar a página)
Sempre que for necessário preencher valores iniciais de inputs, leia os dados do MCP usando:

Exemplo para obter dados do store de inputs do transformador

```python
transformer_data = app.mcp.get_data('transformer-inputs-store') or {}
valor = transformer_data.get('campo_desejado', valor_padrao)
```

Use esses valores para definir o valor inicial dos componentes Dash.

Gravação de dados (ao salvar alterações do usuário)
Sempre que um input for alterado, salve os dados no MCP usando a função utilitária patch_mcp:

```python
from utils.mcp_utils import patch_mcp
```

Exemplo em um callback

```python
@callback(...)
def atualizar_dados(...):
    ...
    patch_mcp('transformer-inputs-store', {'campo_desejado': novo_valor}, app=app)
    ...
```

O patch_mcp faz merge apenas dos campos não vazios e evita sobrescrever dados válidos.

Nunca gravar diretamente no disco ou usar cache local
Não use arquivos temporários, variáveis globais ou cache local do navegador para persistência de dados de entrada.
Toda a leitura e gravação deve ser feita via MCP.

Funções utilitárias recomendadas

- `app.mcp.get_data(store_id)` — para ler dados de um store.
- `patch_mcp(store_id, data, app)` — para gravar/atualizar dados de um store.

Exemplo de uso em layout
No início do layout:

```python
transformer_data = app.mcp.get_data('transformer-inputs-store') or {}
```

No input:

```python
dbc.Input(id='campo', value=transformer_data.get('campo', valor_padrao))
```

Exemplo de uso em callback

```python
from utils.mcp_utils import patch_mcp

@callback(...)
def salvar_dados(novo_valor, ...):
    patch_mcp('transformer-inputs-store', {'campo': novo_valor}, app=app)
    ...
```

-Always use ShadCN / Tailwind CSS where applicable
-Always keep the design minimal but good looking
-Maintain a tasks.md file for high level tasks that need step by step implementation
Use Context7 MCP Tool to always gather latest documentation / knowledge about a library
Use Firecrawl MCP Tool to search / scrape web pages whenever necessary
Never create code, files, folders, commits or any artifact without explicit authorization
Always read and understand the entire codebase and its dependencies before making changes
All code must follow modular structure and naming conventions defined by the project
Never assume functionality — always trace the actual logic in code before acting
If code references external libs, read their docs or source before using
Output must be deterministic and reproducible — no guesswork allowed
Use localStorage, not cookies, for offline data persistence unless specified
Always validate all params and data flow through modules before proceeding
Respect the logic flow and UI structure already defined — no override unless authorized
