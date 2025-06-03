# -*- coding: utf-8 -*-
"""
Módulo de callbacks para a seção de Tensão Induzida.
Utiliza o padrão de registro centralizado de callbacks para evitar problemas com o reloader.
"""
import datetime
import logging
import math
import numbers # For type checking

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
from dash import Input, Output, State, dcc, html, no_update, callback_context
from dash.exceptions import PreventUpdate
from plotly import graph_objects as go

# Importações da aplicação
from components.formatters import format_parameter_value
from utils.theme_colors import APP_COLORS # Import centralized APP_COLORS
from utils.routes import ROUTE_INDUCED_VOLTAGE, normalize_pathname

# Configurar logger
log = logging.getLogger(__name__)

# --- Funções Auxiliares ---
def safe_float(value, default=None):
    """Converte valor para float de forma segura, retorna default em caso de erro."""
    if value is None or value == "":
        return default
    try:
        if isinstance(value, str):
            value = value.replace(",", ".")
        return float(value)
    except (ValueError, TypeError):
        log.warning(f"safe_float: Não foi possível converter '{value}' para float. Retornando default: {default}")
        return default

# Tabelas de potência magnética e perdas do núcleo
potencia_magnet = {
    (0.5, 50): 0.10, (0.5, 60): 0.15, (0.5, 100): 0.35, (0.5, 120): 0.45, (0.5, 150): 0.70, (0.5, 200): 1.00, (0.5, 240): 1.30,
    (0.6, 50): 0.15, (0.6, 60): 0.20, (0.6, 100): 0.45, (0.6, 120): 0.60, (0.6, 150): 0.90, (0.6, 200): 1.40, (0.6, 240): 1.80,
    (0.7, 50): 0.23, (0.7, 60): 0.28, (0.7, 100): 0.60, (0.7, 120): 0.80, (0.7, 150): 1.10, (0.7, 200): 1.70, (0.7, 240): 2.30,
    (0.8, 50): 0.30, (0.8, 60): 0.35, (0.8, 100): 0.80, (0.8, 120): 1.00, (0.8, 150): 1.40, (0.8, 200): 2.20, (0.8, 240): 3.00,
    (0.9, 50): 0.38, (0.9, 60): 0.45, (0.9, 100): 0.95, (0.9, 120): 1.30, (0.9, 150): 1.70, (0.9, 200): 2.80, (0.9, 240): 3.80,
    (1.0, 50): 0.45, (1.0, 60): 0.55, (1.0, 100): 1.10, (1.0, 120): 1.60, (1.0, 150): 2.20, (1.0, 200): 3.50, (1.0, 240): 4.50,
    (1.1, 50): 0.55, (1.1, 60): 0.70, (1.1, 100): 1.50, (1.1, 120): 2.00, (1.1, 150): 2.80, (1.1, 200): 4.10, (1.1, 240): 5.50,
    (1.2, 50): 0.65, (1.2, 60): 0.85, (1.2, 100): 2.00, (1.2, 120): 2.40, (1.2, 150): 3.30, (1.2, 200): 5.00, (1.2, 240): 6.50,
    (1.3, 50): 0.80, (1.3, 60): 1.00, (1.3, 100): 2.20, (1.3, 120): 2.85, (1.3, 150): 3.80, (1.3, 200): 6.00, (1.3, 240): 7.50,
    (1.4, 50): 0.95, (1.4, 60): 1.20, (1.4, 100): 2.50, (1.4, 120): 3.30, (1.4, 150): 4.50, (1.4, 200): 7.00, (1.4, 240): 9.00,
    (1.5, 50): 1.10, (1.5, 60): 1.40, (1.5, 100): 3.00, (1.5, 120): 4.00, (1.5, 150): 5.50, (1.5, 200): 9.00, (1.5, 240): 11.00,
    (1.6, 50): 1.30, (1.6, 60): 1.60, (1.6, 100): 3.50, (1.6, 120): 4.80, (1.6, 150): 6.50, (1.6, 200): 12.00, (1.6, 240): 14.00,
    (1.7, 50): 1.60, (1.7, 60): 2.00, (1.7, 100): 4.00, (1.7, 120): 5.50, (1.7, 150): 7.00, (1.7, 200): 15.00, (1.7, 240): 17.00,
}
perdas_nucleo = {
    (0.5, 50): 0.10, (0.5, 60): 0.13, (0.5, 100): 0.25, (0.5, 120): 0.35, (0.5, 150): 0.50, (0.5, 200): 0.80, (0.5, 240): 1.10,
    (0.6, 50): 0.12, (0.6, 60): 0.18, (0.6, 100): 0.38, (0.6, 120): 0.48, (0.6, 150): 0.70, (0.6, 200): 1.10, (0.6, 240): 1.50,
    (0.7, 50): 0.15, (0.7, 60): 0.23, (0.7, 100): 0.50, (0.7, 120): 0.62, (0.7, 150): 0.95, (0.7, 200): 1.55, (0.7, 240): 2.10,
    (0.8, 50): 0.20, (0.8, 60): 0.30, (0.8, 100): 0.65, (0.8, 120): 0.80, (0.8, 150): 1.20, (0.8, 200): 2.00, (0.8, 240): 2.80,
    (0.9, 50): 0.25, (0.9, 60): 0.37, (0.9, 100): 0.82, (0.9, 120): 1.00, (0.9, 150): 1.50, (0.9, 200): 2.50, (0.9, 240): 3.50,
    (1.0, 50): 0.32, (1.0, 60): 0.46, (1.0, 100): 1.00, (1.0, 120): 1.25, (1.0, 150): 1.85, (1.0, 200): 3.10, (1.0, 240): 4.20,
    (1.1, 50): 0.41, (1.1, 60): 0.55, (1.1, 100): 1.21, (1.1, 120): 1.55, (1.1, 150): 2.20, (1.1, 200): 3.70, (1.1, 240): 5.00,
    (1.2, 50): 0.50, (1.2, 60): 0.65, (1.2, 100): 1.41, (1.2, 120): 1.90, (1.2, 150): 2.70, (1.2, 200): 4.50, (1.2, 240): 6.00,
    (1.3, 50): 0.60, (1.3, 60): 0.80, (1.3, 100): 1.65, (1.3, 120): 2.30, (1.3, 150): 3.20, (1.3, 200): 5.20, (1.3, 240): 7.00,
    (1.4, 50): 0.71, (1.4, 60): 0.95, (1.4, 100): 1.95, (1.4, 120): 2.80, (1.4, 150): 3.80, (1.4, 200): 6.00, (1.4, 240): 8.50,
    (1.5, 50): 0.85, (1.5, 60): 1.10, (1.5, 100): 2.30, (1.5, 120): 3.30, (1.5, 150): 4.50, (1.5, 200): 7.00, (1.5, 240): 10.00,
    (1.6, 50): 1.00, (1.6, 60): 1.30, (1.6, 100): 2.80, (1.6, 120): 3.80, (1.6, 150): 5.30, (1.6, 200): 8.00, (1.6, 240): 12.00,
    (1.7, 50): 1.20, (1.7, 60): 1.55, (1.7, 100): 3.50, (1.7, 120): 4.40, (1.7, 150): 6.00, (1.7, 200): 9.00, (1.7, 240): 15.00,
}

