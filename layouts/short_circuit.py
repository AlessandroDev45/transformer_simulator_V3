# layouts/short_circuit.py
"""
Defines the layout for the Short-Circuit Withstand section as a function.
"""
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.express as px # For the initial empty graph

# Remove broken imports for helpers and define local fallbacks

def create_help_button(module_name, tooltip_text):
    return None

def create_labeled_input(label, input_id, input_type="number", value=None, min=None, max=None, step=None, label_width=6, input_width=6, placeholder=None, style=None, persistence=True, persistence_type="local"):
    import dash_bootstrap_components as dbc
    from dash import html
    return dbc.Row([
        dbc.Col(dbc.Label(label, style={"fontSize": "0.75rem", "color": "#e0e0e0"}), width=label_width),
        dbc.Col(dbc.Input(id=input_id, type=input_type, value=value, min=min, max=max, step=step, placeholder=placeholder, style=style, persistence=persistence, persistence_type=persistence_type), width=input_width)
    ], className="mb-1")

# --- Paleta de Cores Escura Completa (garante todas as chaves usadas) ---
COLORS = {
    "primary": "#26427A",
    "secondary": "#6c757d",
    "accent": "#00BFFF",
    "accent_alt": "#FFD700",
    "background_main": "#1a1a1a",
    "background_card": "#2c2c2c",
    "background_card_header": "#1f1f1f",
    "background_input": "#3a3a3a",
    "background_header": "#1f1f1f",
    "background_faint": "#333333",
    "text_light": "#e0e0e0",
    "text_dark": "#e0e0e0",
    "text_muted": "#a0a0a0",
    "text_header": "#FFFFFF",
    "border": "#444444",
    "border_light": "#555555",
    "border_strong": "#666666",
    "success": "#28a745",
    "danger": "#dc3545",
    "warning": "#ffc107",
    "info": "#00BFFF",
    "pass": "#28a745",
    "fail": "#dc3545",
    "pass_bg": "rgba(40, 167, 69, 0.2)",
    "fail_bg": "rgba(220, 53, 69, 0.2)",
    "warning_bg": "rgba(255, 193, 7, 0.2)",
}
COMPONENTS = {
    "card": {"backgroundColor": COLORS["background_card"], "border": f'1px solid {COLORS["border"]}', "borderRadius": "4px", "boxShadow": "0 2px 5px rgba(0,0,0,0.25)", "marginBottom": "0.75rem"},
    "card_header": {"backgroundColor": COLORS["background_card_header"], "color": COLORS["text_header"], "padding": "0.4rem 0.75rem", "fontSize": "1rem", "fontWeight": "bold", "letterSpacing": "0.02em", "textTransform": "uppercase", "borderBottom": f'1px solid {COLORS["border_strong"]}'},
    "card_body": {"padding": "0.75rem", "backgroundColor": COLORS["background_card"]},
    "button": {"backgroundColor": COLORS["primary"], "color": COLORS["text_header"]},
    "dropdown": {"backgroundColor": COLORS["background_input"], "color": COLORS["text_light"], "border": f'1px solid {COLORS["border"]}', "borderRadius": "3px"}
}
TYPOGRAPHY = {
    "label": {"fontSize": "0.75rem", "fontWeight": "500"},
    "section_title": {"fontSize": "0.9rem", "fontWeight": "bold", "marginTop": "1rem", "marginBottom": "0.5rem"},
    "card_header": {"fontSize": "1rem", "fontWeight": "bold"},
    "title": {"fontSize": "1.1rem", "fontWeight": "bold", "color": COLORS["accent"]}
}
SPACING = {"row_margin": "mb-3", "row_gutter": "g-3", "col_padding": "px-2"}

# Initial Empty Graph (created within the function now)
def create_empty_sc_figure():
    """ Creates an empty placeholder figure for the impedance variation graph. """
    fig = px.bar(title="Variação da Impedância (%)")
    fig.update_layout(
        template="plotly_white",
        yaxis_title="ΔZ (%)",
        xaxis_title="",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=f"rgba({int(COLORS['background_card'][1:3], 16)},{int(COLORS['background_card'][3:5], 16)},{int(COLORS['background_card'][5:7], 16)},0.5)",
        font={"size": 10, "color": COLORS['text_light']},
        xaxis={"gridcolor": COLORS['border']},
        yaxis={"gridcolor": COLORS['border']},
        margin=dict(t=30, b=10, l=10, r=10),
        title_font_size=12,
        font_size=10
    )
    return fig

