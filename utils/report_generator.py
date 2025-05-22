"""
Gerador de relatórios para o Transformer Test Simulator.
Permite gerar relatórios detalhados com inputs e outputs de cada módulo.
"""

import logging
import json
import os
import datetime
from typing import Dict, Any, List, Optional, Union
import pandas as pd
import matplotlib.pyplot as plt
from fpdf2 import FPDF
import base64
from io import BytesIO

log = logging.getLogger(__name__)

class TransformerReportGenerator:
    """
    Gerador de relatórios para o Transformer Test Simulator.
    """
    
    def __init__(self, app):
        """
        Inicializa o gerador de relatórios.
        
        Args:
            app: Instância da aplicação Dash
        """
        self.app = app
        self.report_data = {}
        self.report_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
        os.makedirs(self.report_dir, exist_ok=True)
    
    def collect_data(self) -> bool:
        """
        Coleta dados de todos os módulos para o relatório.
        
        Returns:
            bool: True se a coleta foi bem-sucedida, False caso contrário
        """
        if not hasattr(self.app, 'mcp') or self.app.mcp is None:
            log.error("[TransformerReportGenerator] MCP não inicializado")
            return False
        
        try:
            # Importar utilitário para obter dados de todos os módulos
            from utils.data_integrity import get_all_modules_report_data
            
            # Coletar dados
            self.report_data = get_all_modules_report_data(self.app)
            
            # Verificar se há dados
            if not self.report_data or "error" in self.report_data:
                log.error(f"[TransformerReportGenerator] Erro ao coletar dados: {self.report_data.get('error', 'Erro desconhecido')}")
                return False
            
            log.info(f"[TransformerReportGenerator] Dados coletados com sucesso para {len(self.report_data)} módulos")
            return True
        
        except Exception as e:
            log.error(f"[TransformerReportGenerator] Erro ao coletar dados: {e}")
            return False
    
    def generate_html_report(self, output_path: Optional[str] = None) -> str:
        """
        Gera um relatório em formato HTML.
        
        Args:
            output_path: Caminho para salvar o relatório. Se None, usa um nome padrão.
            
        Returns:
            str: Caminho do relatório gerado
        """
        if not self.report_data:
            success = self.collect_data()
            if not success:
                log.error("[TransformerReportGenerator] Falha ao coletar dados para o relatório HTML")
                return ""
        
        # Definir caminho de saída
        if output_path is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.report_dir, f"transformer_report_{timestamp}.html")
        
        try:
            # Iniciar HTML
            html = """
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Relatório de Simulação de Transformador</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        margin: 0;
                        padding: 20px;
                        color: #333;
                    }
                    h1 {
                        color: #2c3e50;
                        border-bottom: 2px solid #3498db;
                        padding-bottom: 10px;
                    }
                    h2 {
                        color: #2980b9;
                        margin-top: 30px;
                        border-left: 4px solid #3498db;
                        padding-left: 10px;
                    }
                    h3 {
                        color: #3498db;
                        margin-top: 20px;
                    }
                    table {
                        border-collapse: collapse;
                        width: 100%;
                        margin: 20px 0;
                    }
                    th, td {
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                    }
                    th {
                        background-color: #f2f2f2;
                        color: #333;
                    }
                    tr:nth-child(even) {
                        background-color: #f9f9f9;
                    }
                    .section {
                        margin-bottom: 30px;
                        padding: 15px;
                        background-color: #f8f9fa;
                        border-radius: 5px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }
                    .timestamp {
                        color: #7f8c8d;
                        font-style: italic;
                        margin-bottom: 20px;
                    }
                    .chart-container {
                        margin: 20px 0;
                        text-align: center;
                    }
                    .chart-container img {
                        max-width: 100%;
                        height: auto;
                    }
                </style>
            </head>
            <body>
                <h1>Relatório de Simulação de Transformador</h1>
                <div class="timestamp">
                    Gerado em: """ + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + """
                </div>
            """
            
            # Obter dados do transformador
            transformer_data = self.report_data.get("transformer_inputs", {}).get("data", {})
            
            # Seção de dados básicos
            html += """
                <div class="section">
                    <h2>1. Dados Básicos do Transformador</h2>
            """
            
            # Tabela de dados básicos
            html += """
                    <table>
                        <tr>
                            <th>Parâmetro</th>
                            <th>Valor</th>
                        </tr>
            """
            
            # Mapear campos importantes e seus rótulos
            basic_fields = [
                ("tipo_transformador", "Tipo de Transformador"),
                ("potencia_mva", "Potência (MVA)"),
                ("tensao_at", "Tensão AT (kV)"),
                ("tensao_bt", "Tensão BT (kV)"),
                ("tensao_terciario", "Tensão Terciário (kV)"),
                ("frequencia", "Frequência (Hz)"),
                ("conexao_at", "Conexão AT"),
                ("conexao_bt", "Conexão BT"),
                ("conexao_terciario", "Conexão Terciário"),
                ("grupo_ligacao", "Grupo de Ligação"),
                ("impedancia", "Impedância (%)"),
                ("corrente_nominal_at", "Corrente Nominal AT (A)"),
                ("corrente_nominal_bt", "Corrente Nominal BT (A)"),
                ("corrente_nominal_terciario", "Corrente Nominal Terciário (A)"),
                ("liquido_isolante", "Líquido Isolante"),
                ("tipo_isolamento", "Tipo de Isolamento"),
            ]
            
            for field, label in basic_fields:
                value = transformer_data.get(field, "")
                if value is not None and value != "":
                    html += f"""
                        <tr>
                            <td>{label}</td>
                            <td>{value}</td>
                        </tr>
                    """
            
            html += """
                    </table>
                </div>
            """
            
            # Seção de perdas
            losses_data = self.report_data.get("losses", {}).get("data", {})
            if losses_data:
                html += """
                    <div class="section">
                        <h2>2. Perdas</h2>
                """
                
                # Extrair dados específicos de perdas
                losses_specific = losses_data.get("transformer_data", {})
                
                # Tabela de perdas
                html += """
                        <table>
                            <tr>
                                <th>Parâmetro</th>
                                <th>Valor</th>
                            </tr>
                """
                
                # Mapear campos de perdas e seus rótulos
                losses_fields = [
                    ("perdas_vazio", "Perdas em Vazio (W)"),
                    ("perdas_carga", "Perdas em Carga (W)"),
                    ("corrente_excitacao", "Corrente de Excitação (%)"),
                    ("potencia_magnetica", "Potência Magnética (VA)"),
                    ("tensao_curto_circuito", "Tensão de Curto-Circuito (%)"),
                    ("eficiencia_plena_carga", "Eficiência a Plena Carga (%)"),
                    ("eficiencia_75_carga", "Eficiência a 75% da Carga (%)"),
                    ("eficiencia_50_carga", "Eficiência a 50% da Carga (%)"),
                    ("eficiencia_25_carga", "Eficiência a 25% da Carga (%)"),
                ]
                
                for field, label in losses_fields:
                    value = losses_specific.get(field, "")
                    if value is not None and value != "":
                        html += f"""
                            <tr>
                                <td>{label}</td>
                                <td>{value}</td>
                            </tr>
                        """
                
                html += """
                        </table>
                    </div>
                """
            
            # Seção de impulso
            impulse_data = self.report_data.get("impulse", {}).get("data", {})
            if impulse_data:
                html += """
                    <div class="section">
                        <h2>3. Impulso</h2>
                """
                
                # Extrair dados específicos de impulso
                impulse_specific = impulse_data.get("transformer_data", {})
                
                # Tabela de impulso
                html += """
                        <table>
                            <tr>
                                <th>Parâmetro</th>
                                <th>Valor</th>
                            </tr>
                """
                
                # Mapear campos de impulso e seus rótulos
                impulse_fields = [
                    ("parametro_r_equivalente", "Resistência Equivalente (Ω)"),
                    ("parametro_l_equivalente", "Indutância Equivalente (H)"),
                    ("parametro_c_equivalente", "Capacitância Equivalente (F)"),
                    ("eficiencia_circuito", "Eficiência do Circuito (%)"),
                    ("energia_ensaio_li", "Energia para Ensaio LI (J)"),
                    ("energia_ensaio_si", "Energia para Ensaio SI (J)"),
                    ("energia_ensaio_lic", "Energia para Ensaio LIC (J)"),
                ]
                
                for field, label in impulse_fields:
                    value = impulse_specific.get(field, "")
                    if value is not None and value != "":
                        html += f"""
                            <tr>
                                <td>{label}</td>
                                <td>{value}</td>
                            </tr>
                        """
                
                html += """
                        </table>
                    </div>
                """
            
            # Seção de análise dielétrica
            dieletric_data = self.report_data.get("dieletric_analysis", {}).get("data", {})
            if dieletric_data:
                html += """
                    <div class="section">
                        <h2>4. Análise Dielétrica</h2>
                """
                
                # Extrair dados específicos de análise dielétrica
                dieletric_specific = dieletric_data.get("transformer_data", {})
                
                # Tabela de análise dielétrica
                html += """
                        <table>
                            <tr>
                                <th>Parâmetro</th>
                                <th>Valor</th>
                            </tr>
                """
                
                # Mapear campos de análise dielétrica e seus rótulos
                dieletric_fields = [
                    ("espacamento_minimo_at_bt", "Espaçamento Mínimo AT-BT (mm)"),
                    ("espacamento_minimo_at_terra", "Espaçamento Mínimo AT-Terra (mm)"),
                    ("espacamento_minimo_bt_terra", "Espaçamento Mínimo BT-Terra (mm)"),
                    ("rigidez_dieletrica_oleo", "Rigidez Dielétrica do Óleo (kV/mm)"),
                    ("rigidez_dieletrica_papel", "Rigidez Dielétrica do Papel (kV/mm)"),
                    ("fator_correcao_altitude", "Fator de Correção para Altitude"),
                ]
                
                for field, label in dieletric_fields:
                    value = dieletric_specific.get(field, "")
                    if value is not None and value != "":
                        html += f"""
                            <tr>
                                <td>{label}</td>
                                <td>{value}</td>
                            </tr>
                        """
                
                html += """
                        </table>
                    </div>
                """
            
            # Seção de tensão aplicada
            applied_voltage_data = self.report_data.get("applied_voltage", {}).get("data", {})
            if applied_voltage_data:
                html += """
                    <div class="section">
                        <h2>5. Tensão Aplicada</h2>
                """
                
                # Extrair dados específicos de tensão aplicada
                applied_voltage_specific = applied_voltage_data.get("transformer_data", {})
                
                # Tabela de tensão aplicada
                html += """
                        <table>
                            <tr>
                                <th>Parâmetro</th>
                                <th>Valor</th>
                            </tr>
                """
                
                # Mapear campos de tensão aplicada e seus rótulos
                applied_voltage_fields = [
                    ("impedancia_capacitiva", "Impedância Capacitiva (Ω)"),
                    ("corrente_ensaio_ta", "Corrente para Ensaio TA (A)"),
                    ("potencia_reativa_ta", "Potência Reativa para TA (kVAr)"),
                    ("viabilidade_sistema_ressonante", "Viabilidade com Sistema Ressonante"),
                ]
                
                for field, label in applied_voltage_fields:
                    value = applied_voltage_specific.get(field, "")
                    if value is not None and value != "":
                        html += f"""
                            <tr>
                                <td>{label}</td>
                                <td>{value}</td>
                            </tr>
                        """
                
                html += """
                        </table>
                    </div>
                """
            
            # Seção de tensão induzida
            induced_voltage_data = self.report_data.get("induced_voltage", {}).get("data", {})
            if induced_voltage_data:
                html += """
                    <div class="section">
                        <h2>6. Tensão Induzida</h2>
                """
                
                # Extrair dados específicos de tensão induzida
                induced_voltage_specific = induced_voltage_data.get("transformer_data", {})
                
                # Tabela de tensão induzida
                html += """
                        <table>
                            <tr>
                                <th>Parâmetro</th>
                                <th>Valor</th>
                            </tr>
                """
                
                # Mapear campos de tensão induzida e seus rótulos
                induced_voltage_fields = [
                    ("frequencia_otima", "Frequência Ótima (Hz)"),
                    ("carga_capacitiva", "Carga Capacitiva (µF)"),
                    ("potencia_reativa_ti", "Potência Reativa para TI (kVAr)"),
                ]
                
                for field, label in induced_voltage_fields:
                    value = induced_voltage_specific.get(field, "")
                    if value is not None and value != "":
                        html += f"""
                            <tr>
                                <td>{label}</td>
                                <td>{value}</td>
                            </tr>
                        """
                
                html += """
                        </table>
                    </div>
                """
            
            # Seção de curto-circuito
            short_circuit_data = self.report_data.get("short_circuit", {}).get("data", {})
            if short_circuit_data:
                html += """
                    <div class="section">
                        <h2>7. Curto-Circuito</h2>
                """
                
                # Extrair dados específicos de curto-circuito
                short_circuit_specific = short_circuit_data.get("transformer_data", {})
                
                # Tabela de curto-circuito
                html += """
                        <table>
                            <tr>
                                <th>Parâmetro</th>
                                <th>Valor</th>
                            </tr>
                """
                
                # Mapear campos de curto-circuito e seus rótulos
                short_circuit_fields = [
                    ("corrente_curto_circuito_at", "Corrente de Curto-Circuito AT (kA)"),
                    ("corrente_curto_circuito_bt", "Corrente de Curto-Circuito BT (kA)"),
                    ("suportabilidade_mecanica", "Suportabilidade Mecânica (%)"),
                    ("variacao_impedancia", "Variação de Impedância (%)"),
                ]
                
                for field, label in short_circuit_fields:
                    value = short_circuit_specific.get(field, "")
                    if value is not None and value != "":
                        html += f"""
                            <tr>
                                <td>{label}</td>
                                <td>{value}</td>
                            </tr>
                        """
                
                html += """
                        </table>
                    </div>
                """
            
            # Seção de elevação de temperatura
            temperature_rise_data = self.report_data.get("temperature_rise", {}).get("data", {})
            if temperature_rise_data:
                html += """
                    <div class="section">
                        <h2>8. Elevação de Temperatura</h2>
                """
                
                # Extrair dados específicos de elevação de temperatura
                temperature_rise_specific = temperature_rise_data.get("transformer_data", {})
                
                # Tabela de elevação de temperatura
                html += """
                        <table>
                            <tr>
                                <th>Parâmetro</th>
                                <th>Valor</th>
                            </tr>
                """
                
                # Mapear campos de elevação de temperatura e seus rótulos
                temperature_rise_fields = [
                    ("constante_termica_oleo", "Constante Térmica do Óleo (min)"),
                    ("constante_termica_enrolamento", "Constante Térmica do Enrolamento (min)"),
                    ("elevacao_temperatura_oleo", "Elevação de Temperatura do Óleo (°C)"),
                    ("elevacao_temperatura_enrolamento_at", "Elevação de Temperatura do Enrolamento AT (°C)"),
                    ("elevacao_temperatura_enrolamento_bt", "Elevação de Temperatura do Enrolamento BT (°C)"),
                    ("elevacao_temperatura_enrolamento_terciario", "Elevação de Temperatura do Enrolamento Terciário (°C)"),
                    ("conformidade_limites_normativos", "Conformidade com Limites Normativos"),
                ]
                
                for field, label in temperature_rise_fields:
                    value = temperature_rise_specific.get(field, "")
                    if value is not None and value != "":
                        html += f"""
                            <tr>
                                <td>{label}</td>
                                <td>{value}</td>
                            </tr>
                        """
                
                html += """
                        </table>
                    </div>
                """
            
            # Seção de análise abrangente
            comprehensive_data = self.report_data.get("comprehensive_analysis", {}).get("data", {})
            if comprehensive_data:
                html += """
                    <div class="section">
                        <h2>10. Análise Abrangente</h2>
                """
                
                # Extrair dados específicos de análise abrangente
                comprehensive_specific = comprehensive_data.get("transformer_data", {})
                
                # Tabela de análise abrangente
                html += """
                        <table>
                            <tr>
                                <th>Parâmetro</th>
                                <th>Valor</th>
                            </tr>
                """
                
                # Mapear campos de análise abrangente e seus rótulos
                comprehensive_fields = [
                    ("conformidade_geral", "Conformidade Geral"),
                    ("observacoes", "Observações"),
                    ("recomendacoes", "Recomendações"),
                ]
                
                for field, label in comprehensive_fields:
                    value = comprehensive_specific.get(field, "")
                    if value is not None and value != "":
                        html += f"""
                            <tr>
                                <td>{label}</td>
                                <td>{value}</td>
                            </tr>
                        """
                
                html += """
                        </table>
                    </div>
                """
            
            # Finalizar HTML
            html += """
            </body>
            </html>
            """
            
            # Salvar HTML
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html)
            
            log.info(f"[TransformerReportGenerator] Relatório HTML gerado com sucesso: {output_path}")
            return output_path
        
        except Exception as e:
            log.error(f"[TransformerReportGenerator] Erro ao gerar relatório HTML: {e}")
            return ""
    
    def generate_pdf_report(self, output_path: Optional[str] = None) -> str:
        """
        Gera um relatório em formato PDF.
        
        Args:
            output_path: Caminho para salvar o relatório. Se None, usa um nome padrão.
            
        Returns:
            str: Caminho do relatório gerado
        """
        if not self.report_data:
            success = self.collect_data()
            if not success:
                log.error("[TransformerReportGenerator] Falha ao coletar dados para o relatório PDF")
                return ""
        
        # Definir caminho de saída
        if output_path is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.report_dir, f"transformer_report_{timestamp}.pdf")
        
        try:
            # Criar PDF
            pdf = FPDF()
            pdf.add_page()
            
            # Configurar fonte
            pdf.add_font('DejaVu', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', uni=True)
            pdf.set_font('DejaVu', '', 12)
            
            # Título
            pdf.set_font('DejaVu', '', 16)
            pdf.cell(0, 10, "Relatório de Simulação de Transformador", 0, 1, 'C')
            pdf.ln(5)
            
            # Data e hora
            pdf.set_font('DejaVu', '', 10)
            pdf.cell(0, 10, f"Gerado em: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 0, 1, 'R')
            pdf.ln(5)
            
            # Obter dados do transformador
            transformer_data = self.report_data.get("transformer_inputs", {}).get("data", {})
            
            # Seção de dados básicos
            pdf.set_font('DejaVu', '', 14)
            pdf.cell(0, 10, "1. Dados Básicos do Transformador", 0, 1, 'L')
            pdf.ln(2)
            
            # Tabela de dados básicos
            pdf.set_font('DejaVu', '', 10)
            
            # Mapear campos importantes e seus rótulos
            basic_fields = [
                ("tipo_transformador", "Tipo de Transformador"),
                ("potencia_mva", "Potência (MVA)"),
                ("tensao_at", "Tensão AT (kV)"),
                ("tensao_bt", "Tensão BT (kV)"),
                ("tensao_terciario", "Tensão Terciário (kV)"),
                ("frequencia", "Frequência (Hz)"),
                ("conexao_at", "Conexão AT"),
                ("conexao_bt", "Conexão BT"),
                ("conexao_terciario", "Conexão Terciário"),
                ("grupo_ligacao", "Grupo de Ligação"),
                ("impedancia", "Impedância (%)"),
                ("corrente_nominal_at", "Corrente Nominal AT (A)"),
                ("corrente_nominal_bt", "Corrente Nominal BT (A)"),
                ("corrente_nominal_terciario", "Corrente Nominal Terciário (A)"),
                ("liquido_isolante", "Líquido Isolante"),
                ("tipo_isolamento", "Tipo de Isolamento"),
            ]
            
            for field, label in basic_fields:
                value = transformer_data.get(field, "")
                if value is not None and value != "":
                    pdf.cell(90, 8, label, 1, 0, 'L')
                    pdf.cell(90, 8, str(value), 1, 1, 'L')
            
            pdf.ln(5)
            
            # Seção de perdas
            losses_data = self.report_data.get("losses", {}).get("data", {})
            if losses_data:
                pdf.set_font('DejaVu', '', 14)
                pdf.cell(0, 10, "2. Perdas", 0, 1, 'L')
                pdf.ln(2)
                
                # Extrair dados específicos de perdas
                losses_specific = losses_data.get("transformer_data", {})
                
                # Tabela de perdas
                pdf.set_font('DejaVu', '', 10)
                
                # Mapear campos de perdas e seus rótulos
                losses_fields = [
                    ("perdas_vazio", "Perdas em Vazio (W)"),
                    ("perdas_carga", "Perdas em Carga (W)"),
                    ("corrente_excitacao", "Corrente de Excitação (%)"),
                    ("potencia_magnetica", "Potência Magnética (VA)"),
                    ("tensao_curto_circuito", "Tensão de Curto-Circuito (%)"),
                    ("eficiencia_plena_carga", "Eficiência a Plena Carga (%)"),
                    ("eficiencia_75_carga", "Eficiência a 75% da Carga (%)"),
                    ("eficiencia_50_carga", "Eficiência a 50% da Carga (%)"),
                    ("eficiencia_25_carga", "Eficiência a 25% da Carga (%)"),
                ]
                
                for field, label in losses_fields:
                    value = losses_specific.get(field, "")
                    if value is not None and value != "":
                        pdf.cell(90, 8, label, 1, 0, 'L')
                        pdf.cell(90, 8, str(value), 1, 1, 'L')
                
                pdf.ln(5)
            
            # Continuar com as demais seções...
            # (Código similar para as outras seções)
            
            # Salvar PDF
            pdf.output(output_path)
            
            log.info(f"[TransformerReportGenerator] Relatório PDF gerado com sucesso: {output_path}")
            return output_path
        
        except Exception as e:
            log.error(f"[TransformerReportGenerator] Erro ao gerar relatório PDF: {e}")
            return ""
    
    def generate_excel_report(self, output_path: Optional[str] = None) -> str:
        """
        Gera um relatório em formato Excel.
        
        Args:
            output_path: Caminho para salvar o relatório. Se None, usa um nome padrão.
            
        Returns:
            str: Caminho do relatório gerado
        """
        if not self.report_data:
            success = self.collect_data()
            if not success:
                log.error("[TransformerReportGenerator] Falha ao coletar dados para o relatório Excel")
                return ""
        
        # Definir caminho de saída
        if output_path is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.report_dir, f"transformer_report_{timestamp}.xlsx")
        
        try:
            # Criar Excel writer
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Dados básicos
                transformer_data = self.report_data.get("transformer_inputs", {}).get("data", {})
                basic_data = []
                
                # Mapear campos importantes e seus rótulos
                basic_fields = [
                    ("tipo_transformador", "Tipo de Transformador"),
                    ("potencia_mva", "Potência (MVA)"),
                    ("tensao_at", "Tensão AT (kV)"),
                    ("tensao_bt", "Tensão BT (kV)"),
                    ("tensao_terciario", "Tensão Terciário (kV)"),
                    ("frequencia", "Frequência (Hz)"),
                    ("conexao_at", "Conexão AT"),
                    ("conexao_bt", "Conexão BT"),
                    ("conexao_terciario", "Conexão Terciário"),
                    ("grupo_ligacao", "Grupo de Ligação"),
                    ("impedancia", "Impedância (%)"),
                    ("corrente_nominal_at", "Corrente Nominal AT (A)"),
                    ("corrente_nominal_bt", "Corrente Nominal BT (A)"),
                    ("corrente_nominal_terciario", "Corrente Nominal Terciário (A)"),
                    ("liquido_isolante", "Líquido Isolante"),
                    ("tipo_isolamento", "Tipo de Isolamento"),
                ]
                
                for field, label in basic_fields:
                    value = transformer_data.get(field, "")
                    if value is not None:
                        basic_data.append({"Parâmetro": label, "Valor": value})
                
                # Criar DataFrame e salvar na planilha
                if basic_data:
                    df_basic = pd.DataFrame(basic_data)
                    df_basic.to_excel(writer, sheet_name="Dados Básicos", index=False)
                
                # Perdas
                losses_data = self.report_data.get("losses", {}).get("data", {})
                if losses_data:
                    losses_specific = losses_data.get("transformer_data", {})
                    losses_data_list = []
                    
                    # Mapear campos de perdas e seus rótulos
                    losses_fields = [
                        ("perdas_vazio", "Perdas em Vazio (W)"),
                        ("perdas_carga", "Perdas em Carga (W)"),
                        ("corrente_excitacao", "Corrente de Excitação (%)"),
                        ("potencia_magnetica", "Potência Magnética (VA)"),
                        ("tensao_curto_circuito", "Tensão de Curto-Circuito (%)"),
                        ("eficiencia_plena_carga", "Eficiência a Plena Carga (%)"),
                        ("eficiencia_75_carga", "Eficiência a 75% da Carga (%)"),
                        ("eficiencia_50_carga", "Eficiência a 50% da Carga (%)"),
                        ("eficiencia_25_carga", "Eficiência a 25% da Carga (%)"),
                    ]
                    
                    for field, label in losses_fields:
                        value = losses_specific.get(field, "")
                        if value is not None:
                            losses_data_list.append({"Parâmetro": label, "Valor": value})
                    
                    # Criar DataFrame e salvar na planilha
                    if losses_data_list:
                        df_losses = pd.DataFrame(losses_data_list)
                        df_losses.to_excel(writer, sheet_name="Perdas", index=False)
                
                # Continuar com as demais seções...
                # (Código similar para as outras seções)
            
            log.info(f"[TransformerReportGenerator] Relatório Excel gerado com sucesso: {output_path}")
            return output_path
        
        except Exception as e:
            log.error(f"[TransformerReportGenerator] Erro ao gerar relatório Excel: {e}")
            return ""
