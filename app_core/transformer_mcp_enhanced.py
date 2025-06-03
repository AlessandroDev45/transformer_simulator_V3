"""
Master Control Program (MCP) aprimorado para o Transformer Test Simulator.
Implementa persistência centralizada e propagação automática de dados entre módulos.
"""

import logging
import json
import copy
import math
from typing import Dict, Any, List, Optional, Tuple, Set, Callable

from utils.store_diagnostics import convert_numpy_types, is_json_serializable, fix_store_data
from utils.db_manager import save_test_session, get_test_session_details as db_get_session_details, session_name_exists, delete_test_session as db_delete_session
from utils.mcp_disk_persistence import save_mcp_state_to_disk, load_mcp_state_from_disk
from utils.mcp_persistence_enhanced import auto_update_on_change, sync_isolation_values, propagate_all_data

log = logging.getLogger(__name__)

# Lista de todos os store IDs usados na aplicação
STORE_IDS = [
    'transformer-inputs-store',
    'losses-store',
    'impulse-store',
    'dieletric-analysis-store',
    'applied-voltage-store',
    'induced-voltage-store',
    'short-circuit-store',
    'temperature-rise-store',
    'comprehensive-analysis-store',
    'front-resistor-data',
    'tail-resistor-data',
    'calculated-inductance',
    'simulation-status'
]

# Valores padrão para transformer inputs
DEFAULT_TRANSFORMER_INPUTS = {
    'tipo_transformador': 'Trifásico',
    'frequencia': 60.0,
    'conexao_at': None,
    'conexao_bt': None,
    'conexao_terciario': '',
    'liquido_isolante': 'Mineral',
    'tipo_isolamento': 'uniforme',
    'potencia_mva': None,
    'grupo_ligacao': None,
    'elevacao_oleo_topo': None,
    'elevacao_enrol': None,
    'tensao_at': None,
    'classe_tensao_at': None,
    'elevacao_enrol_at': None,
    'impedancia': None,
    'nbi_at': None,
    'sil_at': None,
    'tensao_at_tap_maior': None,
    'impedancia_tap_maior': None,
    'tensao_at_tap_menor': None,
    'impedancia_tap_menor': None,
    'teste_tensao_aplicada_at': None,
    'teste_tensao_induzida_at': None,
    'teste_tensao_induzida': None,   
    'tensao_bt': None,
    'classe_tensao_bt': None,
    'elevacao_enrol_bt': None,
    'nbi_bt': None,
    'sil_bt': None,
    'teste_tensao_aplicada_bt': None,
    'tensao_terciario': None,
    'classe_tensao_terciario': None,
    'elevacao_enrol_terciario': None,
    'nbi_terciario': None,
    'sil_terciario': None,
    'teste_tensao_aplicada_terciario': None,
    'tensao_bucha_neutro_at': None,
    'tensao_bucha_neutro_bt': None,
    'tensao_bucha_neutro_terciario': None,
    'nbi_neutro_at': None,
    'nbi_neutro_bt': None,
    'nbi_neutro_terciario': None,
    'peso_total': None,
    'peso_parte_ativa': None,
    'peso_oleo': None,
    'peso_tanque_acessorios': None,
    'corrente_nominal_at': None,
    'corrente_nominal_at_tap_maior': None,
    'corrente_nominal_at_tap_menor': None,
    'corrente_nominal_bt': None,
    'corrente_nominal_terciario': None
}

