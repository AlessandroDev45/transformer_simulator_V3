# components/formatters.py
"""
Funções para formatar dados para exibição na UI e, principalmente,
para a geração de relatórios PDF, convertendo dados dos Stores
em estruturas compatíveis com o pdf_generator.
"""
import logging
import math
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np

log = logging.getLogger(__name__)

# --- Formatador Genérico de Valor (para UI e PDF) ---


def format_parameter_value(
    param_value, precision: int = 2, unit: str = "", none_value: str = "N/A"
) -> str:
    """
    Formata um valor numérico (ou outros tipos) para exibição, tratando None, NaN, Inf.
    Retorna uma string formatada.

    Args:
        param_value: O valor a ser formatado.
        precision: Número de casas decimais para floats.
        unit: Unidade a ser anexada (com espaço).
        none_value: String a ser retornada se o valor for None, NaN ou Inf.

    Returns:
        String formatada.
    """
    if param_value is None:
        return none_value
    if isinstance(param_value, bool):
        return "Sim" if param_value else "Não"
    if isinstance(param_value, (int, float)):
        if math.isnan(param_value) or math.isinf(param_value):
            return none_value
        val = float(param_value)

        # Format with specific precision first
        try:
            formatted_num = f"{val:.{precision}f}"
            # Remove trailing zeros if needed (e.g., 1.20 -> 1.2, 1.00 -> 1)
            if precision > 0 and "." in formatted_num:
                formatted_num = formatted_num.rstrip("0").rstrip(".")
            return f"{formatted_num}  {unit}".strip() if unit else formatted_num
        except (ValueError, TypeError):
            # Fallback for potential issues with f-string formatting
            return str(param_value)

    # For other types (string, etc.), return as string
    return str(param_value).strip() if str(param_value).strip() else none_value


# --- Formatadores Específicos para Relatório PDF ---


