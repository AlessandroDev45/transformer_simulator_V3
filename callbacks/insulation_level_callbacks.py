# callbacks/insulation_level_callbacks.py
"""
Callbacks para seleção detalhada de níveis de isolamento.
Estes callbacks APENAS populam as OPÇÕES dos dropdowns
NBI, SIL, Aplicada e Induzida, com base na Norma e Classe de Tensão.
O VALOR selecionado é gerenciado pela persistência do browser e pelo
callback principal em transformer_inputs_fix.py.
"""

import json
import logging
from dash import Input, Output, State, html, dcc, no_update, ctx
from dash.exceptions import PreventUpdate

# Importar funções de app_core.isolation_repo
from app_core.isolation_repo import get_isolation_levels, create_options_for_key, get_distinct_values_for_norma

log = logging.getLogger(__name__)
# Configuração de logging explícita para este módulo
if not log.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
log.setLevel(logging.DEBUG)

log.info("="*20 + " MÓDULO INSULATION_LEVEL_CALLBACKS (Options Only Logic) CARREGADO " + "="*20)

# Carregar os dados do JSON
try:
    with open("assets/tabela.json", "r", encoding="utf-8") as f:
        TABELA_DATA = json.load(f)
    INSULATION_LEVELS = TABELA_DATA.get("insulation_levels", [])
    log.info(f"Dados de níveis de isolamento carregados: {len(INSULATION_LEVELS)} registros")
except FileNotFoundError:
    log.error("ERRO: assets/tabela.json não encontrado!")
    INSULATION_LEVELS = []
except json.JSONDecodeError:
    log.error("ERRO: Falha ao decodificar assets/tabela.json!")
    INSULATION_LEVELS = []

def create_options_from_list_simple(values_list, label_suffix=""):
    """Cria opções para um dropdown a partir de uma lista de valores, APENAS options."""
    default_empty_option = [{"label": "N/A", "value": ""}]
    if values_list is None:
        log.debug(f"SimpleOptions: Lista de valores é None para suffix '{label_suffix}'. Retornando N/A.")
        return default_empty_option

    processed_values = []
    seen = set()
    for v in values_list:
        if v is not None and v not in seen:
            processed_values.append(v)
            seen.add(v)

    if not processed_values:
        log.debug(f"SimpleOptions: Lista de valores processados está vazia para suffix '{label_suffix}'. Retornando N/A.")
        return default_empty_option

    try:
        # Tentar ordenar. Se houver mistura de tipos (ex: int e 'NA_SIL'), ordenar como string.
        distinct_sorted_values = sorted(processed_values, key=lambda x: str(x))
    except TypeError: # Fallback se a ordenação complexa falhar
        distinct_sorted_values = sorted(processed_values, key=str)


    # GARANTIR QUE OS VALUES DAS OPÇÕES SEJAM STRINGS
    options = [{"label": f"{val}{label_suffix}", "value": str(val)} for val in distinct_sorted_values]
    log.debug(f"SimpleOptions: Opções geradas: {options} para suffix: '{label_suffix}'")
    return options

