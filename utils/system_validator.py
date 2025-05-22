"""
Módulo de integração para validar o funcionamento geral do sistema.
Permite testar a persistência, propagação automática e geração de relatórios.
"""

import logging
import os
import json
import time
from typing import Dict, Any, List, Optional, Tuple

log = logging.getLogger(__name__)

class SystemValidator:
    """
    Validador do sistema para testar o funcionamento geral.
    """
    
    def __init__(self, app):
        """
        Inicializa o validador do sistema.
        
        Args:
            app: Instância da aplicação Dash
        """
        self.app = app
        self.validation_results = {}
        self.test_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test_data")
        os.makedirs(self.test_data_dir, exist_ok=True)
    
    def validate_persistence(self) -> Tuple[bool, List[str]]:
        """
        Valida a persistência dos dados.
        
        Returns:
            Tuple[bool, List[str]]: (sucesso, mensagens)
        """
        messages = []
        
        try:
            if not hasattr(self.app, 'mcp') or self.app.mcp is None:
                messages.append("MCP não inicializado")
                return False, messages
            
            # Testar salvamento e carregamento do disco
            test_data = {
                "test_field": "test_value",
                "test_number": 123,
                "test_list": [1, 2, 3],
                "test_dict": {"a": 1, "b": 2}
            }
            
            # Salvar dados de teste no transformer-inputs-store
            original_data = self.app.mcp.get_data("transformer-inputs-store")
            self.app.mcp.set_data("transformer-inputs-store", test_data)
            
            # Salvar no disco
            save_success = self.app.mcp.save_to_disk(force=True)
            if not save_success:
                messages.append("Falha ao salvar dados no disco")
                # Restaurar dados originais
                self.app.mcp.set_data("transformer-inputs-store", original_data)
                return False, messages
            
            messages.append("Dados salvos no disco com sucesso")
            
            # Limpar dados
            self.app.mcp.set_data("transformer-inputs-store", {})
            
            # Carregar do disco
            load_success = self.app.mcp._load_from_disk()
            if not load_success:
                messages.append("Falha ao carregar dados do disco")
                # Restaurar dados originais
                self.app.mcp.set_data("transformer-inputs-store", original_data)
                return False, messages
            
            # Verificar se os dados foram carregados corretamente
            loaded_data = self.app.mcp.get_data("transformer-inputs-store")
            if not loaded_data or "test_field" not in loaded_data or loaded_data["test_field"] != "test_value":
                messages.append("Dados carregados não correspondem aos dados salvos")
                # Restaurar dados originais
                self.app.mcp.set_data("transformer-inputs-store", original_data)
                return False, messages
            
            messages.append("Dados carregados do disco com sucesso")
            
            # Restaurar dados originais
            self.app.mcp.set_data("transformer-inputs-store", original_data)
            self.app.mcp.save_to_disk(force=True)
            
            messages.append("Persistência validada com sucesso")
            return True, messages
        
        except Exception as e:
            messages.append(f"Erro ao validar persistência: {e}")
            return False, messages
    
    def validate_propagation(self) -> Tuple[bool, List[str]]:
        """
        Valida a propagação automática de dados entre módulos.
        
        Returns:
            Tuple[bool, List[str]]: (sucesso, mensagens)
        """
        messages = []
        
        try:
            if not hasattr(self.app, 'mcp') or self.app.mcp is None:
                messages.append("MCP não inicializado")
                return False, messages
            
            # Obter dados originais
            original_data = {}
            for store_id in ["transformer-inputs-store", "losses-store", "impulse-store"]:
                original_data[store_id] = self.app.mcp.get_data(store_id)
            
            # Criar dados de teste para transformer-inputs-store
            test_data = {
                "potencia_mva": 100.0,
                "tensao_at": 138.0,
                "tensao_bt": 13.8,
                "frequencia": 60.0,
                "tipo_transformador": "Trifásico",
                "conexao_at": "estrela",
                "conexao_bt": "triangulo",
                "impedancia": 10.0,
                "corrente_nominal_at": 418.37,
                "corrente_nominal_bt": 4183.7,
                "test_propagation": "test_value"
            }
            
            # Salvar dados de teste no transformer-inputs-store
            self.app.mcp.set_data("transformer-inputs-store", test_data, auto_propagate=True, app_instance=self.app)
            messages.append("Dados de teste salvos no transformer-inputs-store")
            
            # Verificar se os dados foram propagados para outros stores
            from utils.mcp_persistence_enhanced import BASIC_FIELDS
            
            propagation_success = True
            for store_id in ["losses-store", "impulse-store"]:
                store_data = self.app.mcp.get_data(store_id)
                
                # Verificar se transformer_data existe
                if "transformer_data" not in store_data:
                    messages.append(f"transformer_data não encontrado em {store_id}")
                    propagation_success = False
                    continue
                
                # Verificar se os campos básicos foram propagados
                for field in BASIC_FIELDS:
                    if field in test_data and test_data[field] is not None:
                        if field not in store_data["transformer_data"] or store_data["transformer_data"][field] != test_data[field]:
                            messages.append(f"Campo '{field}' não propagado corretamente para {store_id}")
                            propagation_success = False
            
            if propagation_success:
                messages.append("Dados propagados com sucesso para outros stores")
            
            # Restaurar dados originais
            for store_id, data in original_data.items():
                self.app.mcp.set_data(store_id, data)
            
            if propagation_success:
                messages.append("Propagação automática validada com sucesso")
                return True, messages
            else:
                return False, messages
        
        except Exception as e:
            messages.append(f"Erro ao validar propagação: {e}")
            return False, messages
    
    def validate_data_integrity(self) -> Tuple[bool, List[str]]:
        """
        Valida a integridade dos dados.
        
        Returns:
            Tuple[bool, List[str]]: (sucesso, mensagens)
        """
        messages = []
        
        try:
            if not hasattr(self.app, 'mcp') or self.app.mcp is None:
                messages.append("MCP não inicializado")
                return False, messages
            
            # Importar utilitário de integridade de dados
            from utils.data_integrity import check_data_integrity, fix_data_integrity
            
            # Verificar integridade dos dados
            integrity_errors = check_data_integrity(self.app)
            
            if not integrity_errors:
                messages.append("Nenhum problema de integridade encontrado")
            else:
                messages.append(f"Problemas de integridade encontrados: {json.dumps(integrity_errors, indent=2)}")
                
                # Tentar corrigir problemas de integridade
                fix_results = fix_data_integrity(self.app)
                
                if all(fix_results.values()):
                    messages.append("Todos os problemas de integridade foram corrigidos")
                else:
                    messages.append(f"Alguns problemas de integridade não puderam ser corrigidos: {json.dumps(fix_results, indent=2)}")
                    return False, messages
            
            messages.append("Integridade de dados validada com sucesso")
            return True, messages
        
        except Exception as e:
            messages.append(f"Erro ao validar integridade de dados: {e}")
            return False, messages
    
    def validate_report_generation(self) -> Tuple[bool, List[str]]:
        """
        Valida a geração de relatórios.
        
        Returns:
            Tuple[bool, List[str]]: (sucesso, mensagens)
        """
        messages = []
        
        try:
            if not hasattr(self.app, 'mcp') or self.app.mcp is None:
                messages.append("MCP não inicializado")
                return False, messages
            
            # Importar gerador de relatórios
            from utils.report_generator import TransformerReportGenerator
            
            # Criar gerador de relatórios
            report_generator = TransformerReportGenerator(self.app)
            
            # Coletar dados
            collect_success = report_generator.collect_data()
            if not collect_success:
                messages.append("Falha ao coletar dados para o relatório")
                return False, messages
            
            messages.append("Dados coletados com sucesso para o relatório")
            
            # Gerar relatório HTML
            html_path = report_generator.generate_html_report()
            if not html_path or not os.path.exists(html_path):
                messages.append("Falha ao gerar relatório HTML")
                return False, messages
            
            messages.append(f"Relatório HTML gerado com sucesso: {html_path}")
            
            # Gerar relatório PDF
            pdf_path = report_generator.generate_pdf_report()
            if not pdf_path or not os.path.exists(pdf_path):
                messages.append("Falha ao gerar relatório PDF")
                return False, messages
            
            messages.append(f"Relatório PDF gerado com sucesso: {pdf_path}")
            
            # Gerar relatório Excel
            excel_path = report_generator.generate_excel_report()
            if not excel_path or not os.path.exists(excel_path):
                messages.append("Falha ao gerar relatório Excel")
                return False, messages
            
            messages.append(f"Relatório Excel gerado com sucesso: {excel_path}")
            
            messages.append("Geração de relatórios validada com sucesso")
            return True, messages
        
        except Exception as e:
            messages.append(f"Erro ao validar geração de relatórios: {e}")
            return False, messages
    
    def validate_all(self) -> Dict[str, Any]:
        """
        Valida todos os aspectos do sistema.
        
        Returns:
            Dict[str, Any]: Resultados da validação
        """
        results = {}
        
        # Validar persistência
        persistence_success, persistence_messages = self.validate_persistence()
        results["persistence"] = {
            "success": persistence_success,
            "messages": persistence_messages
        }
        
        # Validar propagação
        propagation_success, propagation_messages = self.validate_propagation()
        results["propagation"] = {
            "success": propagation_success,
            "messages": propagation_messages
        }
        
        # Validar integridade de dados
        integrity_success, integrity_messages = self.validate_data_integrity()
        results["integrity"] = {
            "success": integrity_success,
            "messages": integrity_messages
        }
        
        # Validar geração de relatórios
        report_success, report_messages = self.validate_report_generation()
        results["report"] = {
            "success": report_success,
            "messages": report_messages
        }
        
        # Resultado geral
        results["overall"] = {
            "success": persistence_success and propagation_success and integrity_success and report_success,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.validation_results = results
        return results
    
    def save_validation_results(self, output_path: Optional[str] = None) -> str:
        """
        Salva os resultados da validação em um arquivo JSON.
        
        Args:
            output_path: Caminho para salvar os resultados. Se None, usa um nome padrão.
            
        Returns:
            str: Caminho do arquivo salvo
        """
        if not self.validation_results:
            self.validate_all()
        
        # Definir caminho de saída
        if output_path is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.test_data_dir, f"validation_results_{timestamp}.json")
        
        try:
            # Salvar resultados
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(self.validation_results, f, indent=2)
            
            log.info(f"[SystemValidator] Resultados da validação salvos com sucesso: {output_path}")
            return output_path
        
        except Exception as e:
            log.error(f"[SystemValidator] Erro ao salvar resultados da validação: {e}")
            return ""
