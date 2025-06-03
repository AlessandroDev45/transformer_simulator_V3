# callbacks/temperature_rise.py
""" Callbacks para a seção de Elevação de Temperatura. """
import dash
import numpy as np
from dash import dcc, html, Input, Output, State, callback, callback_context, no_update
from utils.elec import safe_float
import dash_bootstrap_components as dbc
import math
import logging
import datetime
from dash.exceptions import PreventUpdate

# Importações da aplicação
from app import app
from utils import constants # Para constantes de material
from utils.routes import normalize_pathname, ROUTE_TEMPERATURE_RISE # Para normalização de pathname
# <<< IMPORTANTE: Verifique a assinatura e unidades esperadas destas funções >>>
from app_core.calculations import (
    calculate_winding_temps,
    calculate_top_oil_rise,
    calculate_thermal_time_constant # Assume que espera pesos em KG
)
from formulas.thermal_math import calculate_thermal_time_constant
# <<< FIM IMPORTANTE >>>
from components.validators import validate_dict_inputs # Para validação
from components.transformer_info_template import create_transformer_info_panel
from components.formatters import formatar_elevacao_temperatura, format_parameter_value # Formatadores

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Remove: from config import colors # Para estilos
COLORS = {
    "warning": "#ffc107",
    "fail": "#dc3545",
}