def formatar_dados_basicos(dados: dict) -> dict:
    """Formata dados básicos para estrutura de tabela PDF (parâmetro-valor)."""
    if not isinstance(dados, dict) or not dados:
        log.warning("Dados básicos ausentes para formatação PDF.")
        return {}  # Retorna dicionário vazio

    log.debug("Formatando dados básicos para PDF...")
    # Map internal keys to user-friendly labels
    nomes_amigaveis = {
        "tipo_transformador": "Tipo",
        "potencia_mva": "Potência (MVA)",
        "frequencia": "Frequência (Hz)",
        "tensao_at": "Tensão Nom. AT (kV)",
        "corrente_nominal_at": "Corrente Nom. AT (A)",
        "impedancia": "Impedância Nom. (%)",
        "conexao_at": "Conexão AT",
        "nbi_at": "NBI AT (kV)",
        "tensao_at_tap_maior": "Tensão Tap+ AT (kV)",
        "corrente_nominal_at_tap_maior": "Corrente Tap+ AT (A)",
        "impedancia_tap_maior": "Impedância Tap+ (%)",
        "tensao_at_tap_menor": "Tensão Tap- AT (kV)",
        "corrente_nominal_at_tap_menor": "Corrente Tap- AT (A)",
        "impedancia_tap_menor": "Impedância Tap- (%)",
        "tensao_bt": "Tensão Nom. BT (kV)",
        "corrente_nominal_bt": "Corrente Nom. BT (A)",
        "conexao_bt": "Conexão BT",
        "nbi_bt": "NBI BT (kV)",
        "tensao_terciario": "Tensão Nom. Terciário (kV)",
        "corrente_nominal_terciario": "Corrente Nom. Terciário (A)",
        "conexao_terciario": "Conexão Terciário",
        "nbi_terciario": "NBI Terciário (kV)",
        "tensao_bucha_neutro_at": "Tensão Bucha Neutro AT (kV)",
        "tensao_bucha_neutro_bt": "Tensão Bucha Neutro BT (kV)",
        "tensao_bucha_neutro_terciario": "Tensão Bucha Neutro Ter. (kV)",
        "peso_total": "Peso Total (kg)",
        "peso_parte_ativa": "Peso Parte Ativa (kg)",
        "peso_oleo": "Peso Óleo (kg)",
        "elevacao_enrol": "Elevação Enrol. (°C)",
        "elevacao_oleo_topo": "Elevação Óleo Topo (°C)",
        "teste_tensao_aplicada_at": "Tensão Aplicada AT (kV)",
        "teste_tensao_aplicada_bt": "Tensão Aplicada BT (kV)",
        "teste_tensao_aplicada_terciario": "Tensão Aplicada Terciário (kV)",
        "teste_tensao_induzida_at": "Tensão Induzida AT (kV)",
    }
    # Define the order of fields in the report
    ordem_campos = [
        "tipo_transformador",
        "potencia_mva",
        "frequencia",
        "tensao_at",
        "corrente_nominal_at",
        "impedancia",
        "conexao_at",
        "nbi_at",
        "tensao_bucha_neutro_at",
        "tensao_at_tap_maior",
        "corrente_nominal_at_tap_maior",
        "impedancia_tap_maior",
        "tensao_at_tap_menor",
        "corrente_nominal_at_tap_menor",
        "impedancia_tap_menor",
        "tensao_bt",
        "corrente_nominal_bt",
        "conexao_bt",
        "nbi_bt",
        "tensao_bucha_neutro_bt",
        "tensao_terciario",
        "corrente_nominal_terciario",
        "conexao_terciario",
        "nbi_terciario",
        "tensao_bucha_neutro_terciario",
        "peso_total",
        "peso_parte_ativa",
        "peso_oleo",
        "elevacao_enrol",
        "elevacao_oleo_topo",
        "teste_tensao_aplicada_at",
        "teste_tensao_aplicada_bt",
        "teste_tensao_aplicada_terciario",
        "teste_tensao_induzida_at",
    ]

    # Create formatted dictionary (Parameter: Value)
    dados_formatados_pv = {}
    for k in ordem_campos:
        valor = dados.get(k)
        if valor is not None and str(valor).strip() != "":
            # Determine precision based on key
            precision = (
                0 if "peso" in k else (1 if "mva" in k or "tensao" in k or "nbi" in k else 2)
            )
            unit = (
                "kV"
                if "tensao" in k or "nbi" in k
                else (
                    "%"
                    if "impedancia" in k
                    else (
                        "kg"
                        if "peso" in k
                        else (
                            "Hz"
                            if "freq" in k
                            else ("A" if "corrente" in k else ("MVA" if "potencia" in k else ("°C" if "elevacao" in k else "")))
                        )
                    )
                )
            )
            valor_formatado = format_parameter_value(valor, precision, unit)
            dados_formatados_pv[nomes_amigaveis.get(k, k)] = valor_formatado

    # Return in the structure expected by add_section {Title: {Param: Val}}
    return {"Dados Nominais e Características": dados_formatados_pv} if dados_formatados_pv else {}


