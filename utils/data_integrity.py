"""
Utilitários para garantir a integridade e consistência dos dados entre módulos.
"""

import logging
import json
import copy
from typing import Dict, Any, List, Optional, Set, Tuple

log = logging.getLogger(__name__)

def validate_transformer_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Valida os dados básicos do transformador.
    
    Args:
        data: Dados do transformador a serem validados
        
    Returns:
        Tuple[bool, List[str]]: (válido, lista de erros)
    """
    errors = []
    
    # Campos obrigatórios
    required_fields = [
        "potencia_mva", "tensao_at", "tensao_bt", "frequencia", 
        "tipo_transformador", "conexao_at", "conexao_bt"
    ]
    
    # Verificar campos obrigatórios
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            errors.append(f"Campo obrigatório '{field}' não preenchido")
    
    # Verificar valores numéricos
    numeric_fields = [
        "potencia_mva", "tensao_at", "tensao_bt", "tensao_terciario",
        "frequencia", "impedancia", "impedancia_tap_maior", "impedancia_tap_menor"
    ]
    
    for field in numeric_fields:
        if field in data and data[field] is not None and data[field] != "":
            try:
                float(data[field])
            except (ValueError, TypeError):
                errors.append(f"Campo '{field}' deve ser um valor numérico")
    
    # Verificar valores positivos
    positive_fields = [
        "potencia_mva", "tensao_at", "tensao_bt", "tensao_terciario",
        "frequencia", "impedancia"
    ]
    
    for field in positive_fields:
        if field in data and data[field] is not None and data[field] != "":
            try:
                value = float(data[field])
                if value <= 0:
                    errors.append(f"Campo '{field}' deve ser um valor positivo")
            except (ValueError, TypeError):
                pass  # Já tratado na verificação anterior
    
    # Verificar valores de enumeração
    if "tipo_transformador" in data and data["tipo_transformador"] not in ["Monofásico", "Trifásico"]:
        errors.append("Tipo de transformador deve ser 'Monofásico' ou 'Trifásico'")
    
    if "conexao_at" in data and data["conexao_at"] not in ["estrela", "triangulo"]:
        errors.append("Conexão AT deve ser 'estrela' ou 'triangulo'")
    
    if "conexao_bt" in data and data["conexao_bt"] not in ["estrela", "triangulo"]:
        errors.append("Conexão BT deve ser 'estrela' ou 'triangulo'")
    
    if "conexao_terciario" in data and data["conexao_terciario"] not in ["", "estrela", "triangulo"]:
        errors.append("Conexão terciário deve ser 'estrela', 'triangulo' ou vazio")
    
    # Verificar consistência entre campos
    if "tensao_terciario" in data and data["tensao_terciario"] and "conexao_terciario" not in data:
        errors.append("Conexão terciário deve ser especificada quando tensão terciário é informada")
    
    # Verificar consistência de impedância
    if "impedancia" in data and data["impedancia"] is not None and data["impedancia"] != "":
        try:
            impedancia = float(data["impedancia"])
            if impedancia < 0 or impedancia > 100:
                errors.append("Impedância deve estar entre 0 e 100%")
        except (ValueError, TypeError):
            pass  # Já tratado na verificação anterior
    
    return len(errors) == 0, errors

def ensure_data_consistency(app, store_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Garante a consistência dos dados de um store.
    
    Args:
        app: Instância da aplicação Dash
        store_id: ID do store
        data: Dados a serem verificados
        
    Returns:
        Dict[str, Any]: Dados consistentes
    """
    if not app.mcp:
        return data
    
    # Clonar os dados para evitar modificações acidentais
    consistent_data = copy.deepcopy(data)
    
    # Se o store for transformer-inputs-store, validar os dados básicos
    if store_id == "transformer-inputs-store":
        valid, errors = validate_transformer_data(consistent_data)
        if not valid:
            log.warning(f"[ensure_data_consistency] Dados do transformer-inputs-store inválidos: {errors}")
            # Não corrigimos automaticamente, apenas logamos os erros
    
    # Se o store não for transformer-inputs-store, garantir que os dados básicos sejam consistentes
    else:
        # Obter dados da fonte-de-verdade
        auth_data = app.mcp.get_data("transformer-inputs-store") or {}
        
        # Se transformer_data não existir, criar
        if "transformer_data" not in consistent_data:
            consistent_data["transformer_data"] = {}
        
        # Garantir que os campos básicos sejam consistentes
        from utils.mcp_persistence_enhanced import BASIC_FIELDS
        for field in BASIC_FIELDS:
            if field in auth_data and auth_data[field] is not None:
                consistent_data["transformer_data"][field] = auth_data[field]
    
    return consistent_data