class TransformerMCPEnhanced:
    """
    Master Control Program (MCP) aprimorado para o Transformer Test Simulator.
    Implementa persistência centralizada e propagação automática de dados entre módulos.
    """
    
    def __init__(self, load_from_disk=False):
        """
        Inicializa o MCP.
        
        Args:
            load_from_disk: Se True, carrega os dados do disco
        """
        log.info(f"Initializing Enhanced Transformer MCP (load_from_disk={load_from_disk})")
        self._data = {}
        self._listeners = {}
        self._change_history = []
        self.last_save_error = None
        self._initialize_stores()

        # Carregar dados do disco se solicitado
        if load_from_disk:
            self._load_from_disk()

    def _initialize_stores(self):
        """Inicializa todos os stores com valores padrão."""
        log.info("===============================================================")
        log.info("[MCP INITIALIZE] INICIALIZANDO STORES:")

        # Inicializar todos os stores com valores vazios
        for store_id in STORE_IDS:
            if store_id == 'transformer-inputs-store':
                # Para transformer-inputs-store, usar os valores padrão
                self._data[store_id] = DEFAULT_TRANSFORMER_INPUTS.copy()
                log.info("===============================================================")
                log.info("[MCP INITIALIZE] DADOS INICIAIS DO TRANSFORMER-INPUTS-STORE:")
                log.info(f"DADOS COMPLETOS INICIAIS: {json.dumps(self._data[store_id], indent=2)}")
                log.info("===============================================================")
            else:
                # Para outros stores, inicializar com dicionário vazio
                self._data[store_id] = {}

        log.info("===============================================================")
        log.info(f"Enhanced MCP Initialized {len(STORE_IDS)} data stores")
        log.info("===============================================================")

    def get_data(self, store_id: str, force_reload: bool = False) -> Dict[str, Any]:
        """
        Obtém os dados de um store específico.

        Args:
            store_id: ID do store
            force_reload: Se True, tenta recarregar os dados do disco antes de retornar

        Returns:
            Cópia dos dados do store ou dicionário vazio se o store não existir
        """
        # Se force_reload for True, tenta recarregar os dados do disco
        if force_reload:
            log.info(f"[MCP GET] Forçando recarga dos dados do disco para store '{store_id}'")
            self._load_from_disk()

        if store_id not in self._data:
            log.warning(f"[MCP GET] Store ID '{store_id}' não encontrado. Retornando dicionário vazio.")
            return {}

        # Retorna uma cópia profunda para evitar modificações acidentais
        return copy.deepcopy(self._data.get(store_id, {}))

    def set_data(self, store_id: str, data: Dict[str, Any], auto_propagate: bool = True, app_instance=None) -> None:
        """
        Define os dados de um store específico e opcionalmente propaga as alterações.

        Args:
            store_id: ID do store
            data: Dados a serem definidos
            auto_propagate: Se True, propaga automaticamente as alterações para outros stores
            app_instance: Instância da aplicação Dash (necessária para propagação automática)
        """
        if store_id not in STORE_IDS:
            log.warning(f"[MCP SET] Store ID '{store_id}' não é um store conhecido. Ignorando.")
            return

        # Converter tipos numpy para tipos Python nativos
        serializable_data = convert_numpy_types(data, debug_path=f"mcp_set.{store_id}")

        # Registrar alteração no histórico
        old_data = self.get_data(store_id)
        self._register_change(store_id, old_data, serializable_data)

        # Atualizar os dados
        self._data[store_id] = serializable_data

        # Notificar listeners
        self._notify_listeners(store_id, serializable_data)

        # Propagar alterações automaticamente se solicitado
        if auto_propagate and app_instance is not None:
            try:
                auto_update_on_change(app_instance, store_id, serializable_data)
                log.info(f"[MCP SET] Alterações em '{store_id}' propagadas automaticamente.")
            except Exception as e:
                log.error(f"[MCP SET] Erro ao propagar alterações de '{store_id}': {e}")

        log.debug(f"[MCP SET] Dados definidos para store '{store_id}'.")

    def _register_change(self, store_id: str, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> None:
        """
        Registra uma alteração no histórico.

        Args:
            store_id: ID do store
            old_data: Dados antigos
            new_data: Dados novos
        """
        # Limitar o tamanho do histórico
        if len(self._change_history) > 100:
            self._change_history.pop(0)

        # Registrar alteração
        self._change_history.append({
            'store_id': store_id,
            'timestamp': logging.Formatter.formatTime(logging.Formatter(), logging.LogRecord('', 0, '', 0, None, None, None)),
            'changes': self._get_changes(old_data, new_data)
        })

    def _get_changes(self, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Tuple[Any, Any]]:
        """
        Identifica as alterações entre dois conjuntos de dados.

        Args:
            old_data: Dados antigos
            new_data: Dados novos

        Returns:
            Dicionário com as alterações (chave: (valor_antigo, valor_novo))
        """
        changes = {}

        # Identificar valores alterados ou adicionados
        for key, new_value in new_data.items():
            if key not in old_data:
                changes[key] = (None, new_value)
            elif old_data[key] != new_value:
                changes[key] = (old_data[key], new_value)

        # Identificar valores removidos
        for key in old_data:
            if key not in new_data:
                changes[key] = (old_data[key], None)

        return changes

    def get_change_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Obtém o histórico de alterações.

        Args:
            limit: Número máximo de alterações a retornar

        Returns:
            Lista com o histórico de alterações
        """
        if limit is None:
            return copy.deepcopy(self._change_history)
        else:
            # Corrige: se limit for None ou não for int, retorna tudo
            if not isinstance(limit, int) or limit <= 0:
                return copy.deepcopy(self._change_history)
            return copy.deepcopy(self._change_history[-limit:])

    def get_all_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtém todos os dados de todos os stores.

        Returns:
            Cópia de todos os dados
        """
        # Retorna uma cópia profunda para evitar modificações acidentais
        return copy.deepcopy(self._data)

    def clear_data(self, app_instance=None) -> Dict[str, Dict[str, Any]]:
        """
        Limpa todos os dados de todos os stores, redefinindo-os para os valores padrão.

        Args:
            app_instance: Instância da aplicação Dash (necessária para propagação automática)

        Returns:
            Cópia dos dados após a limpeza
        """
        # Reinicializar todos os stores
        self._initialize_stores()

        # Notificar listeners
        for store_id in STORE_IDS:
            self._notify_listeners(store_id, self._data[store_id])

        # Propagar alterações automaticamente se app_instance for fornecido
        if app_instance is not None:
            try:
                propagate_all_data(app_instance)
                log.info("[MCP CLEAR] Dados propagados para todos os stores após limpeza.")
            except Exception as e:
                log.error(f"[MCP CLEAR] Erro ao propagar dados após limpeza: {e}")

        log.info("[MCP CLEAR] Todos os stores foram limpos e redefinidos para os valores padrão.")

        # Retornar uma cópia dos dados após a limpeza
        return self.get_all_data()

    def _notify_listeners(self, store_id: str, data: Dict[str, Any]) -> None:
        """
        Notifica os listeners de um store específico.

        Args:
            store_id: ID do store
            data: Dados atualizados
        """
        if store_id in self._listeners:
            for listener in self._listeners[store_id]:
                try:
                    listener(data)
                except Exception as e:
                    log.error(f"[MCP NOTIFY] Erro ao notificar listener para store '{store_id}': {e}")

    def add_listener(self, store_id: str, listener: Callable) -> None:
        """
        Adiciona um listener para um store específico.

        Args:
            store_id: ID do store
            listener: Função a ser chamada quando o store for atualizado
        """
        if store_id not in self._listeners:
            self._listeners[store_id] = []

        # Corrige: verifica se listener é uma função
        if not callable(listener):
            raise TypeError("Listener deve ser uma função ou método.")
        self._listeners[store_id].append(listener)
        log.debug(f"[MCP ADD_LISTENER] Listener adicionado para store '{store_id}'.")

    def remove_listener(self, store_id: str, listener: Callable) -> None:
        """
        Remove um listener de um store específico.

        Args:
            store_id: ID do store
            listener: Função a ser removida
        """
        if store_id in self._listeners and listener in self._listeners[store_id]:
            self._listeners[store_id].remove(listener)
            log.debug(f"[MCP REMOVE_LISTENER] Listener removido de store '{store_id}'.")

    def save_to_disk(self, force: bool = False) -> bool:
        """
        Salva o estado atual do MCP em disco.

        Args:
            force: Se True, força o salvamento mesmo que não haja alterações

        Returns:
            bool: True se o salvamento foi bem-sucedido, False caso contrário
        """
        log.info("[MCP SAVE_TO_DISK] Salvando estado do MCP em disco...")

        # Obter dados de todos os stores
        all_data = self.get_all_data()

        # Verificar se há dados para salvar
        if not all_data and not force:
            log.warning("[MCP SAVE_TO_DISK] Nenhum dado para salvar. Abortando.")
            return False

        # Verificar se há dados essenciais no transformer-inputs-store
        transformer_data = all_data.get('transformer-inputs-store', {})
        if not transformer_data and not force:
            log.warning("[MCP SAVE_TO_DISK] Dados do transformer-inputs-store vazios. Abortando.")
            return False

        # Salvar dados em disco
        success = save_mcp_state_to_disk(all_data, create_backup=True)

        if success:
            log.info("[MCP SAVE_TO_DISK] Estado do MCP salvo em disco com sucesso.")
        else:
            log.error("[MCP SAVE_TO_DISK] Falha ao salvar estado do MCP em disco.")

        return success

    def _load_from_disk(self) -> bool:
        """
        Carrega o estado do MCP a partir do disco.

        Returns:
            bool: True se o carregamento foi bem-sucedido, False caso contrário
        """
        log.info("Carregando dados do MCP a partir do disco")

        # Carregar dados do disco
        stores_data, success = load_mcp_state_from_disk()

        if not success:
            log.warning("Falha ao carregar dados do MCP do disco. Mantendo valores padrão.")
            return False

        # Atualizar dados do MCP
        for store_id, data in stores_data.items():
            if store_id in STORE_IDS:
                # Converter tipos numpy para tipos Python nativos
                serializable_data = convert_numpy_types(data, debug_path=f"mcp_init_load.{store_id}")

                # Verificar se o store atual já tem dados
                current_store_data = self._data.get(store_id, {})

                # Se o store atual já tem dados e os dados carregados também são um dicionário,
                # mesclar os dados em vez de substituir
                if current_store_data and isinstance(current_store_data, dict) and isinstance(serializable_data, dict):
                    # Verificar se há dados específicos no store carregado
                    has_specific_inputs = any(key.startswith('inputs_') for key in serializable_data.keys())

                    if has_specific_inputs:
                        log.debug(f"[MCP LOAD FROM DISK] Mesclando dados específicos para o store '{store_id}'")
                        # Mesclar os dados, dando prioridade aos dados carregados
                        merged_data = {**current_store_data, **serializable_data}
                        serializable_data = merged_data
                        log.debug(f"[MCP LOAD FROM DISK] Dados mesclados para o store '{store_id}': {list(serializable_data.keys())}")

                # Atualizar dados
                self._data[store_id] = serializable_data
                log.info(f"Dados carregados do disco para store: {store_id}")
            else:
                log.warning(f"Store ID '{store_id}' do disco não é um store conhecido. Ignorando.")

        return True

    def save_session(self, session_name: str, notes: str = "", stores_data: Optional[Dict[str, Any]] = None) -> int:
        """
        Salva uma sessão de teste no banco de dados.
        Se stores_data for fornecido (eg., vindo de callback States), usa esses dados.
        Se stores_data for None, usa o estado interno do MCP (self._data).

        Args:
            session_name: Nome da sessão
            notes: Notas da sessão
            stores_data: Opcional. Dicionário {store_id: data} com os dados a serem salvos.

        Returns:
            int: O ID da sessão salva (> 0) ou um código de erro (< 0):
                 -1: Erro genérico ou falha no DB
                 -2: Nome da sessão já existe
                 -3: Erro de serialização crítico (após fix_store_data)
        """
        self.last_save_error = None
        log.info(f"[MCP SAVE SESSION] Tentando salvar sessão: '{session_name}'")

        # Verifica nome duplicado PRIMEIRO
        if session_name_exists(session_name):
            log.warning(f"[MCP SAVE SESSION] Nome da sessão '{session_name}' já existe.")
            self.last_save_error = f"Nome de sessão '{session_name}' já existe."
            return -2

        # 1. Obter dados de todos os stores. Use stores_data se fornecido, senão use o estado interno do MCP.
        if stores_data is not None:
            log.debug("[MCP SAVE SESSION] Usando dados fornecidos para salvamento.")
            data_to_process = copy.deepcopy(stores_data) # Sempre trabalhar com uma cópia
            # Verificar se os dados fornecidos incluem pelo menos os stores básicos
            if not any(sid in data_to_process for sid in STORE_IDS):
                 log.warning("[MCP SAVE SESSION] Os dados fornecidos parecem incompletos (não contêm IDs de store conhecidos). Fallback para estado interno do MCP.")
                 data_to_process = self.get_all_data() # Fallback para o estado interno
            else:
                 log.debug(f"[MCP SAVE SESSION] Dados fornecidos contêm {len(data_to_process)} stores: {list(data_to_process.keys())}")

        else:
            log.debug("[MCP SAVE SESSION] Usando dados do estado interno do MCP para salvamento.")
            data_to_process = self.get_all_data() # Já retorna uma deepcopy

        # Verificar se há dados para salvar (após determinar a fonte)
        if not data_to_process:
             log.warning("[MCP SAVE SESSION] Nenhuma dado disponível para salvar. Abortando.")
             self.last_save_error = "Nenhum dado disponível para salvar."
             return -1 # Ou outro código para "sem dados"

        # 2. Verificação de serializabilidade e correção em TODOS os dados
        log.debug("[MCP SAVE SESSION] Realizando verificação e preparação dos dados para DB...")
        data_prepared_for_db = fix_store_data(data_to_process) # fix_store_data já chama convert_numpy_types

        # 3. Verificar se algum store teve falha crítica na conversão
        for store_id_check, store_content_check in data_prepared_for_db.items():
            # fix_store_data pode retornar um dicionário especial para indicar falha
            if isinstance(store_content_check, dict) and store_content_check.get("_conversion_failed"):
                err_msg = store_content_check.get("_error", "Erro desconhecido na conversão.")
                log.error(f"[MCP SAVE SESSION] Falha crítica ao preparar store '{store_id_check}' para salvamento: {err_msg}")
                self.last_save_error = f"Erro ao preparar dados do store '{store_id_check}': {err_msg}"
                return -3 # Erro de serialização crítico

        # 4. Chamar o db_manager para salvar
        log.debug("[MCP SAVE SESSION] Chamando db_manager.save_test_session com dados preparados...")
        
        # Converter dados para JSON
        json_data = {}
        for store_id, store_data in data_prepared_for_db.items():
            try:
                json_data[store_id] = json.dumps(store_data)
            except Exception as e:
                log.error(f"[MCP SAVE SESSION] Erro ao converter store '{store_id}' para JSON: {e}")
                self.last_save_error = f"Erro ao converter store '{store_id}' para JSON: {e}"
                return -3

        # Salvar no banco de dados
        try:
            # Corrige: passa o dicionário de dados como primeiro argumento, nome da sessão como segundo, notas como terceiro
            session_id = save_test_session(data_prepared_for_db, session_name, notes)
            if session_id > 0:
                log.info(f"[MCP SAVE SESSION] Sessão '{session_name}' salva com sucesso. ID: {session_id}")
                return session_id
            else:
                log.error(f"[MCP SAVE SESSION] Falha ao salvar sessão '{session_name}'. Código de erro: {session_id}")
                self.last_save_error = f"Falha ao salvar sessão no banco de dados. Código de erro: {session_id}"
                return session_id
        except Exception as e:
            log.error(f"[MCP SAVE SESSION] Exceção ao salvar sessão '{session_name}': {e}")
            self.last_save_error = f"Exceção ao salvar sessão: {e}"
            return -1

    def load_session(self, session_id: int, app_instance=None) -> bool:
        """
        Carrega uma sessão de teste do banco de dados.

        Args:
            session_id: ID da sessão a ser carregada
            app_instance: Instância da aplicação Dash (necessária para propagação automática)

        Returns:
            bool: True se o carregamento foi bem-sucedido, False caso contrário
        """
        log.info(f"[MCP LOAD SESSION] Tentando carregar sessão com ID: {session_id}")

        try:
            # Obter detalhes da sessão
            session_details = db_get_session_details(session_id)
            if not session_details:
                log.warning(f"[MCP LOAD SESSION] Sessão com ID {session_id} não encontrada.")
                return False

            # Extrair dados da sessão
            session_data = session_details.get('data', {})
            if not session_data:
                log.warning(f"[MCP LOAD SESSION] Sessão com ID {session_id} não contém dados.")
                return False

            # Converter dados de JSON para dicionário
            stores_data = {}
            for store_id, json_data in session_data.items():
                try:
                    stores_data[store_id] = json.loads(json_data)
                except Exception as e:
                    log.error(f"[MCP LOAD SESSION] Erro ao converter JSON para store '{store_id}': {e}")
                    return False

            # Atualizar dados do MCP
            for store_id, data in stores_data.items():
                if store_id in STORE_IDS:
                    self._data[store_id] = data
                    self._notify_listeners(store_id, data)
                    log.info(f"[MCP LOAD SESSION] Dados carregados para store: {store_id}")
                else:
                    log.warning(f"[MCP LOAD SESSION] Store ID '{store_id}' não é um store conhecido. Ignorando.")

            # Propagar alterações automaticamente se app_instance for fornecido
            if app_instance is not None:
                try:
                    propagate_all_data(app_instance)
                    log.info("[MCP LOAD SESSION] Dados propagados para todos os stores após carregamento.")
                except Exception as e:
                    log.error(f"[MCP LOAD SESSION] Erro ao propagar dados após carregamento: {e}")

            log.info(f"[MCP LOAD SESSION] Sessão com ID {session_id} carregada com sucesso.")
            return True

        except Exception as e:
            log.error(f"[MCP LOAD SESSION] Exceção ao carregar sessão com ID {session_id}: {e}")
            return False

    def delete_session(self, session_id: int) -> bool:
        """
        Exclui uma sessão de teste do banco de dados.

        Args:
            session_id: ID da sessão a ser excluída

        Returns:
            bool: True se a exclusão foi bem-sucedida, False caso contrário
        """
        log.info(f"[MCP DELETE SESSION] Tentando excluir sessão com ID: {session_id}")

        try:
            # Excluir sessão
            success = db_delete_session(session_id)
            if success:
                log.info(f"[MCP DELETE SESSION] Sessão com ID {session_id} excluída com sucesso.")
            else:
                log.warning(f"[MCP DELETE SESSION] Falha ao excluir sessão com ID {session_id}.")
            return success
        except Exception as e:
            log.error(f"[MCP DELETE SESSION] Exceção ao excluir sessão com ID {session_id}: {e}")
            return False

    def calculate_nominal_currents(self, transformer_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calcula as correntes nominais do transformador.

        Args:
            transformer_data: Dados do transformador

        Returns:
            Dict[str, float]: Dicionário com as correntes nominais calculadas
        """
        try:
            from utils.elec import calculate_nominal_currents
            result = calculate_nominal_currents(transformer_data)
            # Remove valores None para garantir Dict[str, float]
            return {k: v for k, v in result.items() if v is not None}
        except Exception as e:
            log.error(f"[MCP CALCULATE CURRENTS] Erro ao calcular correntes nominais: {e}")
            return {}

    def get_last_save_error(self) -> Optional[str]:
        """
        Obtém o último erro de salvamento.

        Returns:
            Optional[str]: Mensagem do último erro de salvamento ou None se não houver erro
        """
        return self.last_save_error

from dash import Dash
from typing import Optional

class MCPInterface:
    def __init__(self):
        self.store_data = {
            store_id: {} for store_id in STORE_IDS
        }

    def get_data(self, store_name: str) -> dict:
        """Retrieve data from the specified store."""
        return self.store_data.get(store_name, {})

class DashWithMCP(Dash):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mcp: Optional[MCPInterface] = MCPInterface()