df_potencia_magnet = pd.DataFrame(list(potencia_magnet.items()), columns=["key", "potencia_magnet"])
df_potencia_magnet[["inducao_nominal", "frequencia_nominal"]] = pd.DataFrame(
    df_potencia_magnet["key"].tolist(), index=df_potencia_magnet.index
)
df_potencia_magnet.drop("key", axis=1, inplace=True)
df_potencia_magnet.set_index(["inducao_nominal", "frequencia_nominal"], inplace=True)

df_perdas_nucleo = pd.DataFrame(list(perdas_nucleo.items()), columns=["key", "perdas_nucleo"])
df_perdas_nucleo[["inducao_nominal", "frequencia_nominal"]] = pd.DataFrame(
    df_perdas_nucleo["key"].tolist(), index=df_perdas_nucleo.index
)
df_perdas_nucleo.drop("key", axis=1, inplace=True)
df_perdas_nucleo.set_index(["inducao_nominal", "frequencia_nominal"], inplace=True)

def buscar_valores_tabela(inducao_teste, frequencia_teste, df):
    """Busca valores nas tabelas usando interpolação bilinear."""
    # Ensure inputs are float
    inducao_teste = safe_float(inducao_teste, default=0.0)
    frequencia_teste = safe_float(frequencia_teste, default=0.0)

    # Ensure values are not None and are floats
    if inducao_teste is None:
        inducao_teste = 0.0
    if frequencia_teste is None:
        frequencia_teste = 0.0

    inducoes = sorted(df.index.get_level_values("inducao_nominal").unique())
    frequencias = sorted(df.index.get_level_values("frequencia_nominal").unique())

    inducao_teste_clipped = max(min(float(inducao_teste), max(inducoes)), min(inducoes))
    frequencia_teste_clipped = max(min(float(frequencia_teste), max(frequencias)), min(frequencias))
    
    if inducao_teste != inducao_teste_clipped:
        log.warning(f"Indução de teste {inducao_teste:.3f}T fora do range da tabela [{min(inducoes)}, {max(inducoes)}], usando {inducao_teste_clipped:.3f}T.")
    if frequencia_teste != frequencia_teste_clipped:
        log.warning(f"Frequência de teste {frequencia_teste:.1f}Hz fora do range da tabela [{min(frequencias)}, {max(frequencias)}], usando {frequencia_teste_clipped:.1f}Hz.")

    inducao_teste = inducao_teste_clipped
    frequencia_teste = frequencia_teste_clipped

    ind_idx = np.searchsorted(inducoes, inducao_teste)
    freq_idx = np.searchsorted(frequencias, frequencia_teste)

    ind_idx = min(max(ind_idx, 1), len(inducoes) - 1)
    freq_idx = min(max(freq_idx, 1), len(frequencias) - 1)

    ind_low, ind_high = inducoes[ind_idx - 1], inducoes[ind_idx]
    freq_low, freq_high = frequencias[freq_idx - 1], frequencias[freq_idx]
    
    q11 = df.loc[(ind_low, freq_low), df.columns[0]]
    q12 = df.loc[(ind_low, freq_high), df.columns[0]]
    q21 = df.loc[(ind_high, freq_low), df.columns[0]]
    q22 = df.loc[(ind_high, freq_high), df.columns[0]]
    
    # Ensure q values are float
    q11, q12, q21, q22 = float(q11), float(q12), float(q21), float(q22)

    x = (inducao_teste - ind_low) / (ind_high - ind_low) if (ind_high - ind_low) != 0 else 0
    y = (frequencia_teste - freq_low) / (freq_high - freq_low) if (freq_high - freq_low) != 0 else 0
    
    valor_interpolado = (1 - x) * (1 - y) * q11 + x * (1 - y) * q21 + (1 - x) * y * q12 + x * y * q22
    return float(valor_interpolado)


