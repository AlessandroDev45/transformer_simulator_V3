# callbacks/global_actions.py
"""
Callbacks para ações globais da aplicação, como limpar todos os campos.
"""
import logging

from dash import Input, Output, State, ctx, no_update
from dash.exceptions import PreventUpdate

# Importar a instância da aplicação
from app import app
from utils.routes import normalize_pathname, ROUTE_HOME, ROUTE_LOSSES, ROUTE_IMPULSE, ROUTE_DIELETRIC, ROUTE_APPLIED_VOLTAGE, ROUTE_INDUCED_VOLTAGE, ROUTE_SHORT_CIRCUIT, ROUTE_TEMPERATURE_RISE

log = logging.getLogger(__name__)


# --- Callback para abrir o modal de confirmação ---
def global_actions_toggle_clear_modal(n_global, n_cancel, n_confirm, is_open):
    """Abre ou fecha o modal de confirmação para limpar todos os campos."""
    print(f"[DEBUG] toggle_clear_modal acionado. Trigger: {ctx.triggered_id}")

    if ctx.triggered_id == "global-clear-button":
        print("[DEBUG] Abrindo modal de confirmação para limpar campos")
        return True
    elif ctx.triggered_id in ["clear-cancel-button", "clear-confirm-button"]:
        print(f"[DEBUG] Fechando modal de confirmação. Botão: {ctx.triggered_id}")
        return False

    print("[DEBUG] Mantendo estado atual do modal")
    return is_open


# --- Callback para limpar dados do módulo ativo ---
def global_actions_clear_module_data(n_clicks, pathname):
    """Limpa apenas os dados do módulo ativo quando o botão de confirmação é clicado."""
    print(f"[DEBUG] clear_module_data acionado. n_clicks: {n_clicks}, pathname: {pathname}")

    # Log detalhado para diagnóstico
    log.info(f"CLEAR_MODULE_DATA Start - Trigger: {ctx.triggered_id}, Pathname: {pathname}")
    print(f"[DEBUG] CLEAR_MODULE_DATA Start - Trigger: {ctx.triggered_id}, Pathname: {pathname}")

    if n_clicks is None or n_clicks == 0:
        print("[DEBUG] PreventUpdate em clear_module_data (n_clicks é None ou 0)")
        log.info("CLEAR_MODULE_DATA Aborted - n_clicks is None or 0")
        raise PreventUpdate

    # Verificar se estamos em uma página que não deve atualizar os stores
    if pathname and pathname.strip("/") in ["consulta-normas", "gerenciar-normas"]:
        print(f"[DEBUG] Ignorando limpeza em página não relacionada: {pathname}")
        log.info(f"CLEAR_MODULE_DATA Skipped - Pathname: {pathname} is not related")
        return [no_update] * 12

    # Normalizar o pathname para identificar o módulo ativo
    normalized_path = normalize_pathname(pathname)
    if not normalized_path:
        normalized_path = ROUTE_HOME  # Default para a página inicial

    log.info(f"Limpando dados do módulo ativo: {normalized_path}")
    print(f"[DEBUG] Iniciando limpeza de dados do módulo: {normalized_path}")

    # Mapear pathname para o store correspondente
    store_to_clear = None
    if normalized_path == ROUTE_HOME:
        store_to_clear = "transformer-inputs-store"
    elif normalized_path == ROUTE_LOSSES:
        store_to_clear = "losses-store"
    elif normalized_path == ROUTE_IMPULSE:
        store_to_clear = "impulse-store"
    elif normalized_path == ROUTE_DIELETRIC:
        store_to_clear = "dieletric-analysis-store"
    elif normalized_path == ROUTE_APPLIED_VOLTAGE:
        store_to_clear = "applied-voltage-store"
    elif normalized_path == ROUTE_INDUCED_VOLTAGE:
        store_to_clear = "induced-voltage-store"
    elif normalized_path == ROUTE_SHORT_CIRCUIT:
        store_to_clear = "short-circuit-store"
    elif normalized_path == ROUTE_TEMPERATURE_RISE:
        store_to_clear = "temperature-rise-store"
    else:
        log.warning(f"Módulo não reconhecido: {normalized_path}. Nenhum dado será limpo.")
        return [no_update] * 12

    # Preparar retorno - todos os stores são no_update por padrão
    result = [no_update] * 12
    
    # Índice do store a ser atualizado
    store_indices = {
        "transformer-inputs-store": 0,
        "losses-store": 1,
        "impulse-store": 2,
        "dieletric-analysis-store": 3,
        "applied-voltage-store": 4,
        "induced-voltage-store": 5,
        "short-circuit-store": 6,
        "temperature-rise-store": 7,
        "front-resistor-data": 8,
        "tail-resistor-data": 9,
        "calculated-inductance": 10,
        "simulation-status": 11
    }
    
    # Usar o MCP para limpar apenas o store do módulo ativo
    try:
        if hasattr(app, "mcp") and app.mcp is not None:
            # Limpar apenas o store do módulo ativo
            if store_to_clear == "transformer-inputs-store":
                # Para transformer-inputs-store, usar os valores padrão
                from app_core.transformer_mcp import DEFAULT_TRANSFORMER_INPUTS
                
                # Atualizar o store no MCP
                app.mcp.set_data(store_to_clear, DEFAULT_TRANSFORMER_INPUTS.copy())
                
                # Atualizar também o cache
                app.transformer_data_cache = DEFAULT_TRANSFORMER_INPUTS.copy()
                
                # Atualizar o resultado para retornar
                result[store_indices[store_to_clear]] = DEFAULT_TRANSFORMER_INPUTS.copy()
                
                log.info("Cache de dados do transformador limpo para o módulo ativo.")
                print("[DEBUG] Cache de dados do transformador limpo para o módulo ativo.")
            else:
                # Para outros stores, limpar completamente (tanto inputs quanto memória)
                # Criar um novo dicionário vazio mantendo apenas a estrutura básica
                new_data = {"transformer_data": {}}
                
                # Atualizar o store no MCP com os dados limpos
                app.mcp.set_data(store_to_clear, new_data)
                
                # Atualizar o resultado para retornar
                result[store_indices[store_to_clear]] = new_data
                
                # Para o módulo de impulso, limpar também os dados relacionados
                if store_to_clear == "impulse-store":
                    app.mcp.set_data("front-resistor-data", {})
                    app.mcp.set_data("tail-resistor-data", {})
                    app.mcp.set_data("calculated-inductance", {})
                    app.mcp.set_data("simulation-status", {"running": False})
                    
                    result[store_indices["front-resistor-data"]] = {}
                    result[store_indices["tail-resistor-data"]] = {}
                    result[store_indices["calculated-inductance"]] = {}
                    result[store_indices["simulation-status"]] = {"running": False}
            
            log.info(f"CLEAR_MODULE_DATA End - Dados do módulo {normalized_path} limpos com sucesso")
            print(f"[DEBUG] CLEAR_MODULE_DATA End - Dados do módulo {normalized_path} limpos com sucesso")
            
            return tuple(result)
        else:
            # Fallback para o método antigo se o MCP não estiver disponível
            log.warning("MCP não disponível. Usando método antigo para limpar dados.")
            print("[DEBUG] MCP não disponível. Usando método antigo para limpar dados.")

            # Valores padrão para cada store
            from app_core.transformer_mcp import DEFAULT_TRANSFORMER_INPUTS
            
            # Atualizar apenas o store do módulo ativo
            if store_to_clear in store_indices:
                if store_to_clear == "transformer-inputs-store":
                    result[store_indices[store_to_clear]] = DEFAULT_TRANSFORMER_INPUTS.copy()
                else:
                    # Para outros stores, criar um dicionário vazio com a estrutura básica
                    result[store_indices[store_to_clear]] = {"transformer_data": {}}
                
                # Para o módulo de impulso, limpar também os dados relacionados
                if store_to_clear == "impulse-store":
                    result[store_indices["front-resistor-data"]] = {}
                    result[store_indices["tail-resistor-data"]] = {}
                    result[store_indices["calculated-inductance"]] = {}
                    result[store_indices["simulation-status"]] = {"running": False}
            
            log.info(f"CLEAR_MODULE_DATA End - Dados do módulo {normalized_path} limpos com sucesso (fallback)")
            print(f"[DEBUG] CLEAR_MODULE_DATA End - Dados do módulo {normalized_path} limpos com sucesso (fallback)")
            
            return tuple(result)
    except Exception as e:
        log.error(f"Erro ao limpar dados do módulo {normalized_path}: {e}")
        print(f"[DEBUG] Erro ao limpar dados do módulo {normalized_path}: {e}")
        import traceback
        print(f"[DEBUG] Traceback: {traceback.format_exc()}")

        # Em caso de erro, não atualizar nenhum store
        return [no_update] * 12