def formatar_perdas_vazio(dados_vazio: dict | None) -> dict:
    """Formata dados de perdas em vazio para estrutura PDF (dicionários Parameter:Value)."""
    if not isinstance(dados_vazio, dict) or not dados_vazio:
        log.warning("Dados de perdas em vazio ausentes para formatação PDF.")
        return {}

    log.debug("Formatando perdas em vazio para PDF...")
    results_projeto = dados_vazio.get("resultados_projeto", {})
    results_m4 = dados_vazio.get("resultados_aco_m4", {})
    inputs_vazio = dados_vazio.get("inputs_vazio", {})

    # Define precision and units for each key
    formatting_rules = {
        "Perdas em Vazio (kW)": {"prec": 2, "unit": "kW"},
        "Tensão nominal teste 1.0 pu (kV)": {"prec": 2, "unit": "kV"},
        "Corrente de excitação (A)": {"prec": 2, "unit": "A"},
        "Corrente de excitação calculada (A)": {"prec": 2, "unit": "A"},
        "Tensão de teste 1.1 pu (kV)": {"prec": 2, "unit": "kV"},
        "Corrente de excitação 1.1 pu (A)": {"prec": 2, "unit": "A"},
        "Tensão de teste 1.2 pu (kV)": {"prec": 2, "unit": "kV"},
        "Corrente de excitação 1.2 pu (A)": {"prec": 2, "unit": "A"},
        "Frequência (Hz)": {"prec": 2, "unit": "Hz"},
        "Potência Mag. (kVAr)": {"prec": 2, "unit": "kVAr"},
        "Fator de perdas Mag. (VAr/kg)": {"prec": 2, "unit": "VAr/kg"},
        "Fator de perdas (W/kg)": {"prec": 2, "unit": "W/kg"},
        "Peso do núcleo de projeto (Ton)": {"prec": 2, "unit": "Ton"},
        "Peso do núcleo Calculado(Ton)": {"prec": 2, "unit": "Ton"},
        "Potência de Ensaio (1 pu) (kVA)": {"prec": 2, "unit": "kVA"},
        "Potência de Ensaio (1.1 pu) (kVA)": {"prec": 2, "unit": "kVA"},
        "Potência de Ensaio (1.2 pu) (kVA)": {"prec": 2, "unit": "kVA"},
    }

    def format_section(data_dict):
        formatted = {}
        for key_orig, value in data_dict.items():
            if value is not None:
                rules = formatting_rules.get(
                    key_orig, {"prec": 2, "unit": ""}
                )  # Default formatting
                formatted[key_orig] = format_parameter_value(value, rules["prec"], rules["unit"])
        return formatted

    # Format each section
    formatted_projeto = format_section(results_projeto)
    formatted_m4 = format_section(results_m4)
    formatted_inputs = format_section(inputs_vazio)

    # Combine into final structure
    result = {}
    if formatted_inputs:
        result["Inputs de Perdas em Vazio"] = formatted_inputs
    if formatted_projeto:
        result["Resultados de Projeto"] = formatted_projeto
    if formatted_m4:
        result["Resultados Aço M4"] = formatted_m4

    return result


def formatar_perdas_carga(dados_carga: dict | None) -> dict:
    """Formata dados de perdas em carga para estrutura PDF (dicionários Parameter:Value)."""
    if not isinstance(dados_carga, dict) or not dados_carga:
        log.warning("Dados de perdas em carga ausentes para formatação PDF.")
        return {}

    log.debug("Formatando perdas em carga para PDF...")
    results_carga = dados_carga.get("resultados_carga", {})
    inputs_carga = dados_carga.get("inputs_carga", {})

    # Define precision and units for each key
    formatting_rules = {
        "Perdas em Carga (kW)": {"prec": 2, "unit": "kW"},
        "Perdas I²R (kW)": {"prec": 2, "unit": "kW"},
        "Perdas Adicionais (kW)": {"prec": 2, "unit": "kW"},
        "Impedância (%)": {"prec": 2, "unit": "%"},
        "Temperatura de Referência (°C)": {"prec": 1, "unit": "°C"},
        "Temperatura de Ensaio (°C)": {"prec": 1, "unit": "°C"},
        "Corrente de Ensaio (A)": {"prec": 2, "unit": "A"},
        "Tensão de Ensaio (V)": {"prec": 2, "unit": "V"},
        "Potência de Ensaio (kW)": {"prec": 2, "unit": "kW"},
    }

    def format_section(data_dict):
        formatted = {}
        for key_orig, value in data_dict.items():
            if value is not None:
                rules = formatting_rules.get(
                    key_orig, {"prec": 2, "unit": ""}
                )  # Default formatting
                formatted[key_orig] = format_parameter_value(value, rules["prec"], rules["unit"])
        return formatted

    # Format each section
    formatted_results = format_section(results_carga)
    formatted_inputs = format_section(inputs_carga)

    # Combine into final structure
    result = {}
    if formatted_inputs:
        result["Inputs de Perdas em Carga"] = formatted_inputs
    if formatted_results:
        result["Resultados de Perdas em Carga"] = formatted_results

    return result