# --- Layout Definition Function ---
def create_short_circuit_layout():
    """Creates the layout component for the Short-Circuit section.

    Esta função cria o layout da seção de Curto-Circuito e inclui
    o painel de informações do transformador diretamente no layout, obtendo
    os dados do cache da aplicação.

    Returns:
        dash.html.Div: O layout completo da seção de Curto-Circuito
    """

    return dbc.Container([
        # Removemos a redefinição dos stores para evitar conflitos com os stores globais
        # Os stores já estão definidos em components/global_stores.py e incluídos no layout principal

        # Primeira seção - Informações do Transformador (sempre visível no topo)
        dbc.Row([
            dbc.Col(
                html.Div(
                    [
                        html.Div(
                            id="transformer-info-short-circuit-page", className="mb-1"
                        ),  # Painel visível que será atualizado pelo callback local
                        html.Div(
                            html.Div(),
                            id="transformer-info-short-circuit",
                            style={"display": "none"},
                        ),  # Painel oculto atualizado pelo callback global
                        html.Div(
                            html.Div(),
                            id="transformer-info-losses",
                            style={"display": "none"},
                        ),  # Compatibility
                        html.Div(
                            html.Div(),
                            id="transformer-info-impulse",
                            style={"display": "none"},
                        ),  # Compatibility
                        html.Div(
                            html.Div(),
                            id="transformer-info-dieletric",
                            style={"display": "none"},
                        ),  # Compatibility
                        html.Div(
                            html.Div(),
                            id="transformer-info-applied",
                            style={"display": "none"},
                        ),  # Compatibility
                        html.Div(
                            html.Div(),
                            id="transformer-info-induced",
                            style={"display": "none"},
                        ),  # Compatibility
                        html.Div(
                            html.Div(),
                            id="transformer-info-temperature-rise",
                            style={"display": "none"},
                        ),  # Compatibility
                        html.Div(
                            html.Div(),
                            id="transformer-info-comprehensive",
                            style={"display": "none"},
                        ),  # Compatibility
                    ],
                    className="mb-2",
                ),
                width=12,
            )
        ], className=SPACING['row_margin']),

        # Título principal do módulo
        dbc.Card([
            dbc.CardHeader(
                html.Div([
                    html.H6("ANÁLISE DE CURTO-CIRCUITO", className="text-center m-0 d-inline-block", style=TYPOGRAPHY['card_header']),
                    # Botão de ajuda
                    create_help_button("short_circuit", "Ajuda sobre Curto-Circuito")
                ], className="d-flex align-items-center justify-content-center"),
                style=COMPONENTS['card_header']
            ),
            dbc.CardBody([

        # Layout principal com duas colunas
        dbc.Row([
            # --- Coluna Esquerda: Dados de Entrada e Resultados ---
            dbc.Col([
                # Card para Dados de Entrada
                dbc.Card([
                    dbc.CardHeader(
                        html.H6("Dados de Entrada do Ensaio", className="m-0", style=TYPOGRAPHY['card_header']),
                        style=COMPONENTS['card_header']
                    ),
                    dbc.CardBody([
                        # Alerta informativo
                        dbc.Alert([
                            html.P("Cálculos e verificações baseados na NBR 5356-5 / IEC 60076-5.",
                                  className="mb-0", style={"fontSize": "0.7rem"})
                        ], color="info", className="p-2 mb-3"),

                        # Seção de Impedâncias
                        html.Div("Impedâncias Medidas (%)",
                                style={"fontSize": "0.8rem", "fontWeight": "bold", "marginBottom": "0.5rem", "color": COLORS['text_light']}),
                        dbc.Row([
                            dbc.Col([
                                create_labeled_input(
                                    "Pré-Ensaio (Z_antes):", "impedance-before", placeholder="Z% antes",
                                    label_width=6, input_width=6, persistence=True, persistence_type='local', step=0.01
                                ),
                            ], width=6),
                            dbc.Col([
                                create_labeled_input(
                                    "Pós-Ensaio (Z_depois):", "impedance-after", placeholder="Z% depois",
                                    label_width=6, input_width=6, persistence=True, persistence_type='local', step=0.01
                                ),
                            ], width=6),
                        ], className="mb-3"),

                        # Seção de Parâmetros Adicionais
                        html.Div("Parâmetros Adicionais",
                                style={"fontSize": "0.8rem", "fontWeight": "bold", "marginBottom": "0.5rem", "color": COLORS['text_light']}),
                        dbc.Row([
                            # Fator de Pico
                            dbc.Col([
                                create_labeled_input(
                                    "Fator Pico (k√2):", "peak-factor", placeholder="Ex: 2.55", value=2.55,
                                    label_width=6, input_width=6, persistence=True, persistence_type='local', step=0.01
                                ),
                            ], width=6),

                            # Lado de Cálculo
                            dbc.Col([
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Lado Cálculo Isc:", style=TYPOGRAPHY['label'], html_for='isc-side'),
                                    ], width=6),
                                    dbc.Col([
                                        dcc.Dropdown(
                                            id='isc-side',
                                            options=[
                                                {'label': 'AT', 'value': 'AT'},
                                                {'label': 'BT', 'value': 'BT'},
                                                {'label': 'Terciário', 'value': 'TERCIARIO'}
                                            ],
                                            value='AT', # Default
                                            clearable=False,
                                            style=COMPONENTS['dropdown'],
                                            className="dash-dropdown-dark",
                                            persistence=True, persistence_type='local'
                                        ),
                                    ], width=6),
                                ]),
                            ], width=6),
                        ], className="mb-3"),

                        # Categoria de Potência
                        dbc.Row([
                            dbc.Col([
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Categoria (Potência):", style=TYPOGRAPHY['label'], html_for='power-category'),
                                    ], width=6),
                                    dbc.Col([
                                        dcc.Dropdown(
                                            id='power-category',
                                            options=[
                                                {'label': 'Categoria I', 'value': 'I'},
                                                {'label': 'Categoria II', 'value': 'II'},
                                                {'label': 'Categoria III', 'value': 'III'},
                                                {'label': 'Categoria IV', 'value': 'IV'},
                                            ],
                                            placeholder="Selecione...",
                                            style=COMPONENTS['dropdown'],
                                            className="dash-dropdown-dark",
                                            persistence=True, persistence_type='local'
                                        ),
                                    ], width=6),
                                ]),
                            ], width=6),

                            # Botão de Cálculo
                            dbc.Col([
                                dbc.Button("Calcular / Verificar", id="calc-short-circuit-btn", color="primary",
                                          size="md", className="w-100 mt-1", style=TYPOGRAPHY['button']),
                            ], width=6, className="d-flex align-items-center"),
                        ], className="mb-2"),

                        # Mensagem de erro
                        html.Div(id='short-circuit-error-message', className="mt-2", style=TYPOGRAPHY['error_text'])
                    ], style=COMPONENTS['card_body'])
                ], style=COMPONENTS['card'], className="mb-3"),

                # Card para Resultados
                dbc.Card([
                    dbc.CardHeader(
                        html.H6("Resultados do Cálculo", className="m-0", style=TYPOGRAPHY['card_header']),
                        style=COMPONENTS['card_header']
                    ),
                    dbc.CardBody([
                        dbc.Row([
                            # Coluna de resultados numéricos
                            dbc.Col([
                                dbc.Row([
                                    dbc.Col(html.Label("Isc Simétrica (kA):", style=TYPOGRAPHY['label']), width=6),
                                    dbc.Col(dbc.Input(id="isc-sym-result", type="number", readonly=True, style=COMPONENTS['read_only'], persistence=True, persistence_type='local'), width=6)
                                ], className="mb-2 align-items-center"),
                                dbc.Row([
                                    dbc.Col(html.Label("Ip Pico (kA):", style=TYPOGRAPHY['label']), width=6),
                                    dbc.Col(dbc.Input(id="isc-peak-result", type="number", readonly=True, style=COMPONENTS['read_only'], persistence=True, persistence_type='local'), width=6)
                                ], className="mb-2 align-items-center"),
                                dbc.Row([
                                    dbc.Col(html.Label("Variação ΔZ (%):", style=TYPOGRAPHY['label']), width=6),
                                    dbc.Col(dbc.Input(id="delta-impedance-result", type="text", readonly=True, style=COMPONENTS['read_only'], persistence=True, persistence_type='local'), width=6)
                                ], className="mb-2 align-items-center"),
                            ], width=12),

                            # Status de verificação (destacado)
                            dbc.Col([
                                dbc.Row([
                                    dbc.Col(html.Label("Status Verificação:", style=TYPOGRAPHY['label']), width=6),
                                    dbc.Col(html.Div(id="impedance-check-status", children="-",
                                                    style={"paddingTop": "2px", "fontSize": "0.75rem"}), width=6)
                                ], className="mb-2 align-items-center"),
                            ], width=12),

                            # Notas explicativas
                            dbc.Col([
                                dbc.Alert([
                                    html.P([
                                        html.Strong("Nota 1:"), " Cálculos de Isc e ip são simplificados.", html.Br(),
                                        html.Strong("Nota 2:"), " Limites de ΔZ% conforme NBR 5356-5 Tabela 2."
                                    ], style=TYPOGRAPHY['small_text'], className="mb-0")
                                ], color="light", className="py-1 px-2 mt-1", style={"borderColor": "#e9ecef", "borderRadius":"4px", "marginBottom": "0"})
                            ], width=12),
                        ]),

                        # Hidden notes div for compatibility
                        html.Div(id='short-circuit-notes', style={"display": "none"})
                    ], style=COMPONENTS['card_body'])
                ], style=COMPONENTS['card'])
            ], md=5, className=SPACING['col_padding']),

            # --- Coluna Direita: Gráfico de Variação de Impedância (mais espaço) ---
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H6("Variação da Impedância", className="m-0", style=TYPOGRAPHY['card_header']),
                        style=COMPONENTS['card_header']
                    ),
                    dbc.CardBody([
                        # Descrição do gráfico
                        html.P([
                            "O gráfico abaixo mostra a variação percentual da impedância (ΔZ) medida antes e após o ensaio, ",
                            "comparada com os limites estabelecidos pela norma NBR 5356-5 / IEC 60076-5 para a categoria selecionada."
                        ], style={"fontSize": "0.75rem", "color": COLORS['text_light'], "marginBottom": "0.5rem"}),

                        # Gráfico com altura aumentada
                        dcc.Loading(
                            html.Div(
                                dcc.Graph(id='impedance-variation-graph', figure=create_empty_sc_figure(),
                                         config={'displayModeBar': True, 'displaylogo': False, 'modeBarButtonsToRemove': ['select2d', 'lasso2d']},
                                         style={"height": "400px"}) # Altura aumentada para melhor visualização
                            )
                        ),

                        # Legenda explicativa
                        html.Div([
                            html.Span("■ ", style={"color": COLORS.get('primary', 'royalblue'), "fontSize": "1rem"}),
                            html.Span("Variação Medida (ΔZ)", style={"fontSize": "0.75rem", "color": COLORS['text_light']}),
                            html.Span(" | ", style={"margin": "0 0.5rem", "color": COLORS['text_light']}),
                            html.Span("■ ", style={"color": COLORS.get('fail', 'firebrick'), "fontSize": "1rem"}),
                            html.Span("Limites Normativos", style={"fontSize": "0.75rem", "color": COLORS['text_light']}),
                        ], className="mt-2 text-center")
                    ], style=COMPONENTS['card_body'])
                ], style=COMPONENTS['card'], className="h-100")
            ], md=7, className=SPACING['col_padding']),
        ], className=SPACING['row_gutter'])
            ]), # Fechamento do CardBody
        ]), # Fechamento do Card

    ], fluid=True, className="p-0", style={"backgroundColor": COLORS['background_main']})
