# Documentação do Transformer Test Simulator V2

## Visão Geral

O Transformer Test Simulator V2 é uma versão aprimorada do simulador de testes de transformadores, com arquitetura modular, persistência centralizada de dados e propagação automática entre módulos. Esta versão mantém toda a lógica de cálculos dos callbacks originais, mas adiciona recursos importantes para garantir consistência, integridade e documentação dos dados.

## Principais Melhorias

1. **Arquitetura Modular**: 10 módulos principais com responsabilidades bem definidas
2. **Fonte Única da Verdade**: Dados centralizados no `transformer-inputs-store`
3. **Propagação Automática**: Atualizações em um módulo refletem em todos os outros
4. **Persistência de Dados**: Salvamento automático do estado da aplicação
5. **Geração de Relatórios**: Documentação completa dos inputs e outputs de cada módulo
6. **Validação do Sistema**: Utilitários para validar o funcionamento geral

## Estrutura de Diretórios

```
transformer_test_simulator_v2/
├── app_core/
│   ├── transformer_mcp_enhanced.py    # MCP aprimorado com persistência e propagação
│   └── ...
├── utils/
│   ├── mcp_persistence_enhanced.py    # Utilitários aprimorados de persistência
│   ├── data_integrity.py              # Utilitários para garantir integridade dos dados
│   ├── callback_adapter.py            # Adaptadores para manter lógica dos callbacks
│   ├── report_generator.py            # Gerador de relatórios
│   ├── system_validator.py            # Validador do sistema
│   └── ...
├── reports/                           # Diretório para relatórios gerados
├── test_data/                         # Diretório para dados de teste
└── ...
```

## Módulos Principais

### 1. Transformer Inputs (Dados Básicos)
- Fonte única da verdade para todos os dados básicos do transformador
- Armazenamento: `transformer-inputs-store`

### 2. Losses (Perdas)
- Cálculo de perdas em vazio e em carga
- Armazenamento: `losses-store`

### 3. Impulse (Impulso)
- Simulação de ensaios de impulso
- Armazenamento: `impulse-store`

### 4. Dieletric Analysis (Análise Dielétrica)
- Verificação de espaçamentos mínimos e níveis de isolamento
- Armazenamento: `dieletric-analysis-store`

### 5. Applied Voltage (Tensão Aplicada)
- Cálculo de parâmetros para ensaios de tensão aplicada
- Armazenamento: `applied-voltage-store`

### 6. Induced Voltage (Tensão Induzida)
- Simulação de ensaios de tensão induzida
- Armazenamento: `induced-voltage-store`

### 7. Short Circuit (Curto-Circuito)
- Análise de correntes de curto-circuito
- Armazenamento: `short-circuit-store`

### 8. Temperature Rise (Elevação de Temperatura)
- Cálculo de elevação de temperatura
- Armazenamento: `temperature-rise-store`

### 9. Standards Consultation (Consulta de Normas)
- Acesso a requisitos de normas técnicas
- Armazenamento: Banco de dados de normas

### 10. Comprehensive Analysis (Análise Abrangente)
- Integração de dados de todos os módulos
- Armazenamento: `comprehensive-analysis-store`

## Fluxo de Dados

1. Os dados básicos são inseridos no módulo Transformer Inputs
2. O MCP armazena os dados no `transformer-inputs-store`
3. Os dados são propagados automaticamente para os demais módulos
4. Cada módulo realiza seus cálculos específicos
5. Os resultados são armazenados nos respectivos stores
6. Os dados são persistidos automaticamente no disco
7. Relatórios podem ser gerados a qualquer momento

## Geração de Relatórios

O sistema permite gerar relatórios em três formatos:

1. **HTML**: Relatório completo com formatação rica
2. **PDF**: Relatório formatado para impressão
3. **Excel**: Dados tabulares para análise

Os relatórios incluem:
- Dados básicos do transformador
- Resultados de cálculos de cada módulo
- Gráficos e visualizações (quando aplicável)
- Verificação de conformidade com normas técnicas

## Validação do Sistema

O sistema inclui utilitários para validar:

1. **Persistência**: Salvamento e carregamento de dados
2. **Propagação**: Atualização automática entre módulos
3. **Integridade**: Consistência dos dados entre módulos
4. **Relatórios**: Geração de relatórios em diferentes formatos

## Como Usar

### Inicialização

```python
from app_core.transformer_mcp_enhanced import TransformerMCPEnhanced

# Inicializar o MCP aprimorado
app.mcp = TransformerMCPEnhanced(load_from_disk=True)
```

### Atualização de Dados

```python
# Atualizar dados com propagação automática
app.mcp.set_data("transformer-inputs-store", data, auto_propagate=True, app_instance=app)
```

### Geração de Relatórios

```python
from utils.report_generator import TransformerReportGenerator

# Criar gerador de relatórios
report_generator = TransformerReportGenerator(app)

# Gerar relatório HTML
html_path = report_generator.generate_html_report()

# Gerar relatório PDF
pdf_path = report_generator.generate_pdf_report()

# Gerar relatório Excel
excel_path = report_generator.generate_excel_report()
```

### Validação do Sistema

```python
from utils.system_validator import SystemValidator

# Criar validador do sistema
validator = SystemValidator(app)

# Validar todos os aspectos do sistema
results = validator.validate_all()

# Salvar resultados da validação
results_path = validator.save_validation_results()
```

## Conclusão

O Transformer Test Simulator V2 mantém toda a lógica de cálculos do sistema original, mas adiciona recursos importantes para garantir consistência, integridade e documentação dos dados. A arquitetura modular e a propagação automática de dados facilitam a manutenção e extensão do sistema, enquanto a geração de relatórios permite documentar os resultados de forma completa e detalhada.