def formatar_impulso(dados_impulso: dict | None) -> dict:
    """Formata dados de impulso para estrutura PDF."""
    if not isinstance(dados_impulso, dict) or not dados_impulso:
        log.warning("Dados de impulso ausentes para formatação PDF.")
        return {}

    log.debug("Formatando dados de impulso para PDF...")
    resultados = dados_impulso.get("resultados_impulso", {})
    inputs = dados_impulso.get("inputs_impulso", {})

    # Define precision and units for each key
    formatting_rules = {
        "Tensão de Impulso AT (kV)": {"prec": 1, "unit": "kV"},
        "Tensão de Impulso BT (kV)": {"prec": 1, "unit": "kV"},
        "Tensão de Impulso Terciário (kV)": {"prec": 1, "unit": "kV"},
        "Tempo de Frente (μs)": {"prec": 2, "unit": "μs"},
        "Tempo de Cauda (μs)": {"prec": 2, "unit": "μs"},
        "Eficiência (%)": {"prec": 2, "unit": "%"},
    }

    def format_section(data_dict):
        formatted = {}
        for key_orig, value in data_dict.items():
            if value is not None:
                rules = formatting_rules.get(
                    key_orig, {"prec": 2, "unit": ""}
                )  # Default formatting
                formatted[key_orig] = format_parameter_value(value, rules["prec"], rules["unit"])
        return formatted

    # Format each section
    formatted_results = format_section(resultados)
    formatted_inputs = format_section(inputs)

    # Combine into final structure
    result = {}
    if formatted_inputs:
        result["Inputs de Impulso"] = formatted_inputs
    if formatted_results:
        result["Resultados de Impulso"] = formatted_results

    # Adicionar gráficos se disponíveis
    if "grafico_impulso" in dados_impulso and dados_impulso["grafico_impulso"]:
        try:
            # Aqui você pode adicionar lógica para incluir gráficos no relatório
            # Por exemplo, convertendo dados de gráfico para uma imagem
            result["Gráficos de Impulso"] = {"Gráfico disponível": "Sim"}
        except Exception as e:
            log.error(f"Erro ao processar gráfico de impulso: {e}")

    return result


def formatar_analise_dieletrica(dados_dieletrica: dict | None) -> dict:
    """Formata dados de análise dielétrica para estrutura PDF."""
    if not isinstance(dados_dieletrica, dict) or not dados_dieletrica:
        log.warning("Dados de análise dielétrica ausentes para formatação PDF.")
        return {}

    log.debug("Formatando dados de análise dielétrica para PDF...")
    resultados = dados_dieletrica.get("resultados_dieletrica", {})
    inputs = dados_dieletrica.get("inputs_dieletrica", {})

    # Define precision and units for each key
    formatting_rules = {
        "Tensão Aplicada AT (kV)": {"prec": 1, "unit": "kV"},
        "Tensão Aplicada BT (kV)": {"prec": 1, "unit": "kV"},
        "Tensão Aplicada Terciário (kV)": {"prec": 1, "unit": "kV"},
        "Tensão Induzida AT (kV)": {"prec": 1, "unit": "kV"},
        "Frequência de Ensaio (Hz)": {"prec": 0, "unit": "Hz"},
        "Fator de Dissipação (%)": {"prec": 3, "unit": "%"},
        "Capacitância (pF)": {"prec": 1, "unit": "pF"},
    }

    def format_section(data_dict):
        formatted = {}
        for key_orig, value in data_dict.items():
            if value is not None:
                rules = formatting_rules.get(
                    key_orig, {"prec": 2, "unit": ""}
                )  # Default formatting
                formatted[key_orig] = format_parameter_value(value, rules["prec"], rules["unit"])
        return formatted

    # Format each section
    formatted_results = format_section(resultados)
    formatted_inputs = format_section(inputs)

    # Combine into final structure
    result = {}
    if formatted_inputs:
        result["Inputs de Análise Dielétrica"] = formatted_inputs
    if formatted_results:
        result["Resultados de Análise Dielétrica"] = formatted_results

    return result