def register_induced_voltage_callbacks(app_instance):
    log.debug("Registrando callbacks de Tensão Induzida")

    @app_instance.callback(
        [
            Output("tipo-transformador", "value"),
            Output("frequencia-teste", "value"),
            Output("capacitancia", "value"),
        ],
        [
            Input("url", "pathname"),
            Input("transformer-inputs-store", "data"),
            Input("induced-voltage-store", "data")
        ],
        prevent_initial_call=False
    )
    def load_induced_voltage_inputs(pathname, transformer_data_global, induced_data_local):
        triggered_id = callback_context.triggered_id
        log.debug(f"[LOAD InducedInputs] Acionado por: {triggered_id}, Pathname: {pathname}")

        clean_path = normalize_pathname(pathname) if pathname else ""
        if clean_path != ROUTE_INDUCED_VOLTAGE and triggered_id == 'url':
            log.debug(f"[LOAD InducedInputs] Não na página de Tensão Induzida ({clean_path}). Abortando trigger de URL.")
            raise PreventUpdate

        tipo_trafo_local = None
        freq_teste_local = None
        cap_local = None

        if induced_data_local and isinstance(induced_data_local, dict):
            inputs_local_dict = induced_data_local.get('inputs', {}) # Check for 'inputs' sub-dictionary
            if isinstance(inputs_local_dict, dict):
                tipo_trafo_local = inputs_local_dict.get('tipo_transformador')
                freq_teste_local = inputs_local_dict.get('freq_teste')
                cap_local = inputs_local_dict.get('capacitancia')
            
            # Fallback to direct keys if not in 'inputs'
            if tipo_trafo_local is None: tipo_trafo_local = induced_data_local.get("tipo_transformador")
            if freq_teste_local is None: freq_teste_local = induced_data_local.get("freq_teste")
            if cap_local is None: cap_local = induced_data_local.get("capacitancia")

        tipo_trafo_global = None
        if transformer_data_global and isinstance(transformer_data_global, dict):
            transformer_data_actual = transformer_data_global.get("transformer_data", transformer_data_global)
            tipo_trafo_global = transformer_data_actual.get('tipo_transformador')


        final_tipo_trafo = tipo_trafo_local if tipo_trafo_local else tipo_trafo_global if tipo_trafo_global else "Monofásico"
        final_freq_teste = safe_float(freq_teste_local)
        final_cap = safe_float(cap_local)

        log.debug(f"[LOAD InducedInputs] Valores para UI: TipoTrafo={final_tipo_trafo}, FreqTeste={final_freq_teste}, Cap={final_cap}")

        if (triggered_id == 'url' and clean_path == ROUTE_INDUCED_VOLTAGE) or \
           triggered_id == 'transformer-inputs-store' or \
           triggered_id == 'induced-voltage-store':
            return final_tipo_trafo, final_freq_teste, final_cap
        raise PreventUpdate

    @app_instance.callback(
        Output("transformer-info-induced-page", "children"),
        Input("transformer-info-induced", "children"),
        prevent_initial_call=False,
    )
    def update_induced_page_info_panel(global_panel_content):
        return global_panel_content

    @app_instance.callback(
        [
            Output("resultado-tensao-induzida", "children"),
            Output("induced-voltage-store", "data"),
            Output("induced-voltage-error-message", "children"),
        ],
        Input("calc-induced-voltage-btn", "n_clicks"),
        [
            State("transformer-inputs-store", "data"),
            State("losses-store", "data"),
            State("induced-voltage-store", "data"),
            State("url", "pathname"),
            State("frequencia-teste", "value"),
            State("capacitancia", "value"),
            State("tipo-transformador", "value"),
        ],
        prevent_initial_call=True,
    )
    def calculate_induced_voltage(
        n_clicks,
        transformer_data,
        losses_data,
        current_store_data,
        pathname,
        freq_teste_input,
        capacitancia_input,
        tipo_transformador_input,
    ):
        log.debug(f"[Induced Voltage] Callback calculate_induced_voltage: n_clicks={n_clicks}, pathname={pathname}")
        clean_path = normalize_pathname(pathname) if pathname else ""
        if clean_path != ROUTE_INDUCED_VOLTAGE:
            raise PreventUpdate
        if n_clicks is None or n_clicks == 0:
            return no_update, no_update, no_update

        error_div_style = {"color": APP_COLORS.get('danger', 'red'), "fontSize": "0.8rem"}

        if not transformer_data:
            return no_update, no_update, html.Div("Erro: Dados do transformador não disponíveis.", style=error_div_style)
        
        losses_data_dict = losses_data if isinstance(losses_data, dict) else {}
        resultados_perdas_vazio = losses_data_dict.get("resultados_perdas_vazio", {})
        if not losses_data or not isinstance(resultados_perdas_vazio, dict) or not resultados_perdas_vazio:
            return no_update, no_update, html.Div("Erro: Dados de perdas em vazio não disponíveis ou incompletos.", style=error_div_style)

        try:
            transformer_dict = transformer_data.get("transformer_data", transformer_data) if isinstance(transformer_data, dict) else {}
            
            freq_nominal = safe_float(transformer_dict.get("frequencia"), 60.0)
            if freq_nominal is None or freq_nominal <= 0: raise ValueError("Frequência nominal inválida.")

            freq_teste = safe_float(freq_teste_input)
            if freq_teste is None or freq_teste <= 0:
                raise ValueError("Frequência de teste inválida. Preencha o campo 'Teste (fp)'.")

            tensao_at = safe_float(transformer_dict.get("tensao_at"))
            if tensao_at is None or tensao_at <= 0: raise ValueError("Tensão AT nominal inválida.")
            
            tensao_bt = safe_float(transformer_dict.get("tensao_bt"), 0.0)

            tensao_prova = safe_float(transformer_dict.get("teste_tensao_induzida_at"))
            if tensao_prova is None or tensao_prova <= 0:
                raise ValueError("Tensão de ensaio (Up) 'teste_tensao_induzida_at' inválida ou não fornecida.")

            capacitancia = safe_float(capacitancia_input)
            if capacitancia is None or capacitancia <= 0:
                raise ValueError("Capacitância AT-GND inválida. Preencha o campo 'Cap. AT-GND (pF)'.")

            inducao_nominal = safe_float(resultados_perdas_vazio.get("inducao"))
            if inducao_nominal is None or inducao_nominal <= 0: raise ValueError("Indução nominal inválida (de Perdas).")
            
            peso_nucleo_ton = safe_float(resultados_perdas_vazio.get("peso_nucleo"))
            if peso_nucleo_ton is None or peso_nucleo_ton <= 0: raise ValueError("Peso do núcleo inválido (de Perdas).")
            
            peso_nucleo_kg = peso_nucleo_ton * 1000.0
            tipo_transformador = tipo_transformador_input or transformer_dict.get("tipo_transformador", "Trifásico")

            tensao_induzida = tensao_prova
            
            if tensao_at == 0: raise ValueError("Tensão AT nominal não pode ser zero para cálculo de indução.")
            if freq_teste == 0: raise ValueError("Frequência de teste não pode ser zero para cálculo de indução.")
            if freq_nominal == 0: raise ValueError("Frequência nominal não pode ser zero.")


            inducao_teste = inducao_nominal * (tensao_induzida / tensao_at) * (freq_nominal / freq_teste)
            inducao_teste = min(max(inducao_teste, 0.01), 1.9) 
            beta_teste = inducao_teste

            fp_fn = freq_teste / freq_nominal
            un_ref_at = tensao_at / math.sqrt(3) if tipo_transformador == "Trifásico" else tensao_at
            up_un = tensao_prova / un_ref_at if un_ref_at != 0 else 0
            
            tensao_aplicada_bt = (float(tensao_bt) / float(tensao_at)) * tensao_prova if tensao_bt is not None and tensao_at not in (None, 0) else 0

            fator_potencia_mag = buscar_valores_tabela(beta_teste, freq_teste, df_potencia_magnet)
            fator_perdas = buscar_valores_tabela(beta_teste, freq_teste, df_perdas_nucleo)

            results_data = {}
            pot_ativa = fator_perdas * peso_nucleo_kg / 1000.0
            pot_magnetica = fator_potencia_mag * peso_nucleo_kg / 1000.0

            if tipo_transformador == "Monofásico":
                pot_induzida = math.sqrt(max(0, pot_magnetica**2 - pot_ativa**2))
                up_un_float = float(up_un) if up_un is not None else 0.0
                tensao_bt_float = float(tensao_bt) if tensao_bt is not None else 0.0
                u_calc_scap = tensao_prova - (up_un_float * tensao_bt_float) # tensao_bt can be 0
                pcap = -(((u_calc_scap * 1000)**2 * 2 * math.pi * freq_teste * capacitancia * 1e-12) / 3) / 1000
                results_data = {
                    "tensao_aplicada_bt": tensao_aplicada_bt, "pot_ativa": pot_ativa,
                    "pot_magnetica": pot_magnetica, "pot_induzida": pot_induzida,
                    "u_dif": u_calc_scap, "pcap": pcap,
                }
            else: # Trifásico
                # Ensure tensao_aplicada_bt is float for division
                tensao_aplicada_bt_float = float(tensao_aplicada_bt) if tensao_aplicada_bt is not None else 0.0
                corrente_excitacao = pot_magnetica / (tensao_aplicada_bt_float * math.sqrt(3)) if tensao_aplicada_bt_float > 0 else 0.0
                potencia_teste = corrente_excitacao * tensao_aplicada_bt_float * math.sqrt(3)
                results_data = {
                    "tensao_aplicada_bt": tensao_aplicada_bt_float, "pot_ativa": pot_ativa,
                    "pot_magnetica": pot_magnetica, "corrente_excitacao": corrente_excitacao,
                    "potencia_teste": potencia_teste,
                }
            
            results_data.update({
                "tensao_induzida": tensao_prova, "frequencia_teste": freq_teste,
                "inducao_teste": beta_teste, "capacitancia": capacitancia,
                "tipo_transformador": tipo_transformador, "timestamp": datetime.datetime.now().isoformat(),
                "fator_potencia_mag": fator_potencia_mag, "fator_perdas": fator_perdas,
            })

            param_cell_style = {"backgroundColor": APP_COLORS.get("background_card", "#34495e"), "color": APP_COLORS.get("text_light", "#ecf0f1"), "fontWeight": "500", "fontSize": "0.8rem", "padding": "0.3rem 0.5rem", "textAlign": "left", "borderRight": f"1px solid {APP_COLORS.get('border', '#2c3e50')}", "fontFamily": "Arial, sans-serif"}
            value_cell_style = {**param_cell_style, "textAlign": "right", "fontFamily": "Consolas, monospace", "letterSpacing": "0.02rem"}
            unit_cell_style = {**param_cell_style, "color": APP_COLORS.get("text_muted", "#bdc3c7"), "fontStyle": "italic", "width": "60px"}
            card_header_style = {"backgroundColor": APP_COLORS.get("primary", "#3498db"), "color": APP_COLORS.get("text_header", "#FFFFFF"), "fontWeight": "bold", "fontSize": "0.9rem", "padding": "0.4rem 0.5rem", "borderBottom": f"1px solid {APP_COLORS.get('border_strong', '#666666')}", "borderRadius": "4px 4px 0 0"}
            card_style = {"backgroundColor": APP_COLORS.get("background_card", "#2c2c2c"), "border": f"1px solid {APP_COLORS.get('border', '#444444')}", "borderRadius": "4px", "boxShadow": "0 2px 4px rgba(0,0,0,0.2)", "height": "100%"}
            section_title_style = {"fontSize": "0.85rem", "color": APP_COLORS.get("accent", "#00BFFF"), "fontWeight": "bold", "marginBottom": "0.5rem"}
            table_style = {"fontSize": "0.8rem", "color": APP_COLORS.get("text_light", "#ecf0f1")}
            
            parametros_entrada_content = [
                html.Tr([html.Td("Tipo do Transformador", style=param_cell_style), html.Td(tipo_transformador, style=value_cell_style), html.Td("", style=unit_cell_style)]),
                html.Tr([html.Td("Tensão Nominal AT", style=param_cell_style), html.Td(format_parameter_value(tensao_at, 1), style=value_cell_style), html.Td("kV", style=unit_cell_style)]),
                html.Tr([html.Td("Tensão Nominal BT", style=param_cell_style), html.Td(format_parameter_value(tensao_bt, 1), style=value_cell_style), html.Td("kV", style=unit_cell_style)]),
                html.Tr([html.Td("Frequência Nominal", style=param_cell_style), html.Td(format_parameter_value(freq_nominal, 1), style=value_cell_style), html.Td("Hz", style=unit_cell_style)]),
                html.Tr([html.Td("Indução Nominal", style=param_cell_style), html.Td(format_parameter_value(inducao_nominal, 3), style=value_cell_style), html.Td("T", style=unit_cell_style)]),
                html.Tr([html.Td("Peso do Núcleo", style=param_cell_style), html.Td(format_parameter_value(peso_nucleo_ton, 1), style=value_cell_style), html.Td("Ton", style=unit_cell_style)]),
            ]
            parametros_entrada_table = dbc.Table(html.Tbody(parametros_entrada_content), bordered=True, hover=True, size="sm", className="table-dark mb-0", style=table_style)

            parametros_ensaio_content = [
                html.Tr([html.Td("Frequência de Teste", style=param_cell_style), html.Td(format_parameter_value(freq_teste, 1), style=value_cell_style), html.Td("Hz", style=unit_cell_style)]),
                html.Tr([html.Td("Relação fp/fn", style=param_cell_style), html.Td(format_parameter_value(fp_fn, 2), style=value_cell_style), html.Td("", style=unit_cell_style)]),
                html.Tr([html.Td("Tensão de Ensaio", style=param_cell_style), html.Td(format_parameter_value(tensao_prova, 1), style=value_cell_style), html.Td("kV", style=unit_cell_style)]),
                html.Tr([html.Td("Up/Un", style=param_cell_style), html.Td(format_parameter_value(up_un, 2), style=value_cell_style), html.Td("", style=unit_cell_style)]),
                html.Tr([html.Td("Capacitância AT-GND", style=param_cell_style), html.Td(format_parameter_value(capacitancia, 0), style=value_cell_style), html.Td("pF", style=unit_cell_style)]),
                html.Tr([html.Td("Indução no Teste (β)", style=param_cell_style), html.Td(format_parameter_value(beta_teste, 3), style=value_cell_style), html.Td("T", style=unit_cell_style)]),
                html.Tr([html.Td("Fator de Potência Magnética", style=param_cell_style), html.Td(format_parameter_value(fator_potencia_mag, 2), style=value_cell_style), html.Td("VAr/kg", style=unit_cell_style)]),
                html.Tr([html.Td("Fator de Perdas", style=param_cell_style), html.Td(format_parameter_value(fator_perdas, 2), style=value_cell_style), html.Td("W/kg", style=unit_cell_style)]),
            ]
            parametros_ensaio_table = dbc.Table(html.Tbody(parametros_ensaio_content), bordered=True, hover=True, size="sm", className="table-dark mb-0", style=table_style)
            
            resultados_calculados_content = []
            if tipo_transformador == "Monofásico":
                resultados_calculados_content.extend([
                    html.Tr([html.Td("Tensão Aplicada BT", style=param_cell_style), html.Td(format_parameter_value(results_data.get("tensao_aplicada_bt"), 1), style=value_cell_style), html.Td("kV", style=unit_cell_style)]),
                    html.Tr([html.Td("Potência Ativa Pw", style=param_cell_style), html.Td(format_parameter_value(results_data.get("pot_ativa"), 2), style=value_cell_style), html.Td("kW", style=unit_cell_style)]),
                    html.Tr([html.Td("Potência Reativa Magnética Sm", style=param_cell_style), html.Td(format_parameter_value(results_data.get("pot_magnetica"), 2), style=value_cell_style), html.Td("kVA", style=unit_cell_style)]),
                    html.Tr([html.Td("Componente Indutiva Sind", style=param_cell_style), html.Td(format_parameter_value(results_data.get("pot_induzida"), 2), style=value_cell_style), html.Td("kVAr ind", style=unit_cell_style)]),
                    html.Tr([html.Td("U para cálculo de Scap", style=param_cell_style), html.Td(format_parameter_value(results_data.get("u_dif"), 2), style=value_cell_style), html.Td("kV", style=unit_cell_style)]),
                    html.Tr([html.Td("Potência Capacitiva Scap", style={**param_cell_style, "fontWeight": "bold"}), html.Td(format_parameter_value(results_data.get("pcap"), 2), style={**value_cell_style, "fontWeight": "bold", "color": APP_COLORS.get("danger","red")}), html.Td("kVAr cap", style=unit_cell_style)]),
                ])
            else: # Trifásico
                resultados_calculados_content.extend([
                    html.Tr([html.Td("Tensão Aplicada BT", style=param_cell_style), html.Td(format_parameter_value(results_data.get("tensao_aplicada_bt"), 1), style=value_cell_style), html.Td("kV", style=unit_cell_style)]),
                    html.Tr([html.Td("Potência Ativa Pw", style=param_cell_style), html.Td(format_parameter_value(results_data.get("pot_ativa"), 2), style=value_cell_style), html.Td("kW", style=unit_cell_style)]),
                    html.Tr([html.Td("Potência Magnética Sm (Total)", style=param_cell_style), html.Td(format_parameter_value(results_data.get("pot_magnetica"), 2), style=value_cell_style), html.Td("kVA", style=unit_cell_style)]),
                    html.Tr([html.Td("Corrente de Excitação Iexc", style=param_cell_style), html.Td(format_parameter_value(results_data.get("corrente_excitacao"), 2), style=value_cell_style), html.Td("A", style=unit_cell_style)]),
                    html.Tr([html.Td("Potência de Teste (Total)", style={**param_cell_style, "fontWeight": "bold"}), html.Td(format_parameter_value(results_data.get("potencia_teste"), 2), style={**value_cell_style, "fontWeight": "bold", "backgroundColor": APP_COLORS.get("warning_bg_faint") if results_data.get("potencia_teste", 0) > 1500 else ""}), html.Td("kVA", style=unit_cell_style)]),
                ])
            resultados_calculados_table = dbc.Table(html.Tbody(resultados_calculados_content), bordered=True, hover=True, size="sm", className="table-dark mb-0", style=table_style)

            results_div = html.Div([
                dbc.Card([
                    dbc.CardHeader(html.H6(f"Resultados do Cálculo - {tipo_transformador}", className="m-0 text-center"), style=card_header_style),
                    dbc.CardBody([dbc.Row([
                        dbc.Col([html.H6("Parâmetros de Entrada", className="text-center", style=section_title_style), parametros_entrada_table], md=4),
                        dbc.Col([html.H6("Parâmetros do Ensaio", className="text-center", style=section_title_style), parametros_ensaio_table], md=4),
                        dbc.Col([html.H6(f"Resultados ({tipo_transformador})", className="text-center", style=section_title_style), resultados_calculados_table], md=4)
                    ])], style={"padding": "0.5rem"}),
                ], style=card_style),
            ])
            
            new_store_data = current_store_data.copy() if current_store_data and isinstance(current_store_data, dict) else {}
            new_store_data["inputs"] = { 
                    "freq_nominal": freq_nominal, "freq_teste": freq_teste, "tensao_at": tensao_at,
                    "tensao_bt": tensao_bt, "tensao_prova": tensao_prova, "capacitancia": capacitancia,
                    "inducao_nominal": inducao_nominal, "peso_nucleo_ton": peso_nucleo_ton,
                    "tipo_transformador": tipo_transformador,
            }
            new_store_data["resultados"] = results_data
            new_store_data["timestamp"] = datetime.datetime.now().isoformat()
            new_store_data["inputs_tensao_induzida"] = { # Storing UI inputs for this specific module
                "tipo_transformador": tipo_transformador_input,
                "freq_teste": freq_teste_input, # Store the raw input value
                "capacitancia": capacitancia_input, # Store the raw input value
            }
            
            return results_div, new_store_data, None

        except ValueError as ve:
            log.warning(f"[Induced Voltage] Erro de valor: {ve}")
            return no_update, no_update, html.Div(f"Erro de entrada: {str(ve)}", style=error_div_style)
        except Exception as e:
            log.error(f"Erro ao calcular tensão induzida: {e}", exc_info=True)
            return no_update, no_update, html.Div(f"Erro inesperado: {str(e)}", style=error_div_style)

    @app_instance.callback(
        Output("induced-voltage-error-message", "children", allow_duplicate=True),
        [
            Input("frequencia-teste", "value"),
            Input("capacitancia", "value"),
            Input("tipo-transformador", "value"),
        ],
        prevent_initial_call=True,
    )
    def monitor_remaining_inputs(freq_teste, capacitancia, tipo_transformador):
        ctx = callback_context
        if not ctx.triggered: return None
        input_id = ctx.triggered[0]["prop_id"].split(".")[0]
        input_value = ctx.triggered[0]["value"]
        id_to_name = {
            "frequencia-teste": "Teste (fp)",
            "capacitancia": "Cap. AT-GND (pF)",
            "tipo-transformador": "Tipo de Transformador",
        }
        input_name = id_to_name.get(input_id, input_id)
        log.debug(f"[Induced Voltage] VALOR INSERIDO NO CAMPO '{input_name}': {input_value}, tipo: {type(input_value)}")
        return None

    @app_instance.callback(
        Output("frequency-table-container", "children"),
        [
            Input("generate-frequency-table-button", "n_clicks"),
            Input("clear-frequency-table-button", "n_clicks"),
        ],
        [
            State("transformer-inputs-store", "data"),
            State("losses-store", "data"),
            State("induced-voltage-store", "data"), 
            State("tipo-transformador", "value"),
        ],
        prevent_initial_call=True,
    )
    def generate_frequency_table(
        generate_clicks,
        clear_clicks,
        transformer_data_global, 
        losses_data_global,      
        induced_data_local,      
        tipo_transformador_ui,
    ):
        ctx = callback_context
        if not ctx.triggered: raise PreventUpdate
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == "clear-frequency-table-button":
            return html.Div()
        if not generate_clicks:
            raise PreventUpdate

        log.debug(f"[Induced Voltage] Gerando tabela de frequências...")

        try:
            # Ensure data dictionaries are valid
            transformer_data_global_dict = transformer_data_global if isinstance(transformer_data_global, dict) else {}
            losses_data_global_dict = losses_data_global if isinstance(losses_data_global, dict) else {}
            induced_data_local_dict = induced_data_local if isinstance(induced_data_local, dict) else {}

            current_inputs = induced_data_local_dict.get("inputs", {})
            current_results = induced_data_local_dict.get("resultados", {})
            
            tipo_transformador = tipo_transformador_ui or \
                                 current_inputs.get("tipo_transformador") or \
                                 transformer_data_global_dict.get("tipo_transformador", "Monofásico")

            if tipo_transformador not in ["Monofásico", "Trifásico"]:
                return html.Div(f"Tabela não disponível para tipo '{tipo_transformador}'.", className="alert alert-info")

            # Extract and validate all necessary parameters using safe_float and providing defaults or raising errors
            tensao_at = safe_float(current_inputs.get("tensao_at", transformer_data_global_dict.get("tensao_at")))
            if tensao_at is None or tensao_at <= 0: raise ValueError("Tensão AT inválida.")
            
            tensao_bt = safe_float(current_inputs.get("tensao_bt", transformer_data_global_dict.get("tensao_bt")), 0.0)

            freq_nominal = safe_float(current_inputs.get("freq_nominal", transformer_data_global_dict.get("frequencia", 60.0)))
            if freq_nominal is None or freq_nominal <= 0: raise ValueError("Frequência Nominal inválida.")

            tensao_prova = safe_float(current_inputs.get("tensao_prova", transformer_data_global_dict.get("teste_tensao_induzida_at")))
            if tensao_prova is None or tensao_prova <= 0: raise ValueError("Tensão de Prova inválida.")

            capacitancia = safe_float(current_inputs.get("capacitancia")) # This should have been set by the main calc
            if capacitancia is None or capacitancia <= 0: raise ValueError("Capacitância AT-GND (do cálculo principal) inválida.")

            resultados_perdas_vazio_local = losses_data_global_dict.get("resultados_perdas_vazio", {})
            inducao_nominal = safe_float(resultados_perdas_vazio_local.get("inducao"))
            if inducao_nominal is None or inducao_nominal <= 0: raise ValueError("Indução Nominal (de Perdas) inválida.")
            
            peso_nucleo_ton = safe_float(resultados_perdas_vazio_local.get("peso_nucleo"))
            if peso_nucleo_ton is None or peso_nucleo_ton <= 0: raise ValueError("Peso do Núcleo (de Perdas) inválido.")
            
            peso_nucleo_kg = peso_nucleo_ton * 1000.0
            un_ref_at = tensao_at / math.sqrt(3) if tipo_transformador == "Trifásico" else tensao_at
            if un_ref_at == 0: raise ValueError("Un_ref_at (Tensão de referência AT) não pode ser zero.")


            frequencias_tabela = [100, 120, 150, 180, 200, 240]
            table_data = []

            for freq_teste_tabela in frequencias_tabela:
                fp_fn_tabela = freq_teste_tabela / freq_nominal
                up_un_tabela = tensao_prova / un_ref_at if un_ref_at != 0 else 0
                
                beta_teste_tabela = inducao_nominal * (up_un_tabela / fp_fn_tabela) if fp_fn_tabela != 0 else 0
                beta_teste_tabela = min(max(beta_teste_tabela, 0.01), 1.9)

                fpm_tabela = buscar_valores_tabela(beta_teste_tabela, freq_teste_tabela, df_potencia_magnet)
                fp_tabela = buscar_valores_tabela(beta_teste_tabela, freq_teste_tabela, df_perdas_nucleo)

                pa_tabela = fp_tabela * peso_nucleo_kg / 1000.0
                pm_tabela = fpm_tabela * peso_nucleo_kg / 1000.0
                
                row_entry = {"frequencia": freq_teste_tabela, "pot_ativa": pa_tabela, "pot_magnetica": pm_tabela}

                if tipo_transformador == "Monofásico":
                    pi_tabela = math.sqrt(max(0, pm_tabela**2 - pa_tabela**2))
                    tensao_bt_float = float(tensao_bt) if tensao_bt is not None else 0.0
                    up_un_tabela_float = float(up_un_tabela) if up_un_tabela is not None else 0.0
                    u_calc_scap_tabela = tensao_prova - (up_un_tabela_float * tensao_bt_float)
                    pcap_tabela = -(((u_calc_scap_tabela * 1000)**2 * 2 * math.pi * freq_teste_tabela * capacitancia * 1e-12) / 3) / 1000
                    scap_sind_ratio_tabela = abs(pcap_tabela) / pi_tabela if pi_tabela > 1e-9 else float('inf')
                    row_entry.update({"pot_induzida": pi_tabela, "pcap": pcap_tabela, "scap_sind_ratio": scap_sind_ratio_tabela})
                else: 
                    u_calc_scap_tabela = tensao_prova 
                    pcap_tabela = -((u_calc_scap_tabela * 1000)**2 * 2 * math.pi * freq_teste_tabela * capacitancia * 1e-12) / 1000 
                    row_entry.update({"pcap": pcap_tabela})
                table_data.append(row_entry)
            
            header_style = {"backgroundColor": APP_COLORS.get("background_card_header", "#1f1f1f"), "color": APP_COLORS.get("text_header", "#FFFFFF"), "textAlign": "center"}
            
            if tipo_transformador == "Monofásico":
                table_header_items = ["Frequência (Hz)", "Pw (kW)", "Sm (kVA)", "Sind (kVAr ind)", "Scap (kVAr cap)", "Scap/Sind"]
            else:
                table_header_items = ["Frequência (Hz)", "Pw (kW)", "Sm (kVA)", "Scap (kVAr cap)"]
            
            table_header_html = [html.Thead(html.Tr([html.Th(col, style=header_style) for col in table_header_items]))]
            table_rows_html = []
            for row in table_data:
                if tipo_transformador == "Monofásico":
                    table_rows_html.append(html.Tr([
                        html.Td(f"{row['frequencia']:.0f}", style={"textAlign": "center"}),
                        html.Td(format_parameter_value(row["pot_ativa"], 2), style={"textAlign": "center"}),
                        html.Td(format_parameter_value(row["pot_magnetica"], 2), style={"textAlign": "center"}),
                        html.Td(format_parameter_value(row["pot_induzida"], 2), style={"textAlign": "center"}),
                        html.Td(format_parameter_value(abs(row["pcap"]), 2), style={"textAlign": "center", "color": APP_COLORS.get("danger", "red")}),
                        html.Td(format_parameter_value(row["scap_sind_ratio"], 2), style={"textAlign": "center", "fontWeight": "bold"}),
                    ]))
                else:
                     table_rows_html.append(html.Tr([
                        html.Td(f"{row['frequencia']:.0f}", style={"textAlign": "center"}),
                        html.Td(format_parameter_value(row["pot_ativa"], 2), style={"textAlign": "center"}),
                        html.Td(format_parameter_value(row["pot_magnetica"], 2), style={"textAlign": "center"}),
                        html.Td(format_parameter_value(abs(row["pcap"]), 2), style={"textAlign": "center", "color": APP_COLORS.get("danger", "red")}),
                    ]))
            table_body_html = [html.Tbody(table_rows_html)]
            table = dbc.Table(table_header_html + table_body_html, bordered=True, hover=True, responsive=True, striped=True, className="mt-3 table-dark")

            frequencias_plot = [row["frequencia"] for row in table_data]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=frequencias_plot, y=[row["pot_ativa"] for row in table_data], name="Potência Ativa (kW)", line=dict(color=APP_COLORS.get("danger","red"))))
            fig.add_trace(go.Scatter(x=frequencias_plot, y=[row["pot_magnetica"] for row in table_data], name="Potência Magnética (kVA)", line=dict(color=APP_COLORS.get("primary","blue"))))
            if tipo_transformador == "Monofásico":
                 fig.add_trace(go.Scatter(x=frequencias_plot, y=[row["pot_induzida"] for row in table_data], name="Potência Indutiva (kVAr ind)", line=dict(color=APP_COLORS.get("accent_alt","yellow"))))
            fig.add_trace(go.Scatter(x=frequencias_plot, y=[abs(row["pcap"]) for row in table_data], name="Potência Capacitiva (kVAr cap)", line=dict(color=APP_COLORS.get("success","green"))))
            fig.update_layout(title="Potências vs. Frequência", template="plotly_dark", height=300, paper_bgcolor=APP_COLORS.get("background_card", "#2c2c2c"), plot_bgcolor=APP_COLORS.get("background_card", "#2c2c2c"), font_color=APP_COLORS.get("text_light", "#e0e0e0"))
            
            return html.Div([
                html.H5("Tabela de Resultados para Diferentes Frequências", className="text-center mt-4 mb-3"),
                dbc.Row([dbc.Col(table, md=6), dbc.Col(dcc.Graph(figure=fig), md=6)])
            ])

        except ValueError as ve: # Catch specific ValueErrors from safe_float or checks
            log.warning(f"[Induced Voltage Table] Erro de valor: {ve}")
            return html.Div(f"Erro ao gerar tabela: {str(ve)}. Verifique os dados de entrada e do cálculo principal.", className="alert alert-warning")
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            log.error(f"Erro ao gerar tabela de frequências: {e}\n{error_traceback}")
            return html.Div(f"Erro inesperado ao gerar tabela: {str(e)}", className="alert alert-danger")

    log.debug("Callbacks de Tensão Induzida registrados com sucesso")

# --- Fim do registro ---
