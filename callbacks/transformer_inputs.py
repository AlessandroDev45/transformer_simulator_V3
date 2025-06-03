# callbacks/transformer_inputs.py
"""
Módulo transformer_inputs que usa o padrão de registro centralizado.
"""
import logging

from dash import Input, Output, State, html, no_update, dcc # Adicionado State e dcc

# Não importar app diretamente para evitar importações circulares
from dash.exceptions import PreventUpdate
from utils.store_diagnostics import convert_numpy_types
from utils.routes import ROUTE_HOME, normalize_pathname # Import route constant and normalizer

log = logging.getLogger(__name__)
log.info("============ MÓDULO TRANSFORMER_INPUTS CARREGADO ============")
log.info(f"Nível de log: {logging.getLevelName(log.getEffectiveLevel())}")
log.info(f"Handlers configurados: {[h.__class__.__name__ for h in log.handlers]}")
log.info("=============================================================")

def register_transformer_inputs_callbacks(app_instance):
    """
    Função de registro explícito para callbacks de transformer_inputs.
    Esta função é chamada por app.py durante a inicialização.
    """
    log.info(f"Registrando callbacks do módulo transformer_inputs para app {app_instance.title}...")

    @app_instance.callback(
        [
            Output("corrente_nominal_at", "value"),
            Output("corrente_nominal_bt", "value"),
            Output("corrente_nominal_terciario", "value"),
            Output("corrente_nominal_at_tap_maior", "value"),
            Output("corrente_nominal_at_tap_menor", "value"),
        ],
        [
            Input("potencia_mva", "value"), Input("frequencia", "value"),
            Input("grupo_ligacao", "value"), Input("liquido_isolante", "value"),
            Input("elevacao_oleo_topo", "value"), Input("elevacao_enrol", "value"),
            Input("tipo_transformador", "value"), Input("tipo_isolamento", "value"),
            Input("norma_iso", "value"), Input("peso_total", "value"),
            Input("peso_parte_ativa", "value"), Input("peso_oleo", "value"),
            Input("peso_tanque_acessorios", "value"), Input("tensao_at", "value"),
            Input("classe_tensao_at", "value"), Input("impedancia", "value"),
            Input("nbi_at", "value"), Input("sil_at", "value"), Input("conexao_at", "value"),
            Input("classe_tensao_neutro_at", "value"), Input("nbi_neutro_at", "value"), # Changed tensao_bucha_neutro_at to classe_tensao_neutro_at
            Input("sil_neutro_at", "value"), Input("tensao_at_tap_maior", "value"),
            Input("impedancia_tap_maior", "value"), Input("tensao_at_tap_menor", "value"),
            Input("impedancia_tap_menor", "value"), Input("teste_tensao_aplicada_at", "value"),
            Input("teste_tensao_induzida_at", "value"), Input("tensao_bt", "value"),
            Input("classe_tensao_bt", "value"), Input("nbi_bt", "value"),
            Input("sil_bt", "value"), Input("conexao_bt", "value"),
            Input("classe_tensao_neutro_bt", "value"), Input("nbi_neutro_bt", "value"), # Changed tensao_bucha_neutro_bt to classe_tensao_neutro_bt
            Input("sil_neutro_bt", "value"), Input("teste_tensao_aplicada_bt", "value"),
            Input("tensao_terciario", "value"), Input("classe_tensao_terciario", "value"),
            Input("nbi_terciario", "value"), Input("sil_terciario", "value"),
            Input("conexao_terciario", "value"), Input("classe_tensao_neutro_terciario", "value"), # Changed tensao_bucha_neutro_terciario to classe_tensao_neutro_terciario
            Input("nbi_neutro_terciario", "value"), Input("sil_neutro_terciario", "value"),
            Input("teste_tensao_aplicada_terciario", "value"),
        ],
        prevent_initial_call=False, priority=1000,
    )
    def update_transformer_calculations_and_mcp(
        potencia_mva, frequencia, grupo_ligacao, liquido_isolante, elevacao_oleo_topo,
        elevacao_enrol, tipo_transformador, tipo_isolamento, norma_iso, peso_total,
        peso_parte_ativa, peso_oleo, peso_tanque_acessorios, tensao_at, classe_tensao_at,
        impedancia, nbi_at, sil_at, conexao_at, classe_tensao_neutro_at, nbi_neutro_at, # Changed param name
        sil_neutro_at, tensao_at_tap_maior, impedancia_tap_maior, tensao_at_tap_menor,
        impedancia_tap_menor, teste_tensao_aplicada_at, teste_tensao_induzida_at,
        tensao_bt, classe_tensao_bt, nbi_bt, sil_bt, conexao_bt, classe_tensao_neutro_bt, # Changed param name
        nbi_neutro_bt, sil_neutro_bt, teste_tensao_aplicada_bt, tensao_terciario,
        classe_tensao_terciario, nbi_terciario, sil_terciario, conexao_terciario,
        classe_tensao_neutro_terciario, nbi_neutro_terciario, sil_neutro_terciario, # Changed param name
        teste_tensao_aplicada_terciario
    ):
        from dash import ctx
        log.debug(f"[UpdateTransformerCalc] Acionado por: {ctx.triggered_id if ctx.triggered else 'Inicial'}")

        corrente_at, corrente_bt, corrente_terciario = None, None, None
        corrente_at_tap_maior, corrente_at_tap_menor = None, None

        try:
            transformer_data_for_currents = {
                "tipo_transformador": tipo_transformador, "potencia_mva": potencia_mva,
                "tensao_at": tensao_at, "tensao_at_tap_maior": tensao_at_tap_maior,
                "tensao_at_tap_menor": tensao_at_tap_menor, "tensao_bt": tensao_bt,
                "tensao_terciario": tensao_terciario,
            }
            from utils.elec import calculate_nominal_currents
            calculated_currents = calculate_nominal_currents(transformer_data_for_currents)
            corrente_at = calculated_currents.get("corrente_nominal_at")
            corrente_bt = calculated_currents.get("corrente_nominal_bt")
            corrente_terciario = calculated_currents.get("corrente_nominal_terciario")
            corrente_at_tap_maior = calculated_currents.get("corrente_nominal_at_tap_maior")
            corrente_at_tap_menor = calculated_currents.get("corrente_nominal_at_tap_menor")

            if hasattr(app_instance, "mcp") and app_instance.mcp is not None:
                mcp_snapshot_before_update = app_instance.mcp.get_data("transformer-inputs-store") or {}
                data_to_save_to_mcp = mcp_snapshot_before_update.copy()

                direct_input_fields_map = {
                    "potencia_mva": potencia_mva, "frequencia": frequencia, "grupo_ligacao": grupo_ligacao,
                    "liquido_isolante": liquido_isolante, "elevacao_oleo_topo": elevacao_oleo_topo,
                    "elevacao_enrol": elevacao_enrol, "tipo_transformador": tipo_transformador,
                    "tipo_isolamento": tipo_isolamento, "norma_iso": norma_iso,
                    "peso_total": peso_total, "peso_parte_ativa": peso_parte_ativa, "peso_oleo": peso_oleo,
                    "peso_tanque_acessorios": peso_tanque_acessorios, "tensao_at": tensao_at,
                    "classe_tensao_at": classe_tensao_at, "impedancia": impedancia, "conexao_at": conexao_at,
                    "classe_tensao_neutro_at": classe_tensao_neutro_at, "tensao_at_tap_maior": tensao_at_tap_maior, # Changed key
                    "impedancia_tap_maior": impedancia_tap_maior, "tensao_at_tap_menor": tensao_at_tap_menor,
                    "impedancia_tap_menor": impedancia_tap_menor, "tensao_bt": tensao_bt,
                    "classe_tensao_bt": classe_tensao_bt, "conexao_bt": conexao_bt,
                    "classe_tensao_neutro_bt": classe_tensao_neutro_bt, "tensao_terciario": tensao_terciario, # Changed key
                    "classe_tensao_terciario": classe_tensao_terciario, "conexao_terciario": conexao_terciario,
                    "classe_tensao_neutro_terciario": classe_tensao_neutro_terciario, # Changed key
                }
                dynamic_fields_from_form_map = {
                    "nbi_at": nbi_at, "sil_at": sil_at, "nbi_neutro_at": nbi_neutro_at,
                    "sil_neutro_at": sil_neutro_at, "teste_tensao_aplicada_at": teste_tensao_aplicada_at,
                    "teste_tensao_induzida_at": teste_tensao_induzida_at, "nbi_bt": nbi_bt, "sil_bt": sil_bt,
                    "nbi_neutro_bt": nbi_neutro_bt, "sil_neutro_bt": sil_neutro_bt,
                    "teste_tensao_aplicada_bt": teste_tensao_aplicada_bt, "nbi_terciario": nbi_terciario,
                    "sil_terciario": sil_terciario, "nbi_neutro_terciario": nbi_neutro_terciario,
                    "sil_neutro_terciario": sil_neutro_terciario,
                    "teste_tensao_aplicada_terciario": teste_tensao_aplicada_terciario,
                }

                for key, form_value in direct_input_fields_map.items():
                    # Se o valor do formulário for uma string vazia, trata como None.
                    # Caso contrário, usa o valor do formulário.
                    # Isto permite limpar campos numéricos para None.
                    if isinstance(form_value, str) and form_value.strip() == "":
                        data_to_save_to_mcp[key] = None
                    elif form_value is not None:
                        data_to_save_to_mcp[key] = form_value
                    elif key not in data_to_save_to_mcp: # Se era None e não estava no store
                        data_to_save_to_mcp[key] = None
                    # Se era None e estava no store, mantém o valor do store (já copiado)
                    # ou permite que seja None se o objetivo é limpar.
                    # Para garantir que um campo possa ser explicitamente limpo para None:
                    elif form_value is None and key in data_to_save_to_mcp:
                         data_to_save_to_mcp[key] = None


                for key, form_value in dynamic_fields_from_form_map.items():
                    # Para campos dinâmicos (dropdowns de níveis de isolamento),
                    # se o valor do formulário for None ou uma string vazia, guarda None.
                    # Caso contrário, guarda o valor como string.
                    if form_value is None or (isinstance(form_value, str) and form_value.strip() == ""):
                        data_to_save_to_mcp[key] = None
                    else:
                        data_to_save_to_mcp[key] = str(form_value)
                        # Log para verificar os valores de isolamento sendo salvos
                        if key in ["nbi_at", "sil_at", "teste_tensao_aplicada_at", "teste_tensao_induzida_at"]:
                            log.info(f"[UpdateTransformerCalc] Salvando valor de isolamento: {key}={form_value}")

                # Garantir que teste_tensao_induzida também seja mantido para compatibilidade
                if data_to_save_to_mcp.get("teste_tensao_induzida_at") is not None:
                    data_to_save_to_mcp["teste_tensao_induzida"] = data_to_save_to_mcp["teste_tensao_induzida_at"]
                    log.info(f"[UpdateTransformerCalc] Mantendo compatibilidade: teste_tensao_induzida={data_to_save_to_mcp['teste_tensao_induzida']}")

                # Garantir que elevacao_enrol seja o mesmo para AT, BT e terciário
                if elevacao_enrol is not None:
                    data_to_save_to_mcp["elevacao_enrol_at"] = elevacao_enrol
                    data_to_save_to_mcp["elevacao_enrol_bt"] = elevacao_enrol
                    data_to_save_to_mcp["elevacao_enrol_terciario"] = elevacao_enrol
                    log.info(f"[UpdateTransformerCalc] Sincronizando elevação de enrolamento: AT=BT=Terciário={elevacao_enrol}°C")

                data_to_save_to_mcp["corrente_nominal_at"] = corrente_at
                data_to_save_to_mcp["corrente_nominal_bt"] = corrente_bt
                data_to_save_to_mcp["corrente_nominal_terciario"] = corrente_terciario
                data_to_save_to_mcp["corrente_nominal_at_tap_maior"] = corrente_at_tap_maior
                data_to_save_to_mcp["corrente_nominal_at_tap_menor"] = corrente_at_tap_menor

                iac_at_calc, iac_bt_calc, iac_terciario_calc = None, None, None
                norma_para_iac = data_to_save_to_mcp.get("norma_iso")
                if norma_para_iac and "IEC" in norma_para_iac:
                    for winding_prefix_iac, nbi_key_iac in [("at", "nbi_at"), ("bt", "nbi_bt"), ("terciario", "nbi_terciario")]:
                        nbi_val_str = data_to_save_to_mcp.get(nbi_key_iac, "")
                        iac_val = None
                        if nbi_val_str and str(nbi_val_str).strip() != "":
                            try:
                                iac_val = round(1.1 * float(nbi_val_str), 2)
                            except (ValueError, TypeError):
                                log.warning(f"Não foi possível calcular IAC para {winding_prefix_iac} a partir de {nbi_key_iac}: {nbi_val_str}")
                        if winding_prefix_iac == "at": iac_at_calc = iac_val
                        elif winding_prefix_iac == "bt": iac_bt_calc = iac_val
                        elif winding_prefix_iac == "terciario": iac_terciario_calc = iac_val

                data_to_save_to_mcp["iac_at"] = iac_at_calc
                data_to_save_to_mcp["iac_bt"] = iac_bt_calc
                data_to_save_to_mcp["iac_terciario"] = iac_terciario_calc

                serializable_data = convert_numpy_types(data_to_save_to_mcp, debug_path="update_transformer_inputs_final")
                app_instance.mcp.set_data("transformer-inputs-store", serializable_data)
                app_instance.mcp.save_to_disk(force=True)
                log.debug("[UpdateTransformerCalc] MCP atualizado e salvo no disco.")

                try:
                    latest_data_for_propagation = app_instance.mcp.get_data("transformer-inputs-store")
                    if not latest_data_for_propagation or not any(latest_data_for_propagation.get(k) is not None for k in ["potencia_mva", "tensao_at", "tensao_bt"]):
                        log.warning("[UpdateTransformerCalc] Dados insuficientes para propagação. Abortando.")
                    else:
                        from utils.mcp_persistence import ensure_mcp_data_propagation
                        target_stores = [
                            "losses-store", "impulse-store", "dieletric-analysis-store",
                            "applied-voltage-store", "induced-voltage-store", "short-circuit-store",
                            "temperature-rise-store", "comprehensive-analysis-store",
                        ]
                        for target_store in target_stores:
                            ensure_mcp_data_propagation(app_instance, "transformer-inputs-store", [target_store])
                        log.debug("[UpdateTransformerCalc] Dados propagados para todos os stores alvo.")
                except Exception as e_prop:
                    log.error(f"[UpdateTransformerCalc] Erro ao propagar dados: {e_prop}", exc_info=True)

        except Exception as e:
            log.error(f"[UpdateTransformerCalc] Erro ao calcular/salvar: {e}", exc_info=True)

        return corrente_at, corrente_bt, corrente_terciario, corrente_at_tap_maior, corrente_at_tap_menor

    # Callback para carregar dados do MCP para os inputs
    @app_instance.callback(
        [
            Output("potencia_mva", "value"),
            Output("frequencia", "value"),
            Output("grupo_ligacao", "value"),
            Output("liquido_isolante", "value"),
            Output("elevacao_oleo_topo", "value"),
            Output("elevacao_enrol", "value"),
            Output("tipo_transformador", "value"),
            Output("tipo_isolamento", "value"),
            Output("norma_iso", "value"),
            Output("peso_total", "value"),
            Output("peso_parte_ativa", "value"),
            Output("peso_oleo", "value"),
            Output("peso_tanque_acessorios", "value"),
            Output("tensao_at", "value"),
            Output("classe_tensao_at", "value"),
            Output("impedancia", "value"),
            Output("nbi_at", "value"),
            Output("sil_at", "value"),
            Output("conexao_at", "value"),
            Output("classe_tensao_neutro_at", "value"), # Changed ID
            Output("nbi_neutro_at", "value"),
            Output("sil_neutro_at", "value"),
            Output("tensao_at_tap_maior", "value"),
            Output("impedancia_tap_maior", "value"),
            Output("tensao_at_tap_menor", "value"),
            Output("impedancia_tap_menor", "value"),
            Output("teste_tensao_aplicada_at", "value"),
            Output("teste_tensao_induzida_at", "value"),
            Output("tensao_bt", "value"),
            Output("classe_tensao_bt", "value"),
            Output("nbi_bt", "value"),
            Output("sil_bt", "value"),
            Output("conexao_bt", "value"),
            Output("classe_tensao_neutro_bt", "value"), # Changed ID
            Output("nbi_neutro_bt", "value"),
            Output("sil_neutro_bt", "value"),
            Output("teste_tensao_aplicada_bt", "value"),
            Output("tensao_terciario", "value"),
            Output("classe_tensao_terciario", "value"),
            Output("nbi_terciario", "value"),
            Output("sil_terciario", "value"),
            Output("conexao_terciario", "value"),
            Output("classe_tensao_neutro_terciario", "value"), # Changed ID
            Output("nbi_neutro_terciario", "value"),
            Output("sil_neutro_terciario", "value"),
            Output("teste_tensao_aplicada_terciario", "value"),
        ],
        [
            Input("url", "pathname"),
            Input("transformer-inputs-store", "data"),
        ],
        prevent_initial_call=False,
    )
    def load_transformer_inputs_from_mcp(pathname, transformer_data):
        from dash import ctx
        # ROUTE_HOME is now imported, normalize_pathname also imported

        triggered_id = ctx.triggered_id
        log.debug(f"[LOAD TransformerInputs] Acionado por: {triggered_id}")

        # Normaliza o pathname para remover barras extras
        clean_path = normalize_pathname(pathname) if pathname else ""

        # Only proceed if we are on the transformer inputs page
        if clean_path != ROUTE_HOME:
            log.debug(f"[LOAD TransformerInputs] Não na página '{ROUTE_HOME}' (atual: '{clean_path}'). Prevenindo atualização.")
            raise PreventUpdate

        # Se não temos dados do transformador, não faz nada (ou return no_update for all outputs)
        if not transformer_data:
            log.debug("[LOAD TransformerInputs] Sem dados do transformador, prevenindo atualização")
            raise PreventUpdate

        # Verificar se os dados do transformador estão aninhados em transformer_data
        if "transformer_data" in transformer_data and isinstance(transformer_data["transformer_data"], dict):
            # Usar os dados aninhados
            transformer_dict = transformer_data["transformer_data"]
            log.debug(f"[LOAD TransformerInputs] Usando dados aninhados em transformer_data")
        else:
            # Usar os dados diretamente
            transformer_dict = transformer_data
            log.debug(f"[LOAD TransformerInputs] Usando dados diretamente do dicionário principal")

        # Extrair valores do dicionário
        potencia_mva = transformer_dict.get("potencia_mva")
        frequencia = transformer_dict.get("frequencia")
        grupo_ligacao = transformer_dict.get("grupo_ligacao")
        liquido_isolante = transformer_dict.get("liquido_isolante")
        elevacao_oleo_topo = transformer_dict.get("elevacao_oleo_topo")
        elevacao_enrol = transformer_dict.get("elevacao_enrol")
        tipo_transformador = transformer_dict.get("tipo_transformador")
        tipo_isolamento = transformer_dict.get("tipo_isolamento")
        norma_iso = transformer_dict.get("norma_iso")
        peso_total = transformer_dict.get("peso_total")
        peso_parte_ativa = transformer_dict.get("peso_parte_ativa")
        peso_oleo = transformer_dict.get("peso_oleo")
        peso_tanque_acessorios = transformer_dict.get("peso_tanque_acessorios")
        tensao_at = transformer_dict.get("tensao_at")
        classe_tensao_at = transformer_dict.get("classe_tensao_at")
        impedancia = transformer_dict.get("impedancia")
        nbi_at = transformer_dict.get("nbi_at")
        sil_at = transformer_dict.get("sil_at")
        conexao_at = transformer_dict.get("conexao_at")
        classe_tensao_neutro_at = transformer_dict.get("classe_tensao_neutro_at") # Changed key
        nbi_neutro_at = transformer_dict.get("nbi_neutro_at")
        sil_neutro_at = transformer_dict.get("sil_neutro_at")
        tensao_at_tap_maior = transformer_dict.get("tensao_at_tap_maior")
        impedancia_tap_maior = transformer_dict.get("impedancia_tap_maior")
        tensao_at_tap_menor = transformer_dict.get("tensao_at_tap_menor")
        impedancia_tap_menor = transformer_dict.get("impedancia_tap_menor")
        teste_tensao_aplicada_at = transformer_dict.get("teste_tensao_aplicada_at")
        teste_tensao_induzida_at = transformer_dict.get("teste_tensao_induzida_at")
        tensao_bt = transformer_dict.get("tensao_bt")
        classe_tensao_bt = transformer_dict.get("classe_tensao_bt")
        nbi_bt = transformer_dict.get("nbi_bt")
        sil_bt = transformer_dict.get("sil_bt")
        conexao_bt = transformer_dict.get("conexao_bt")
        classe_tensao_neutro_bt = transformer_dict.get("classe_tensao_neutro_bt") # Changed key
        nbi_neutro_bt = transformer_dict.get("nbi_neutro_bt")
        sil_neutro_bt = transformer_dict.get("sil_neutro_bt")
        teste_tensao_aplicada_bt = transformer_dict.get("teste_tensao_aplicada_bt")
        tensao_terciario = transformer_dict.get("tensao_terciario")
        classe_tensao_terciario = transformer_dict.get("classe_tensao_terciario")
        nbi_terciario = transformer_dict.get("nbi_terciario")
        sil_terciario = transformer_dict.get("sil_terciario")
        conexao_terciario = transformer_dict.get("conexao_terciario")
        classe_tensao_neutro_terciario = transformer_dict.get("classe_tensao_neutro_terciario") # Changed key
        nbi_neutro_terciario = transformer_dict.get("nbi_neutro_terciario")
        sil_neutro_terciario = transformer_dict.get("sil_neutro_terciario")
        teste_tensao_aplicada_terciario = transformer_dict.get("teste_tensao_aplicada_terciario")

        # Garantir que elevacao_enrol seja o mesmo para AT, BT e terciário
        # Se elevacao_enrol não estiver definido, mas algum dos específicos estiver, usar esse valor
        if elevacao_enrol is None:
            elevacao_enrol_at = transformer_dict.get("elevacao_enrol_at")
            elevacao_enrol_bt = transformer_dict.get("elevacao_enrol_bt")
            elevacao_enrol_terciario = transformer_dict.get("elevacao_enrol_terciario")
            
            # Usar o primeiro valor não nulo encontrado
            if elevacao_enrol_at is not None:
                elevacao_enrol = elevacao_enrol_at
                log.info(f"[LOAD TransformerInputs] Usando elevacao_enrol_at={elevacao_enrol}°C como valor comum")
            elif elevacao_enrol_bt is not None:
                elevacao_enrol = elevacao_enrol_bt
                log.info(f"[LOAD TransformerInputs] Usando elevacao_enrol_bt={elevacao_enrol}°C como valor comum")
            elif elevacao_enrol_terciario is not None:
                elevacao_enrol = elevacao_enrol_terciario
                log.info(f"[LOAD TransformerInputs] Usando elevacao_enrol_terciario={elevacao_enrol}°C como valor comum")

        # Retornar todos os valores
        return (
            potencia_mva, frequencia, grupo_ligacao, liquido_isolante, elevacao_oleo_topo,
            elevacao_enrol, tipo_transformador, tipo_isolamento, norma_iso, peso_total,
            peso_parte_ativa, peso_oleo, peso_tanque_acessorios, tensao_at, classe_tensao_at,
            impedancia, nbi_at, sil_at, conexao_at, classe_tensao_neutro_at, nbi_neutro_at, # Changed variable
            sil_neutro_at, tensao_at_tap_maior, impedancia_tap_maior, tensao_at_tap_menor,
            impedancia_tap_menor, teste_tensao_aplicada_at, teste_tensao_induzida_at,
            tensao_bt, classe_tensao_bt, nbi_bt, sil_bt, conexao_bt, classe_tensao_neutro_bt, # Changed variable
            nbi_neutro_bt, sil_neutro_bt, teste_tensao_aplicada_bt, tensao_terciario,
            classe_tensao_terciario, nbi_terciario, sil_terciario, conexao_terciario,
            classe_tensao_neutro_terciario, nbi_neutro_terciario, sil_neutro_terciario, # Changed variable
            teste_tensao_aplicada_terciario,
        )