def check_data_integrity(app) -> Dict[str, List[str]]:
    """
    Verifica a integridade dos dados em todos os stores.
    
    Args:
        app: Instância da aplicação Dash
        
    Returns:
        Dict[str, List[str]]: Dicionário com erros por store
    """
    if not app.mcp:
        return {"error": ["MCP não inicializado"]}
    
    errors = {}
    
    # Verificar transformer-inputs-store
    transformer_data = app.mcp.get_data("transformer-inputs-store") or {}
    valid, transformer_errors = validate_transformer_data(transformer_data)
    if not valid:
        errors["transformer-inputs-store"] = transformer_errors
    
    # Verificar outros stores
    from utils.mcp_persistence_enhanced import ALL_STORES
    for store_id in ALL_STORES:
        if store_id == "transformer-inputs-store":
            continue
        
        store_data = app.mcp.get_data(store_id) or {}
        
        # Verificar se transformer_data existe
        if "transformer_data" not in store_data:
            if store_id not in errors:
                errors[store_id] = []
            errors[store_id].append("transformer_data não encontrado")
            continue
        
        # Verificar consistência com transformer-inputs-store
        transformer_data = app.mcp.get_data("transformer-inputs-store") or {}
        from utils.mcp_persistence_enhanced import BASIC_FIELDS
        for field in BASIC_FIELDS:
            if field in transformer_data and transformer_data[field] is not None:
                if field not in store_data["transformer_data"] or store_data["transformer_data"][field] != transformer_data[field]:
                    if store_id not in errors:
                        errors[store_id] = []
                    errors[store_id].append(f"Campo '{field}' inconsistente com transformer-inputs-store")
    
    return errors

def fix_data_integrity(app) -> Dict[str, bool]:
    """
    Corrige problemas de integridade dos dados em todos os stores.
    
    Args:
        app: Instância da aplicação Dash
        
    Returns:
        Dict[str, bool]: Dicionário com status de correção por store
    """
    if not app.mcp:
        return {"error": False}
    
    results = {}
    
    # Verificar e corrigir transformer-inputs-store
    transformer_data = app.mcp.get_data("transformer-inputs-store") or {}
    valid, transformer_errors = validate_transformer_data(transformer_data)
    if not valid:
        # Não corrigimos automaticamente o transformer-inputs-store,
        # pois isso poderia causar perda de dados
        results["transformer-inputs-store"] = False
    else:
        results["transformer-inputs-store"] = True
    
    # Corrigir outros stores
    from utils.mcp_persistence_enhanced import ALL_STORES, propagate_all_data
    
    # Propagar todos os dados da fonte-de-verdade para outros stores
    propagation_success = propagate_all_data(app)
    
    # Verificar se a propagação foi bem-sucedida
    for store_id in ALL_STORES:
        if store_id == "transformer-inputs-store":
            continue
        
        results[store_id] = propagation_success
    
    return results

def get_module_report_data(app, module_name: str) -> Dict[str, Any]:
    """
    Obtém os dados de um módulo para geração de relatório.
    
    Args:
        app: Instância da aplicação Dash
        module_name: Nome do módulo
        
    Returns:
        Dict[str, Any]: Dados do módulo para relatório
    """
    if not app.mcp:
        return {"error": "MCP não inicializado"}
    
    # Mapear nome do módulo para store_id
    module_store_map = {
        "transformer_inputs": "transformer-inputs-store",
        "losses": "losses-store",
        "impulse": "impulse-store",
        "dieletric_analysis": "dieletric-analysis-store",
        "applied_voltage": "applied-voltage-store",
        "induced_voltage": "induced-voltage-store",
        "short_circuit": "short-circuit-store",
        "temperature_rise": "temperature-rise-store",
        "comprehensive_analysis": "comprehensive-analysis-store",
    }
    
    store_id = module_store_map.get(module_name)
    if not store_id:
        return {"error": f"Módulo '{module_name}' não encontrado"}
    
    # Obter dados do módulo
    from utils.mcp_persistence_enhanced import get_module_data
    module_data = get_module_data(app, module_name)
    
    # Adicionar metadados para o relatório
    report_data = {
        "module_name": module_name,
        "store_id": store_id,
        "timestamp": logging.Formatter.formatTime(logging.Formatter(), logging.LogRecord('', 0, '', 0, None, None, None)),
        "data": module_data
    }
    
    return report_data

def get_all_modules_report_data(app) -> Dict[str, Dict[str, Any]]:
    """
    Obtém os dados de todos os módulos para geração de relatório completo.
    
    Args:
        app: Instância da aplicação Dash
        
    Returns:
        Dict[str, Dict[str, Any]]: Dados de todos os módulos para relatório
    """
    if not app.mcp:
        return {"error": {"error": "MCP não inicializado"}}
    
    # Lista de todos os módulos
    modules = [
        "transformer_inputs",
        "losses",
        "impulse",
        "dieletric_analysis",
        "applied_voltage",
        "induced_voltage",
        "short_circuit",
        "temperature_rise",
        "comprehensive_analysis",
    ]
    
    # Obter dados de todos os módulos
    report_data = {}
    for module_name in modules:
        report_data[module_name] = get_module_report_data(app, module_name)
    
    return report_data