# --- Função de Registro de Callbacks ---
def register_temperature_rise_callbacks(app_instance):
    """
    Função de registro explícito para callbacks de temperature_rise.
    Esta função é chamada por app.py durante a inicialização.

    Registra os callbacks que foram convertidos para o padrão de registro centralizado.
    """
    log.info(f"Registrando callbacks do módulo temperature_rise para app {app_instance.title}...")

    # --- Callback para exibir informações do transformador na página ---
    @app_instance.callback(
        Output("transformer-info-temperature-rise-page", "children"),
        Input("transformer-info-temperature-rise", "children"),
        prevent_initial_call=False
    )
    def update_temperature_rise_page_info_panel(global_panel_content):
        """Copia o conteúdo do painel global para o painel específico da página."""
        log.info("CALLBACK EXECUTADO: Atualizando painel de informações do transformador na página de elevação de temperatura")
        print("CALLBACK EXECUTADO: Atualizando painel de informações do transformador na página de elevação de temperatura")

        # Verificar se o conteúdo do painel global é válido
        if global_panel_content is None:
            log.warning("Conteúdo do painel global é None")
            from components.transformer_info_template import create_transformer_info_panel
            return create_transformer_info_panel({})

        return global_panel_content

    # Callback para CARREGAR dados (RESTAURADO com triggers corretos)
    @app_instance.callback(
        [
            Output("temp-amb", "value"),
            Output("winding-material", "value"),
            Output("res-cold", "value"),
            Output("temp-cold", "value"),
            Output("res-hot", "value"),
            Output("temp-top-oil", "value"),
            Output("delta-theta-oil-max", "value"),
            Output("avg-winding-temp", "value"),
            Output("avg-winding-rise", "value"),
            Output("top-oil-rise", "value"),
            Output("ptot-used", "value"),
            Output("tau0-result", "value"),
            Output("temp-rise-error-message", "children")
        ],
        [
            Input("url", "pathname"),                    # <<< Trigger pela URL
            Input("transformer-inputs-store", "data"),   # <<< Trigger pelos Dados Básicos
            Input("temperature-rise-store", "data"),     # <<< Trigger pelo store local
            Input("losses-store", "data")                # <<< Trigger pelos dados de perdas
        ],
        prevent_initial_call=False # <<< Permite rodar na carga inicial
    )
    def temperature_rise_load_data(pathname, transformer_data, stored_temp_rise_data, losses_data):
        """
        Carrega os dados da aba Elevação de Temperatura para a UI.
        - Prioriza 'elevacao_oleo_topo' do transformer-inputs-store.
        - Carrega outros inputs e resultados do temperature-rise-store.
        """
        triggered_id = callback_context.triggered_id
        log.debug(f"[LOAD TempRise] Callback triggered by: {triggered_id}")

        normalized_path = normalize_pathname(pathname)
        # Só executa a lógica principal se o trigger for a URL E estiver na página correta,
        # OU se o trigger for a atualização do store global (para pegar delta_theta)
        # OU se o trigger for o store local (para carregar dados salvos)
        # OU se o trigger for o store de perdas (para atualizar cálculos)
        should_process = False

        # Caso 1: Estamos na página correta (independente do trigger)
        if normalized_path == ROUTE_TEMPERATURE_RISE:
            should_process = True
            log.info(f"[LOAD TempRise] Estamos na página de Elevação de Temperatura. Processando.")
        # Caso 2: Trigger é o store global (para pegar delta_theta)
        elif triggered_id == "transformer-inputs-store":
            should_process = True
            log.info(f"[LOAD TempRise] Processando atualização de transformer-inputs-store.")
        # Caso 3: Trigger é o store de perdas
        elif triggered_id == "losses-store":
            should_process = True
            log.info(f"[LOAD TempRise] Processando atualização de losses-store.")
        # Caso 4: Estamos em outra página e o trigger é a URL
        elif triggered_id == "url" and normalized_path != ROUTE_TEMPERATURE_RISE:
            log.debug(f"[LOAD TempRise] Pathname '{pathname}' não é '{ROUTE_TEMPERATURE_RISE}'. Abortando trigger de URL.")
            raise PreventUpdate
        # Caso 5: Outros triggers não relevantes
        else:
            log.debug(f"[LOAD TempRise] Trigger não relevante ({triggered_id}). Abortando.")
            raise PreventUpdate

        if not should_process: # Segurança extra
            raise PreventUpdate

        # Lê dados dos stores, tratando None/inválido
        local_data = stored_temp_rise_data if stored_temp_rise_data and isinstance(stored_temp_rise_data, dict) else {}
        global_data = transformer_data if transformer_data and isinstance(transformer_data, dict) else {}
        losses_data = losses_data if losses_data and isinstance(losses_data, dict) else {}

        # Verificar se os dados do transformador estão aninhados em transformer_data
        if "transformer_data" in global_data and isinstance(global_data["transformer_data"], dict):
            # Usar os dados aninhados
            transformer_dict = global_data["transformer_data"]
            log.debug(f"[LOAD TempRise] Usando dados aninhados em transformer_data")
        else:
            # Usar os dados diretamente
            transformer_dict = global_data
            log.debug(f"[LOAD TempRise] Usando dados diretamente do dicionário principal")

        inputs_local = local_data.get('inputs_temp_rise', {})
        results_local = local_data.get('resultados_temp_rise', {})

        # Verificar se os dados estão diretamente no dicionário principal
        log.debug(f"[LOAD TempRise] Verificando dados diretamente no dicionário principal: {list(local_data.keys())}")

        # Verificar inputs diretamente no dicionário principal
        if "input_ta" in local_data and not inputs_local.get("input_ta"):
            inputs_local["input_ta"] = local_data.get("input_ta")
            log.debug(f"[LOAD TempRise] Valor encontrado diretamente no dicionário principal: input_ta={inputs_local['input_ta']}")

        if "input_material" in local_data and not inputs_local.get("input_material"):
            inputs_local["input_material"] = local_data.get("input_material")
            log.debug(f"[LOAD TempRise] Valor encontrado diretamente no dicionário principal: input_material={inputs_local['input_material']}")

        if "input_rc" in local_data and not inputs_local.get("input_rc"):
            inputs_local["input_rc"] = local_data.get("input_rc")
            log.debug(f"[LOAD TempRise] Valor encontrado diretamente no dicionário principal: input_rc={inputs_local['input_rc']}")

        if "input_tc" in local_data and not inputs_local.get("input_tc"):
            inputs_local["input_tc"] = local_data.get("input_tc")
            log.debug(f"[LOAD TempRise] Valor encontrado diretamente no dicionário principal: input_tc={inputs_local['input_tc']}")

        if "input_rw" in local_data and not inputs_local.get("input_rw"):
            inputs_local["input_rw"] = local_data.get("input_rw")
            log.debug(f"[LOAD TempRise] Valor encontrado diretamente no dicionário principal: input_rw={inputs_local['input_rw']}")

        if "input_t_oil" in local_data and not inputs_local.get("input_t_oil"):
            inputs_local["input_t_oil"] = local_data.get("input_t_oil")
            log.debug(f"[LOAD TempRise] Valor encontrado diretamente no dicionário principal: input_t_oil={inputs_local['input_t_oil']}")

        if "input_delta_theta_oil_max" in local_data and not inputs_local.get("input_delta_theta_oil_max"):
            inputs_local["input_delta_theta_oil_max"] = local_data.get("input_delta_theta_oil_max")
            log.debug(f"[LOAD TempRise] Valor encontrado diretamente no dicionário principal: input_delta_theta_oil_max={inputs_local['input_delta_theta_oil_max']}")

        # Verificar resultados diretamente no dicionário principal
        if "avg_winding_temp" in local_data and not results_local.get("avg_winding_temp"):
            results_local["avg_winding_temp"] = local_data.get("avg_winding_temp")
            log.debug(f"[LOAD TempRise] Valor encontrado diretamente no dicionário principal: avg_winding_temp={results_local['avg_winding_temp']}")

        if "avg_winding_rise" in local_data and not results_local.get("avg_winding_rise"):
            results_local["avg_winding_rise"] = local_data.get("avg_winding_rise")
            log.debug(f"[LOAD TempRise] Valor encontrado diretamente no dicionário principal: avg_winding_rise={results_local['avg_winding_rise']}")

        if "top_oil_rise" in local_data and not results_local.get("top_oil_rise"):
            results_local["top_oil_rise"] = local_data.get("top_oil_rise")
            log.debug(f"[LOAD TempRise] Valor encontrado diretamente no dicionário principal: top_oil_rise={results_local['top_oil_rise']}")

        if "ptot_used_kw" in local_data and not results_local.get("ptot_used_kw"):
            results_local["ptot_used_kw"] = local_data.get("ptot_used_kw")
            log.debug(f"[LOAD TempRise] Valor encontrado diretamente no dicionário principal: ptot_used_kw={results_local['ptot_used_kw']}")

        if "tau0_h" in local_data and not results_local.get("tau0_h"):
            results_local["tau0_h"] = local_data.get("tau0_h")
            log.debug(f"[LOAD TempRise] Valor encontrado diretamente no dicionário principal: tau0_h={results_local['tau0_h']}")

        if "message" in local_data and not results_local.get("message"):
            results_local["message"] = local_data.get("message")
            log.debug(f"[LOAD TempRise] Valor encontrado diretamente no dicionário principal: message={results_local['message']}")

        log.debug(f"[LOAD TempRise] Dados lidos do local store: Inputs={inputs_local}, Resultados={results_local}")
        log.debug(f"[LOAD TempRise] Dados lidos do global store: {global_data}")

        # Determina delta_theta_oil_max (prioridade global)
        delta_theta_oil_max_final = None
        delta_theta_oil_max_global_raw = transformer_dict.get('elevacao_oleo_topo')
        if delta_theta_oil_max_global_raw is not None:
            delta_theta_oil_max_final = safe_float(delta_theta_oil_max_global_raw)
            if delta_theta_oil_max_final is None:
                log.debug(f"[LOAD TempRise] Falha ao converter 'elevacao_oleo_topo' ({delta_theta_oil_max_global_raw}). Fallback para local.")
                delta_theta_oil_max_final = inputs_local.get('input_delta_theta_oil_max') # Já deve ser float
        else:
            delta_theta_oil_max_final = inputs_local.get('input_delta_theta_oil_max')

        # Se ainda for None, usar um valor padrão
        if delta_theta_oil_max_final is None:
            delta_theta_oil_max_final = 55.0  # Valor padrão para classe A
            log.debug(f"[LOAD TempRise] Usando valor padrão para delta_theta_oil_max: {delta_theta_oil_max_final}")

        # Tenta carregar a mensagem salva
        message_str = results_local.get('message', "")
        display_message = ""
        if message_str:
            is_warning = "Aviso" in message_str
            display_message = html.Div(message_str,
                                        style={"color": COLORS.get('warning', 'orange') if is_warning else COLORS.get('fail', 'red'),
                                               "fontSize": "0.7rem"})

        # Retorna valores para UI
        values_to_return = (
            inputs_local.get('input_ta'), inputs_local.get('input_material', 'cobre'),
            inputs_local.get('input_rc'), inputs_local.get('input_tc'),
            inputs_local.get('input_rw'), inputs_local.get('input_t_oil'),
            delta_theta_oil_max_final, # Valor numérico
            results_local.get('avg_winding_temp'), results_local.get('avg_winding_rise'),
            results_local.get('top_oil_rise'), results_local.get('ptot_used_kw'),
            results_local.get('tau0_h'), display_message
        )

        log.debug(f"[LOAD TempRise] Valores finais retornados para UI: {values_to_return}")
        return values_to_return

    # Callback principal para cálculo (RESTAURADO e CORRIGIDO)
    @app_instance.callback(
        [
            Output("avg-winding-temp", "value", allow_duplicate=True),
            Output("avg-winding-rise", "value", allow_duplicate=True),
            Output("top-oil-rise", "value", allow_duplicate=True),
            Output("ptot-used", "value", allow_duplicate=True),
            Output("tau0-result", "value", allow_duplicate=True),
            Output("temp-rise-error-message", "children", allow_duplicate=True),
            Output("temperature-rise-store", "data", allow_duplicate=True)
        ],
        [
            Input("calc-temp-rise-btn", "n_clicks"),  # Trigger: Botão Calcular
            Input("limpar-temp-rise", "n_clicks")     # Trigger: Botão Limpar (agora também calcula)
        ],
        [
            State("winding-material", "value"),
            State("res-cold", "value"),
            State("temp-cold", "value"),
            State("res-hot", "value"),
            State("temp-top-oil", "value"),
            State("delta-theta-oil-max", "value"),
            State("transformer-inputs-store", "data"),
            State("losses-store", "data"),
            State("temperature-rise-store", "data"),
            State("url", "pathname") # Adicionado pathname para verificação
        ],
        prevent_initial_call=True
    )
    def temperature_rise_calculate(
        calc_clicks, limpar_clicks, winding_material, res_cold_str, temp_cold_str, res_hot_str, temp_top_oil_str, delta_theta_oil_max_str, # Inputs locais
        transformer_data, losses_data, current_store_data, pathname): # Dados globais e pathname
        """
        Calcula elevação de temperatura, Ptot usada e τ₀.
        Busca dados globais, realiza cálculos e salva inputs/resultados no store local.
        Responde a ambos os botões: Calcular e Limpar (que agora também calcula).
        """
        # Verificar se estamos na página correta
        if pathname != "/elevacao-temperatura":
            log.info(f"Ignorando callback temperature_rise_calculate em página diferente: {pathname}")
            raise PreventUpdate

        # Identificar qual botão foi clicado
        triggered_id = callback_context.triggered_id
        if triggered_id == "calc-temp-rise-btn" and (calc_clicks is None or calc_clicks <= 0):
            raise PreventUpdate
        if triggered_id == "limpar-temp-rise" and (limpar_clicks is None or limpar_clicks <= 0):
            raise PreventUpdate

        # Se nenhum botão foi clicado (improvável, mas por segurança)
        if triggered_id not in ["calc-temp-rise-btn", "limpar-temp-rise"]:
            log.warning(f"[CALC TempRise] Trigger inesperado: {triggered_id}")
            raise PreventUpdate

        # Determinar qual botão foi clicado para logging
        button_name = "Calcular" if triggered_id == "calc-temp-rise-btn" else "Limpar"
        n_clicks = calc_clicks if triggered_id == "calc-temp-rise-btn" else limpar_clicks

        log.info(f"[CALC TempRise] Callback iniciado - Botão {button_name}, Trigger: {triggered_id}")

        # --- 1. Validar e converter inputs locais ---
        input_values_local = {
            'input_ta': safe_float(25.0),
            'input_material': winding_material or 'cobre',
            'input_rc': safe_float(res_cold_str),
            'input_tc': safe_float(temp_cold_str),
            'input_rw': safe_float(res_hot_str),
            'input_t_oil': safe_float(temp_top_oil_str),
            'input_delta_theta_oil_max': safe_float(delta_theta_oil_max_str, 55.0)
        }

        # --- 2. Obter dados do transformador ---
        # Verificar se os dados do transformador estão aninhados em transformer_data
        transformer_dict = {}
        if transformer_data and isinstance(transformer_data, dict):
            if "transformer_data" in transformer_data and isinstance(transformer_data["transformer_data"], dict):
                # Usar os dados aninhados
                transformer_dict = transformer_data["transformer_data"]
                log.debug(f"[CALC TempRise] Usando dados aninhados em transformer_data")
            else:
                # Usar os dados diretamente
                transformer_dict = transformer_data
                log.debug(f"[CALC TempRise] Usando dados diretamente do dicionário principal")

        # --- 3. Obter dados de perdas ---
        losses_dict = {}
        if losses_data and isinstance(losses_data, dict):
            if "resultados_perdas_vazio" in losses_data and isinstance(losses_data["resultados_perdas_vazio"], dict):
                # Usar os dados aninhados
                losses_dict = losses_data
                log.debug(f"[CALC TempRise] Usando dados de perdas aninhados")
            else:
                # Usar os dados diretamente
                losses_dict = losses_data
                log.debug(f"[CALC TempRise] Usando dados de perdas diretamente do dicionário principal")

        # --- 4. Extrair valores necessários ---
        # Dados do transformador
        potencia_mva = safe_float(transformer_dict.get('potencia_mva'))
        peso_nucleo_kg = safe_float(transformer_dict.get('peso_nucleo_kg'))
        peso_oleo_kg = safe_float(transformer_dict.get('peso_oleo_kg'))
        peso_tanque_kg = safe_float(transformer_dict.get('peso_tanque_kg'))
        peso_enrol_at_kg = safe_float(transformer_dict.get('peso_enrol_at_kg'))
        peso_enrol_bt_kg = safe_float(transformer_dict.get('peso_enrol_bt_kg'))
        peso_enrol_ter_kg = safe_float(transformer_dict.get('peso_enrol_ter_kg', 0))  # Terciário pode não existir

        # Dados de perdas
        perdas_vazio_kw = None
        perdas_totais_kw = None

        # Tentar obter perdas do dicionário de resultados
        if "resultados_perdas_vazio" in losses_dict:
            perdas_vazio_kw = safe_float(losses_dict["resultados_perdas_vazio"].get("perdas_vazio_kw"))

        # Se não encontrou, tentar diretamente no dicionário principal
        if perdas_vazio_kw is None:
            perdas_vazio_kw = safe_float(losses_dict.get("perdas_vazio_kw"))

        # Tentar obter perdas totais do dicionário de resultados
        if "resultados_perdas_totais" in losses_dict:
            perdas_totais_kw = safe_float(losses_dict["resultados_perdas_totais"].get("perdas_totais_kw"))

        # Se não encontrou, tentar diretamente no dicionário principal
        if perdas_totais_kw is None:
            perdas_totais_kw = safe_float(losses_dict.get("perdas_totais_kw"))

        # Se ainda não encontrou, tentar calcular a partir de perdas em carga + perdas em vazio
        if perdas_totais_kw is None:
            perdas_carga_kw = None
            if "resultados_perdas_carga" in losses_dict:
                perdas_carga_kw = safe_float(losses_dict["resultados_perdas_carga"].get("perdas_carga_kw"))
            if perdas_carga_kw is None:
                perdas_carga_kw = safe_float(losses_dict.get("perdas_carga_kw"))

            if perdas_carga_kw is not None and perdas_vazio_kw is not None:
                perdas_totais_kw = perdas_carga_kw + perdas_vazio_kw

        # --- 5. Validar dados necessários ---
        missing_data = []
        if potencia_mva is None:
            missing_data.append("potência (MVA)")
        if perdas_vazio_kw is None:
            missing_data.append("perdas em vazio (kW)")
        if perdas_totais_kw is None:
            missing_data.append("perdas totais (kW)")

        # Verificar pesos (pelo menos um deve estar presente)
        pesos_presentes = [p for p in [peso_nucleo_kg, peso_oleo_kg, peso_tanque_kg,
                                      peso_enrol_at_kg, peso_enrol_bt_kg, peso_enrol_ter_kg]
                          if p is not None]
        if not pesos_presentes:
            missing_data.append("pesos dos componentes (kg)")

        # Verificar inputs locais necessários
        if input_values_local['input_rc'] is None:
            missing_data.append("resistência a frio (Ω)")
        if input_values_local['input_tc'] is None:
            missing_data.append("temperatura a frio (°C)")
        if input_values_local['input_rw'] is None:
            missing_data.append("resistência a quente (Ω)")

        # Se faltam dados, exibir mensagem de erro
        if missing_data:
            error_msg = f"Dados necessários ausentes: {', '.join(missing_data)}."
            log.warning(f"[CALC TempRise] {error_msg}")

            # Preparar mensagem para UI
            display_message = html.Div(error_msg, style={"color": COLORS.get('fail', 'red'), "fontSize": "0.7rem"})

            # Atualizar o store com os inputs, mas sem resultados
            new_store_data = current_store_data.copy() if current_store_data else {}
            new_store_data['inputs_temp_rise'] = input_values_local
            new_store_data['message'] = error_msg

            return no_update, no_update, no_update, no_update, no_update, display_message, new_store_data

        # --- 6. Realizar cálculos ---
        try:
            log.info(f"[CALC TempRise] Iniciando cálculos com dados: P={potencia_mva}MVA, P0={perdas_vazio_kw}kW, Ptot={perdas_totais_kw}kW")

            # Calcular temperatura média do enrolamento
            avg_winding_temp, avg_winding_rise = calculate_winding_temps(
                input_values_local['input_rc'],
                input_values_local['input_tc'],
                input_values_local['input_rw'],
                input_values_local['input_ta'],
                input_values_local['input_material']
            )

            # Calcular elevação de temperatura do óleo
            if input_values_local['input_t_oil'] is not None and input_values_local['input_ta'] is not None:
                top_oil_rise = calculate_top_oil_rise(
                    t_oil=input_values_local['input_t_oil'],
                    ta=input_values_local['input_ta']
                )
            else:
                top_oil_rise = None

            # Definir peso_total_kg antes de usá-lo
            peso_total_kg = sum(
                p for p in [peso_nucleo_kg, peso_oleo_kg, peso_tanque_kg,
                            peso_enrol_at_kg, peso_enrol_bt_kg, peso_enrol_ter_kg]
                if p is not None
            )

            # Validar e definir valores padrão para os argumentos
            perdas_totais_kw = perdas_totais_kw or 0.0
            peso_oleo_kg = peso_oleo_kg or 0.0
            peso_total_kg = peso_total_kg or 0.0
            delta_theta_oil_max = input_values_local.get('input_delta_theta_oil_max', 0.0)

            # Calcular constante de tempo térmica
            tau0_h = calculate_thermal_time_constant(
                ptot=perdas_totais_kw,
                delta_max=delta_theta_oil_max,
                mt=peso_total_kg,
                mo=peso_oleo_kg
            )

            # --- 7. Preparar resultados ---
            results = {
                'avg_winding_temp': avg_winding_temp,
                'avg_winding_rise': avg_winding_rise,
                'top_oil_rise': top_oil_rise,
                'ptot_used_kw': perdas_totais_kw,
                'tau0_h': tau0_h
            }

            # Formatar para exibição
            display_avg_winding_temp = f"{avg_winding_temp:.1f}" if avg_winding_temp is not None else ""
            display_avg_winding_rise = f"{avg_winding_rise:.1f}" if avg_winding_rise is not None else ""
            display_top_oil_rise = f"{top_oil_rise:.1f}" if top_oil_rise is not None else ""
            display_ptot_used = f"{perdas_totais_kw:.1f}" if perdas_totais_kw is not None else ""
            display_tau0 = f"{tau0_h:.1f}" if tau0_h is not None else ""

            # --- 8. Atualizar o store ---
            new_store_data = current_store_data.copy() if current_store_data else {}
            new_store_data['inputs_temp_rise'] = input_values_local
            new_store_data['resultados_temp_rise'] = results
            new_store_data['timestamp'] = datetime.datetime.now().isoformat()

            # Remover mensagem de erro se existir
            if 'message' in new_store_data:
                del new_store_data['message']

            log.info(f"[CALC TempRise] Cálculos concluídos: Tw={avg_winding_temp:.1f}°C, ΔTw={avg_winding_rise:.1f}°C, ΔToil={top_oil_rise:.1f}°C, τ0={tau0_h:.1f}h")

            return (
                display_avg_winding_temp,
                display_avg_winding_rise,
                display_top_oil_rise,
                display_ptot_used,
                display_tau0,
                "",  # Sem mensagem de erro
                new_store_data
            )

        except Exception as e:
            log.exception(f"[CALC TempRise] Erro nos cálculos: {e}")
            error_msg = f"Erro nos cálculos: {str(e)}"
            display_message = html.Div(error_msg, style={"color": COLORS.get('fail', 'red'), "fontSize": "0.7rem"})

            # Atualizar o store com os inputs, mas sem resultados
            new_store_data = current_store_data.copy() if current_store_data else {}
            new_store_data['inputs_temp_rise'] = input_values_local
            new_store_data['message'] = error_msg

            return no_update, no_update, no_update, no_update, no_update, display_message, new_store_data

    # Refactored callback to ensure `temp-amb.value` is updated by only one callback.
    @app_instance.callback(
        Output("temp-amb", "value"),
        Input("transformer-inputs-store", "data"),
        prevent_initial_call=False
    )
    def update_temp_amb(transformer_data):
        """Atualiza o valor de temperatura ambiente."""
        log.info("CALLBACK EXECUTADO: Atualizando temperatura ambiente")
        temp_amb_value = transformer_data.get("ambient_temperature", None)

        # Se necessário, adicione lógica adicional para determinar o valor de temp_amb

        return temp_amb_value

    # Retorna a função de registro para indicar que foi concluída com sucesso
    log.info("Callbacks do módulo temperature_rise registrados com sucesso.")
    return True