# Registrar os callbacks com a aplicação
def register_global_actions_callbacks(app):
    """Registra os callbacks de ações globais com a aplicação."""
    app.callback(
        Output("clear-confirm-modal", "is_open"),
        [
            Input("global-clear-button", "n_clicks"),
            Input("clear-cancel-button", "n_clicks"),
            Input("clear-confirm-button", "n_clicks"),
        ],
        [State("clear-confirm-modal", "is_open")],
        prevent_initial_call=True,
    )(global_actions_toggle_clear_modal)

    app.callback(
        # Outputs para os stores (com allow_duplicate=True)
        [
            Output("transformer-inputs-store", "data", allow_duplicate=True),
            Output("losses-store", "data", allow_duplicate=True),
            Output("impulse-store", "data", allow_duplicate=True),
            Output("dieletric-analysis-store", "data", allow_duplicate=True),
            Output("applied-voltage-store", "data", allow_duplicate=True),
            Output("induced-voltage-store", "data", allow_duplicate=True),
            Output("short-circuit-store", "data", allow_duplicate=True),
            Output("temperature-rise-store", "data", allow_duplicate=True),
            Output("front-resistor-data", "data", allow_duplicate=True),
            Output("tail-resistor-data", "data", allow_duplicate=True),
            Output("calculated-inductance", "data", allow_duplicate=True),
            Output("simulation-status", "data", allow_duplicate=True),
        ],
        [Input("clear-confirm-button", "n_clicks")],
        [State("url", "pathname")],
        prevent_initial_call=True,
    )(global_actions_clear_module_data)