def formatar_tensao_aplicada(dados_aplicada: dict | None) -> dict:
    """Formata dados de tensão aplicada para estrutura PDF."""
    if not isinstance(dados_aplicada, dict) or not dados_aplicada:
        log.warning("Dados de tensão aplicada ausentes para formatação PDF.")
        return {}

    log.debug("Formatando dados de tensão aplicada para PDF...")
    resultados = dados_aplicada.get("resultados_aplicada", {})
    inputs = dados_aplicada.get("inputs_aplicada", {})

    # Define precision and units for each key
    formatting_rules = {
        "Tensão de Ensaio AT (kV)": {"prec": 1, "unit": "kV"},
        "Tensão de Ensaio BT (kV)": {"prec": 1, "unit": "kV"},
        "Tensão de Ensaio Terciário (kV)": {"prec": 1, "unit": "kV"},
        "Duração (s)": {"prec": 0, "unit": "s"},
        "Frequência (Hz)": {"prec": 0, "unit": "Hz"},
        "Temperatura Ambiente (°C)": {"prec": 1, "unit": "°C"},
        "Umidade Relativa (%)": {"prec": 1, "unit": "%"},
    }

    def format_section(data_dict):
        formatted = {}
        for key_orig, value in data_dict.items():
            if value is not None:
                rules = formatting_rules.get(
                    key_orig, {"prec": 2, "unit": ""}
                )  # Default formatting
                formatted[key_orig] = format_parameter_value(value, rules["prec"], rules["unit"])
        return formatted

    # Format each section
    formatted_results = format_section(resultados)
    formatted_inputs = format_section(inputs)

    # Combine into final structure
    result = {}
    if formatted_inputs:
        result["Inputs de Tensão Aplicada"] = formatted_inputs
    if formatted_results:
        result["Resultados de Tensão Aplicada"] = formatted_results

    return result


def formatar_tensao_induzida(dados_induzida: dict | None) -> dict:
    """Formata dados de tensão induzida para estrutura PDF."""
    if not isinstance(dados_induzida, dict) or not dados_induzida:
        log.warning("Dados de tensão induzida ausentes para formatação PDF.")
        return {}

    log.debug("Formatando dados de tensão induzida para PDF...")
    resultados = dados_induzida.get("resultados_induzida", {})
    inputs = dados_induzida.get("inputs_induzida", {})

    # Define precision and units for each key
    formatting_rules = {
        "Tensão de Ensaio AT (kV)": {"prec": 1, "unit": "kV"},
        "Tensão de Ensaio BT (kV)": {"prec": 1, "unit": "kV"},
        "Tensão de Ensaio Terciário (kV)": {"prec": 1, "unit": "kV"},
        "Duração (s)": {"prec": 0, "unit": "s"},
        "Frequência de Ensaio (Hz)": {"prec": 0, "unit": "Hz"},
        "Temperatura Ambiente (°C)": {"prec": 1, "unit": "°C"},
        "Umidade Relativa (%)": {"prec": 1, "unit": "%"},
    }

    def format_section(data_dict):
        formatted = {}
        for key_orig, value in data_dict.items():
            if value is not None:
                rules = formatting_rules.get(
                    key_orig, {"prec": 2, "unit": ""}
                )  # Default formatting
                formatted[key_orig] = format_parameter_value(value, rules["prec"], rules["unit"])
        return formatted

    # Format each section
    formatted_results = format_section(resultados)
    formatted_inputs = format_section(inputs)

    # Combine into final structure
    result = {}
    if formatted_inputs:
        result["Inputs de Tensão Induzida"] = formatted_inputs
    if formatted_results:
        result["Resultados de Tensão Induzida"] = formatted_results

    return result


