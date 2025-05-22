# Arquitetura do Simulador de Teste de Transformadores

## Visão Geral

O Transformer Test Simulator é uma aplicação modular para simulação e análise de diferentes aspectos de transformadores de potência. A arquitetura foi projetada para garantir:

1. **Modularidade**: 10 módulos principais com responsabilidades bem definidas
2. **Fonte Única da Verdade**: Dados centralizados no `transformer-inputs-store`
3. **Propagação Automática**: Atualizações em um módulo refletem em todos os outros
4. **Persistência de Dados**: Salvamento automático do estado da aplicação
5. **Geração de Relatórios**: Documentação completa dos inputs e outputs de cada módulo

## Estrutura Modular

### 1. Transformer Inputs (Dados Básicos)
- **Função**: Fonte única da verdade para todos os dados básicos do transformador
- **Armazenamento**: `transformer-inputs-store`
- **Responsabilidades**:
  - Coleta de informações fundamentais (potência, tensões, conexões)
  - Cálculo de correntes nominais
  - Propagação de dados para outros módulos

### 2. Losses (Perdas)
- **Função**: Cálculo de perdas em vazio e em carga
- **Armazenamento**: `losses-store`
- **Responsabilidades**:
  - Cálculo de perdas no ferro (em vazio)
  - Cálculo de perdas no cobre (em carga)
  - Cálculo de corrente de excitação
  - Cálculo de potência magnética
  - Cálculo de tensão de curto-circuito
  - Análise de eficiência em diferentes condições de carga

### 3. Impulse (Impulso)
- **Função**: Simulação de ensaios de impulso
- **Armazenamento**: `impulse-store`
- **Responsabilidades**:
  - Simulação de ensaios de impulso atmosférico (LI)
  - Simulação de ensaios de impulso de manobra (SI)
  - Simulação de ensaios de impulso cortado (LIC)
  - Cálculo de parâmetros RLC equivalentes
  - Análise de eficiência do circuito
  - Cálculo de requisitos de energia para o ensaio

### 4. Dieletric Analysis (Análise Dielétrica)
- **Função**: Verificação de espaçamentos mínimos e níveis de isolamento
- **Armazenamento**: `dieletric-analysis-store`
- **Responsabilidades**:
  - Verificação de espaçamentos mínimos conforme normas técnicas
  - Análise da rigidez dielétrica dos materiais isolantes
  - Aplicação de correções para altitude
  - Verificação de conformidade com normas técnicas

### 5. Applied Voltage (Tensão Aplicada)
- **Função**: Cálculo de parâmetros para ensaios de tensão aplicada
- **Armazenamento**: `applied-voltage-store`
- **Responsabilidades**:
  - Cálculo de impedância capacitiva
  - Cálculo de corrente necessária para o ensaio
  - Cálculo de potência reativa necessária
  - Análise de viabilidade com sistema ressonante

### 6. Induced Voltage (Tensão Induzida)
- **Função**: Simulação de ensaios de tensão induzida
- **Armazenamento**: `induced-voltage-store`
- **Responsabilidades**:
  - Cálculo de frequência ótima
  - Cálculo de carga capacitiva
  - Cálculo de potência reativa necessária
  - Análise de viabilidade do ensaio

### 7. Short Circuit (Curto-Circuito)
- **Função**: Análise de correntes de curto-circuito
- **Armazenamento**: `short-circuit-store`
- **Responsabilidades**:
  - Cálculo de correntes de curto-circuito
  - Análise de suportabilidade mecânica
  - Cálculo de variação de impedância
  - Visualização gráfica dos resultados

### 8. Temperature Rise (Elevação de Temperatura)
- **Função**: Cálculo de elevação de temperatura
- **Armazenamento**: `temperature-rise-store`
- **Responsabilidades**:
  - Cálculo de constantes térmicas
  - Cálculo de elevação de temperatura do óleo
  - Cálculo de elevação de temperatura dos enrolamentos
  - Verificação de conformidade com limites normativos

### 9. Standards Consultation (Consulta de Normas)
- **Função**: Acesso a requisitos de normas técnicas
- **Armazenamento**: Banco de dados de normas
- **Responsabilidades**:
  - Consulta de requisitos de normas técnicas (NBR, IEC, IEEE)
  - Acesso a valores padronizados para níveis de isolamento
  - Verificação de conformidade com normas

### 10. Comprehensive Analysis (Análise Abrangente)
- **Função**: Integração de dados de todos os módulos
- **Armazenamento**: `comprehensive-analysis-store`
- **Responsabilidades**:
  - Integração de dados de todos os módulos
  - Verificação de conformidade geral
  - Geração de relatórios detalhados

## Fluxo de Dados

### Fonte Única da Verdade
- O módulo Transformer Inputs é a fonte única da verdade para todos os dados básicos
- Todos os dados são armazenados no `transformer-inputs-store`
- Campos básicos como potência, tensões, conexões, etc. são mantidos apenas no `transformer-inputs-store`
- Outros módulos referenciam esses dados em vez de duplicá-los

### Propagação Automática
- Quando os dados básicos são alterados no Transformer Inputs, as alterações são propagadas para todos os outros módulos
- A propagação é feita através do mecanismo de persistência do MCP (Master Control Program)
- Cada módulo recebe apenas os dados relevantes para suas funcionalidades
- A propagação garante consistência entre todos os módulos

### Persistência de Dados
- Todos os dados são persistidos automaticamente no disco
- O estado da aplicação pode ser recuperado após reinicialização
- Sessões de teste podem ser salvas e carregadas
- Backups automáticos são criados para evitar perda de dados

## Geração de Relatórios

O sistema permite a geração de relatórios completos com:
- Inputs e outputs de cada módulo
- Resultados de cálculos e simulações
- Verificação de conformidade com normas técnicas
- Gráficos e visualizações
- Recomendações e observações

## Implementação Técnica

### Master Control Program (MCP)
- Gerencia o estado global da aplicação
- Controla a persistência de dados
- Coordena a propagação de dados entre módulos
- Garante consistência e integridade dos dados

### Stores
- Cada módulo possui seu próprio store para armazenamento de dados específicos
- Os stores são atualizados automaticamente quando os dados básicos são alterados
- Os stores mantêm apenas os dados específicos do módulo, referenciando os dados básicos do `transformer-inputs-store`

### Callbacks
- A lógica de cálculos é implementada em callbacks
- Cada módulo possui seus próprios callbacks
- Os callbacks são acionados quando os dados relevantes são alterados
- A lógica dos cálculos é mantida intacta durante a refatoração

### Utilitários
- Funções auxiliares para cálculos específicos
- Utilitários para persistência e propagação de dados
- Ferramentas para geração de relatórios
- Funções para validação de dados

## Conclusão

A arquitetura modular do Transformer Test Simulator garante:
- Separação clara de responsabilidades
- Consistência de dados entre módulos
- Facilidade de manutenção e extensão
- Geração de relatórios completos
- Persistência e recuperação de dados