def register_insulation_level_callbacks(app_instance):
    log.info("Registrando callbacks de níveis de isolamento (APENAS OPÇÕES - V2)...")

    # --- CALLBACKS PARA ENROLAMENTOS PRINCIPAIS (AT, BT, TERCIARIO) ---
    def create_main_winding_insulation_callback(winding_prefix):
        outputs_options_only = [
            Output(f"nbi_{winding_prefix}", "options", allow_duplicate=True),
            Output(f"sil_{winding_prefix}", "options", allow_duplicate=True),
            Output(f"teste_tensao_aplicada_{winding_prefix}", "options", allow_duplicate=True)
        ]
        # Tensão Induzida apenas para AT
        ti_outputs = [
            Output(f"teste_tensao_induzida_{winding_prefix}", "options", allow_duplicate=True)
        ] if winding_prefix == "at" else []

        outputs_final = outputs_options_only + ti_outputs

        @app_instance.callback(
            outputs_final,
            [Input("url", "pathname"),  # Para carga inicial
             Input("norma_iso", "value"),
             Input(f"classe_tensao_{winding_prefix}", "value"),
             Input(f"tensao_{winding_prefix}", "value")],  # Adicionado para acionar quando a tensão é alterada
            [State("transformer-inputs-store", "data"),  # Adicionado para obter valores armazenados no MCP
             State(f"nbi_{winding_prefix}", "value"),  # Adicionado para obter valor atual do dropdown
             State(f"sil_{winding_prefix}", "value"),  # Adicionado para obter valor atual do dropdown
             State(f"teste_tensao_aplicada_{winding_prefix}", "value"),  # Adicionado para obter valor atual do dropdown
             State(f"teste_tensao_induzida_{winding_prefix}", "value") if winding_prefix == "at" else State("url", "pathname")],  # Adicionado para obter valor atual do dropdown (apenas para AT)
            prevent_initial_call=False  # Executa na carga inicial para popular options
        )
        def update_winding_insulation_options(pathname, norma_selecionada, um_kv_str_input, tensao, mcp_data, current_nbi, current_sil, current_ta, current_ti=None):
            triggered_id = ctx.triggered_id if ctx.triggered else "initial_load_or_direct_call"
            log.info(f"[OPTIONS CB - {winding_prefix.upper()}] Acionado por: {triggered_id}. Norma: {norma_selecionada}, Um_kv: {um_kv_str_input}, Tensão: {tensao}, Path: {pathname}")

            # Obter valores do MCP se disponíveis
            mcp_nbi = None
            mcp_sil = None
            mcp_ta = None
            mcp_ti = None

            if mcp_data and isinstance(mcp_data, dict):
                mcp_nbi = mcp_data.get(f"nbi_{winding_prefix}")
                mcp_sil = mcp_data.get(f"sil_{winding_prefix}")
                mcp_ta = mcp_data.get(f"teste_tensao_aplicada_{winding_prefix}")
                if winding_prefix == "at":
                    mcp_ti = mcp_data.get(f"teste_tensao_induzida_{winding_prefix}")

                log.info(f"[OPTIONS CB - {winding_prefix.upper()}] Valores do MCP: NBI={mcp_nbi}, SIL={mcp_sil}, TA={mcp_ta}, TI={mcp_ti}")

            # Usar valores atuais dos dropdowns ou do MCP
            saved_nbi = current_nbi if current_nbi is not None else mcp_nbi
            saved_sil = current_sil if current_sil is not None else mcp_sil
            saved_ta = current_ta if current_ta is not None else mcp_ta
            saved_ti = current_ti if current_ti is not None else mcp_ti

            log.info(f"[OPTIONS CB - {winding_prefix.upper()}] Valores salvos: NBI={saved_nbi}, SIL={saved_sil}, TA={saved_ta}, TI={saved_ti}")

            # Default para norma IEC se não especificada
            norma_para_opcoes = norma_selecionada if norma_selecionada else "IEC"
            standard_filter = "IEC/NBR" if "IEC" in norma_para_opcoes else "IEEE"

            um_kv_val = None
            if um_kv_str_input is not None and str(um_kv_str_input).strip() != "":
                try:
                    um_kv_val = float(um_kv_str_input)
                except ValueError:
                    log.warning(f"  [OPTIONS CB - {winding_prefix.upper()}] Um_kv_str '{um_kv_str_input}' inválido.")
                    # Continua para popular com opções genéricas se for carga inicial

            options_nbi, options_sil, options_ta, options_ti = [], [], [], []
            empty_opts_na = [{"label": "N/A", "value": ""}]  # Opção padrão para "Não Aplicável"

            if um_kv_val is not None:
                # Lógica para buscar opções filtradas pela Classe de Tensão (Um)
                levels_data_dict, _ = get_isolation_levels(um_kv_val, "", norma_para_opcoes)  # Conexão não afeta options aqui

                options_nbi = [{"label": f"{val} kVp", "value": str(val)} for val in levels_data_dict.get("nbi_list", []) if val is not None] or empty_opts_na

                sil_list_vals = levels_data_dict.get("sil_im_list", [])
                if not any(v is not None and v != "NA_SIL" for v in sil_list_vals) and "NA_SIL" not in [str(v) for v in sil_list_vals]:  # Se só tem None ou vazia
                    options_sil = [{"label": "Não Aplicável", "value": "NA_SIL"}]
                else:
                    options_sil = [{"label": f"{val} kVp" if val != "NA_SIL" else "Não Aplicável", "value": str(val)} for val in sil_list_vals if val is not None] or empty_opts_na

                options_ta = [{"label": f"{val} kVrms", "value": str(val)} for val in levels_data_dict.get("tensao_aplicada_list", []) if val is not None] or empty_opts_na
                if winding_prefix == "at":
                    options_ti = [{"label": f"{val} kVrms", "value": str(val)} for val in levels_data_dict.get("tensao_induzida_list", []) if val is not None] or empty_opts_na
                log.info(f"  [OPTIONS CB - {winding_prefix.upper()}] Opções FILTRADAS por Um={um_kv_val} e Norma={norma_para_opcoes}.")
            else:
                # Lógica para carga inicial SEM Um: Popula com todas as opções distintas da norma
                log.info(f"  [OPTIONS CB - {winding_prefix.upper()}] Um NÃO definido. Populando com opções GERAIS para Norma={norma_para_opcoes}.")
                options_nbi = create_options_for_key(standard_filter.split('/')[0], "bil_kvp", " kVp")

                # Para SIL, é mais complexo devido ao "NA_SIL" e BSL
                sil_distinct_raw = get_distinct_values_for_norma(standard_filter.split('/')[0], "sil_kvp")
                if standard_filter == "IEEE":  # IEEE pode usar BSL
                    bsl_distinct_raw = get_distinct_values_for_norma(standard_filter.split('/')[0], "bsl_kvp")
                    # Combina e remove duplicatas, mantendo a ordem
                    combined_sil_bsl = []
                    seen_sil_bsl = set()
                    for v_sil in sil_distinct_raw:
                        if v_sil not in seen_sil_bsl:
                            combined_sil_bsl.append({"label": f"{v_sil} kVp", "value": str(v_sil)})
                            seen_sil_bsl.add(v_sil)
                    for v_bsl in bsl_distinct_raw:
                         if v_bsl not in seen_sil_bsl:  # Adiciona BSL se ainda não estiver lá (como SIL)
                            combined_sil_bsl.append({"label": f"{v_bsl} kVp (BSL)", "value": str(v_bsl)})
                            seen_sil_bsl.add(v_bsl)
                    # Ordena pela parte numérica do label
                    options_sil = sorted(combined_sil_bsl, key=lambda x: float(x['label'].split(' ')[0]) if x['label'].split(' ')[0].replace('.','',1).isdigit() else float('inf'))
                else:  # IEC/NBR
                    options_sil = [{"label": f"{val} kVp", "value": str(val)} for val in sil_distinct_raw]

                # Adiciona "Não Aplicável" para SIL se não estiver presente
                if not any(opt['value'] == "NA_SIL" for opt in options_sil):
                     options_sil.insert(0, {"label": "Não Aplicável", "value": "NA_SIL"})

                options_ta = create_options_for_key(standard_filter.split('/')[0], "acsd_kv_rms", " kVrms")
                if winding_prefix == "at":
                    # Para Tensão Induzida, podemos combinar ACLD e ACSD para as opções iniciais
                    acld_distinct = get_distinct_values_for_norma(standard_filter.split('/')[0], "acld_kv_rms")
                    acsd_distinct = get_distinct_values_for_norma(standard_filter.split('/')[0], "acsd_kv_rms")
                    combined_ti_raw = sorted(list(set(acld_distinct + acsd_distinct)))
                    options_ti = [{"label": f"{val} kVrms", "value": str(val)} for val in combined_ti_raw] or empty_opts_na

            # Garantir que os valores salvos estejam nas opções
            if saved_nbi is not None and str(saved_nbi).strip() != "":
                # Verificar se o valor já está nas opções
                is_value_in_options = any(opt["value"] == str(saved_nbi) for opt in options_nbi)
                log.info(f"  [OPTIONS CB - {winding_prefix.upper()}] Verificando se valor salvo de NBI ({saved_nbi}) já está nas opções: {is_value_in_options}")

                # Listar todas as opções disponíveis para debug
                option_values = [opt["value"] for opt in options_nbi]
                log.info(f"  [OPTIONS CB - {winding_prefix.upper()}] Opções disponíveis para NBI: {option_values}")

                if not is_value_in_options:
                    log.info(f"  [OPTIONS CB - {winding_prefix.upper()}] Adicionando valor salvo de NBI às opções: {saved_nbi}")
                    options_nbi.append({"label": f"{saved_nbi} kVp (Salvo)", "value": str(saved_nbi)})

            if saved_sil is not None and str(saved_sil).strip() != "":
                if not any(opt["value"] == str(saved_sil) for opt in options_sil):
                    log.info(f"  [OPTIONS CB - {winding_prefix.upper()}] Adicionando valor salvo de SIL às opções: {saved_sil}")
                    if saved_sil == "NA_SIL":
                        if not any(opt["value"] == "NA_SIL" for opt in options_sil):
                            options_sil.insert(0, {"label": "Não Aplicável", "value": "NA_SIL"})
                    else:
                        options_sil.append({"label": f"{saved_sil} kVp (Salvo)", "value": str(saved_sil)})

            if saved_ta is not None and str(saved_ta).strip() != "":
                if not any(opt["value"] == str(saved_ta) for opt in options_ta):
                    log.info(f"  [OPTIONS CB - {winding_prefix.upper()}] Adicionando valor salvo de TA às opções: {saved_ta}")
                    options_ta.append({"label": f"{saved_ta} kVrms (Salvo)", "value": str(saved_ta)})

            if winding_prefix == "at" and saved_ti is not None and str(saved_ti).strip() != "":
                if not any(opt["value"] == str(saved_ti) for opt in options_ti):
                    log.info(f"  [OPTIONS CB - {winding_prefix.upper()}] Adicionando valor salvo de TI às opções: {saved_ti}")
                    options_ti.append({"label": f"{saved_ti} kVrms (Salvo)", "value": str(saved_ti)})

            log.debug(f"  [OPTIONS CB - {winding_prefix.upper()}] NBI opts: {len(options_nbi)}, SIL opts: {len(options_sil)}, TA opts: {len(options_ta)}")
            if winding_prefix == "at":
                log.debug(f"  [OPTIONS CB - {winding_prefix.upper()}] TI opts: {len(options_ti)}")
                return options_nbi, options_sil, options_ta, options_ti
            return options_nbi, options_sil, options_ta

    create_main_winding_insulation_callback("at")
    create_main_winding_insulation_callback("bt")
    create_main_winding_insulation_callback("terciario")

    # --- CALLBACKS PARA GERENCIAMENTO DO NEUTRO ---
    def create_neutral_insulation_callbacks(winding_prefix):
        @app_instance.callback(
            [Output(f"nbi_neutro_{winding_prefix}", "options", allow_duplicate=True),
             Output(f"sil_neutro_{winding_prefix}", "options", allow_duplicate=True)],
            [Input("url", "pathname"),
             Input("norma_iso", "value"),
             Input(f"classe_tensao_neutro_{winding_prefix}", "value"),  # Changed ID to the new Dropdown
             Input(f"conexao_{winding_prefix}", "value"),  # Necessário para saber se é YN/ZN
             Input(f"tensao_{winding_prefix}", "value")],  # Adicionado para acionar quando a tensão é alterada
            [State("transformer-inputs-store", "data"),  # Adicionado para obter valores armazenados no MCP
             State(f"nbi_neutro_{winding_prefix}", "value"),  # Adicionado para obter valor atual do dropdown
             State(f"sil_neutro_{winding_prefix}", "value")],  # Adicionado para obter valor atual do dropdown
            prevent_initial_call=False
        )
        def update_neutral_insulation_options(pathname, norma_selecionada, um_kv_neutral_str, connection_type, tensao, mcp_data, current_nbi_neutro, current_sil_neutro):
            triggered_id = ctx.triggered_id if ctx.triggered else "initial_load_or_direct_call"
            log.info(f"[OPTIONS CB - {winding_prefix.upper()}-NEUTRO] Acionado por: {triggered_id}. Norma: {norma_selecionada}, Um_Neutro: {um_kv_neutral_str}, Conexão: {connection_type}, Tensão: {tensao}")

            # Obter valores do MCP se disponíveis
            mcp_nbi_neutro = None
            mcp_sil_neutro = None

            if mcp_data and isinstance(mcp_data, dict):
                mcp_nbi_neutro = mcp_data.get(f"nbi_neutro_{winding_prefix}")
                mcp_sil_neutro = mcp_data.get(f"sil_neutro_{winding_prefix}")

                log.info(f"[OPTIONS CB - {winding_prefix.upper()}-NEUTRO] Valores do MCP: NBI={mcp_nbi_neutro}, SIL={mcp_sil_neutro}")

            # Usar valores atuais dos dropdowns ou do MCP
            saved_nbi_neutro = current_nbi_neutro if current_nbi_neutro is not None else mcp_nbi_neutro
            saved_sil_neutro = current_sil_neutro if current_sil_neutro is not None else mcp_sil_neutro

            log.info(f"[OPTIONS CB - {winding_prefix.upper()}-NEUTRO] Valores salvos: NBI={saved_nbi_neutro}, SIL={saved_sil_neutro}")

            norma_para_opcoes = norma_selecionada if norma_selecionada else "IEC"
            standard_filter = "IEC/NBR" if "IEC" in norma_para_opcoes else "IEEE"
            empty_opts_na = [{"label": "N/A", "value": ""}]

            # Se o neutro não for acessível, opções vazias/NA
            if connection_type not in ["estrela", "ziguezague"]:  # "estrela" representa YN
                log.debug(f"  [OPTIONS CB - {winding_prefix.upper()}-NEUTRO] Conexão '{connection_type}' não tem neutro acessível. Opções N/A.")
                return empty_opts_na, empty_opts_na

            um_kv_neutral_val = None
            if um_kv_neutral_str is not None and str(um_kv_neutral_str).strip() != "":
                try:
                    um_kv_neutral_val = float(um_kv_neutral_str)
                except ValueError:
                     log.warning(f"  [OPTIONS CB - {winding_prefix.upper()}-NEUTRO] Um_Neutro '{um_kv_neutral_str}' inválido.")

            options_nbi_neutro, options_sil_neutro = [], []

            if um_kv_neutral_val is not None:
                # Popula opções filtradas pela Classe de Tensão do Neutro
                conexao_mapped_neutro = "YN" if connection_type == "estrela" else "ZN" if connection_type == "ziguezague" else ""
                neutro_levels_data_dict, _ = get_isolation_levels(um_kv_neutral_val, conexao_mapped_neutro, norma_para_opcoes)

                options_nbi_neutro = [{"label": f"{val} kVp", "value": str(val)} for val in neutro_levels_data_dict.get("nbi_list", []) if val is not None] or empty_opts_na

                sil_list_neutro_vals = neutro_levels_data_dict.get("sil_im_list", [])
                if not any(v is not None and v != "NA_SIL" for v in sil_list_neutro_vals) and "NA_SIL" not in [str(v) for v in sil_list_neutro_vals]:
                    options_sil_neutro = [{"label": "Não Aplicável", "value": "NA_SIL"}]
                else:
                    options_sil_neutro = [{"label": f"{val} kVp" if val != "NA_SIL" else "Não Aplicável", "value": str(val)} for val in sil_list_neutro_vals if val is not None] or empty_opts_na

                log.info(f"  [OPTIONS CB - {winding_prefix.upper()}-NEUTRO] Opções FILTRADAS por Um_Neutro={um_kv_neutral_val} e Norma={norma_para_opcoes}.")
            else:
                # Popula com todas as opções distintas da norma para NBI Neutro e SIL Neutro
                log.info(f"  [OPTIONS CB - {winding_prefix.upper()}-NEUTRO] Um_Neutro NÃO definido. Populando com opções GERAIS para Norma={norma_para_opcoes}.")
                options_nbi_neutro = create_options_for_key(standard_filter.split('/')[0], "bil_kvp", " kVp")  # Reutiliza BIL para NBI Neutro

                # Para SIL Neutro, a lógica é similar ao SIL principal
                sil_distinct_raw_neutro = get_distinct_values_for_norma(standard_filter.split('/')[0], "sil_kvp")
                if standard_filter == "IEEE":
                    bsl_distinct_raw_neutro = get_distinct_values_for_norma(standard_filter.split('/')[0], "bsl_kvp")
                    combined_sil_bsl_neutro = []
                    seen_sil_bsl_neutro = set()
                    for v_sil_n in sil_distinct_raw_neutro:
                        if v_sil_n not in seen_sil_bsl_neutro:
                            combined_sil_bsl_neutro.append({"label": f"{v_sil_n} kVp", "value": str(v_sil_n)})
                            seen_sil_bsl_neutro.add(v_sil_n)
                    for v_bsl_n in bsl_distinct_raw_neutro:
                         if v_bsl_n not in seen_sil_bsl_neutro:
                            combined_sil_bsl_neutro.append({"label": f"{v_bsl_n} kVp (BSL)", "value": str(v_bsl_n)})
                            seen_sil_bsl_neutro.add(v_bsl_n)
                    options_sil_neutro = sorted(combined_sil_bsl_neutro, key=lambda x: float(x['label'].split(' ')[0]) if x['label'].split(' ')[0].replace('.','',1).isdigit() else float('inf'))
                else:  # IEC/NBR
                    options_sil_neutro = [{"label": f"{val} kVp", "value": str(val)} for val in sil_distinct_raw_neutro]

                if not any(opt['value'] == "NA_SIL" for opt in options_sil_neutro):
                     options_sil_neutro.insert(0, {"label": "Não Aplicável", "value": "NA_SIL"})

            # Garantir que os valores salvos estejam nas opções
            if saved_nbi_neutro is not None and str(saved_nbi_neutro).strip() != "":
                if not any(opt["value"] == str(saved_nbi_neutro) for opt in options_nbi_neutro):
                    log.info(f"  [OPTIONS CB - {winding_prefix.upper()}-NEUTRO] Adicionando valor salvo de NBI Neutro às opções: {saved_nbi_neutro}")
                    options_nbi_neutro.append({"label": f"{saved_nbi_neutro} kVp (Salvo)", "value": str(saved_nbi_neutro)})

            if saved_sil_neutro is not None and str(saved_sil_neutro).strip() != "":
                if not any(opt["value"] == str(saved_sil_neutro) for opt in options_sil_neutro):
                    log.info(f"  [OPTIONS CB - {winding_prefix.upper()}-NEUTRO] Adicionando valor salvo de SIL Neutro às opções: {saved_sil_neutro}")
                    if saved_sil_neutro == "NA_SIL":
                        if not any(opt["value"] == "NA_SIL" for opt in options_sil_neutro):
                            options_sil_neutro.insert(0, {"label": "Não Aplicável", "value": "NA_SIL"})
                    else:
                        options_sil_neutro.append({"label": f"{saved_sil_neutro} kVp (Salvo)", "value": str(saved_sil_neutro)})

            log.debug(f"  [OPTIONS CB - {winding_prefix.upper()}-NEUTRO] NBI Neutro opts: {len(options_nbi_neutro)}, SIL Neutro opts: {len(options_sil_neutro)}")
            return options_nbi_neutro, options_sil_neutro

        # Callback para visibilidade dos campos do neutro (mantido)
        @app_instance.callback(
            [Output(f"classe_tensao_neutro_{winding_prefix}", "disabled", allow_duplicate=True), # Changed ID
             Output(f"nbi_neutro_{winding_prefix}", "disabled", allow_duplicate=True),
             Output(f"sil_neutro_{winding_prefix}", "disabled", allow_duplicate=True),
             Output(f"{winding_prefix}_neutral_fields_row", "style", allow_duplicate=True)],
            [Input(f"conexao_{winding_prefix}", "value")],
            prevent_initial_call=False
        )
        def manage_neutral_fields_visibility_state(connection_type):
            is_neutral_accessible = connection_type in ["estrela", "ziguezague"]
            disabled_state = not is_neutral_accessible
            display_style = {"display": "none"} if disabled_state else {"display": "flex"}  # "flex" para alinhar com os outros
            return disabled_state, disabled_state, disabled_state, display_style

    create_neutral_insulation_callbacks("at")
    create_neutral_insulation_callbacks("bt")
    create_neutral_insulation_callbacks("terciario")

    log.info("Callbacks de níveis de isolamento (APENAS OPÇÕES - V2) registrados.")