def formatar_curto_circuito(dados_curto: dict | None) -> dict:
    """Formata dados de curto-circuito para estrutura PDF."""
    if not isinstance(dados_curto, dict) or not dados_curto:
        log.warning("Dados de curto-circuito ausentes para formatação PDF.")
        return {}

    log.debug("Formatando dados de curto-circuito para PDF...")
    resultados = dados_curto.get("resultados_curto_circuito", {})
    inputs = dados_curto.get("inputs_curto_circuito", {})

    # Define precision and units for each key
    formatting_rules = {
        "Corrente de Curto-Circuito AT (kA)": {"prec": 2, "unit": "kA"},
        "Corrente de Curto-Circuito BT (kA)": {"prec": 2, "unit": "kA"},
        "Corrente de Curto-Circuito Terciário (kA)": {"prec": 2, "unit": "kA"},
        "Força Axial (kN)": {"prec": 2, "unit": "kN"},
        "Força Radial (kN)": {"prec": 2, "unit": "kN"},
        "Tensão Mecânica (MPa)": {"prec": 2, "unit": "MPa"},
        "Impedância (%)": {"prec": 2, "unit": "%"},
        "Potência (MVA)": {"prec": 2, "unit": "MVA"},
        "Tensão AT (kV)": {"prec": 1, "unit": "kV"},
        "Corrente Nominal AT (A)": {"prec": 2, "unit": "A"},
    }

    def format_section(data_dict):
        formatted = {}
        for key_orig, value in data_dict.items():
            if value is not None:
                rules = formatting_rules.get(
                    key_orig, {"prec": 2, "unit": ""}
                )  # Default formatting
                formatted[key_orig] = format_parameter_value(value, rules["prec"], rules["unit"])
        return formatted

    # Format each section
    formatted_results = format_section(resultados)
    formatted_inputs = format_section(inputs)

    # Combine into final structure
    result = {}
    if formatted_inputs:
        result["Inputs de Curto-Circuito"] = formatted_inputs
    if formatted_results:
        result["Resultados de Curto-Circuito"] = formatted_results

    return result


def formatar_elevacao_temperatura(dados_temp: dict | None) -> dict:
    """Formata dados de elevação de temperatura para estrutura PDF."""
    if not isinstance(dados_temp, dict) or not dados_temp:
        log.warning("Dados de elevação de temperatura ausentes para formatação PDF.")
        return {}

    log.debug("Formatando dados de elevação de temperatura para PDF...")
    resultados = dados_temp.get("resultados_temp_rise", {})
    inputs = dados_temp.get("inputs_temp_rise", {})

    # Define precision and units for each key
    formatting_rules = {
        "Temperatura Ambiente (°C)": {"prec": 1, "unit": "°C"},
        "Material do Enrolamento": {"prec": 0, "unit": ""},
        "Resistência a Frio (Ω)": {"prec": 6, "unit": "Ω"},
        "Temperatura a Frio (°C)": {"prec": 1, "unit": "°C"},
        "Resistência a Quente (Ω)": {"prec": 6, "unit": "Ω"},
        "Temperatura do Óleo (°C)": {"prec": 1, "unit": "°C"},
        "Elevação Máxima do Óleo (°C)": {"prec": 1, "unit": "°C"},
        "Temperatura Média do Enrolamento (°C)": {"prec": 1, "unit": "°C"},
        "Elevação Média do Enrolamento (°C)": {"prec": 1, "unit": "°C"},
        "Elevação do Óleo (°C)": {"prec": 1, "unit": "°C"},
        "Potência Total Utilizada (kW)": {"prec": 2, "unit": "kW"},
        "Constante de Tempo Térmica (h)": {"prec": 2, "unit": "h"},
    }

    def format_section(data_dict):
        formatted = {}
        for key_orig, value in data_dict.items():
            if value is not None:
                rules = formatting_rules.get(
                    key_orig, {"prec": 2, "unit": ""}
                )  # Default formatting
                formatted[key_orig] = format_parameter_value(value, rules["prec"], rules["unit"])
        return formatted

    # Format each section
    formatted_results = format_section(resultados)
    formatted_inputs = format_section(inputs)

    # Combine into final structure
    result = {}
    if formatted_inputs:
        result["Inputs de Elevação de Temperatura"] = formatted_inputs
    if formatted_results:
        result["Resultados de Elevação de Temperatura"] = formatted_results

    return result