# Updated DashWithMCP class to allow dynamic assignment of mcp.
from typing import Optional, Protocol

# Introduced MCPInterface to define the expected methods for mcp.
class MCPInterface(Protocol):
    def get_data(self, store_name: str) -> dict:
        ...

# Refactored to use a wrapper class for Dash to include the mcp attribute.
from app_core.transformer_mcp_enhanced import DashWithMCP, MCPInterface

# Import Dash to resolve missing definition
from dash import Dash

# Ensure proper type definition for `mcp`
if isinstance(app, Dash):
    app = DashWithMCP(__name__)
    app.mcp = MCPInterface()  # Inicializar com a interface correta

# Replace app instance with the extended class
if isinstance(app, Dash):
    app = DashWithMCP(__name__)

# Fallback mechanism for MCP
if app.mcp is None:
    log.warning("O atributo 'mcp' não está disponível. Usando fallback.")

    class MCPFallback(MCPInterface):
        def get_data(self, store_name: str) -> dict:
            log.warning(f"Tentativa de acessar '{store_name}' no fallback MCP.")
            return {}

    app.mcp = MCPFallback()

# Adicionar leitura de dados com app.mcp.get_data
data = app.mcp.get_data("temperature-rise-store")

# Adicionar gravação de dados com patch_mcp
from utils.mcp_utils import patch_mcp
patch_mcp("temperature-rise-store", data, app)

# Adicionar proteção de execução
if __name__ == "__main__":
    app.run_server(debug=True)
