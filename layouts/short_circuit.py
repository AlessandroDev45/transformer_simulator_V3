# layouts/short_circuit.py
"""
Defines the layout for the Short-Circuit Withstand section as a function.
"""
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.express as px # For the initial empty graph

# Import centralized styles
from utils.theme_colors import APP_COLORS, COMPONENTS_STYLES, TYPOGRAPHY_STYLES, SPACING_STYLES

# Remove broken imports for helpers and define local fallbacks
def create_help_button(module_name, tooltip_text):
    # This is a placeholder, actual implementation might be in a shared UI components module
    return html.Div() # Fallback to avoid errors if not fully implemented

def create_labeled_input(label, input_id, input_type="number", value=None, min_val=None, max_val=None, step=None, label_width=6, input_width=6, placeholder=None, style=None, input_style_key="input"):
    # Renamed min/max to min_val/max_val to avoid conflict with built-in functions
    import dash_bootstrap_components as dbc
    from dash import html

    final_input_style = COMPONENTS_STYLES.get(input_style_key, {}).copy()
    if style:
        final_input_style.update(style)
        
    label_style = TYPOGRAPHY_STYLES.get("label", {"fontSize": "0.75rem", "color": APP_COLORS.get("text_light", "#e0e0e0")})

    return dbc.Row([
        dbc.Col(dbc.Label(label, style=label_style), width=label_width),
        dbc.Col(dbc.Input(id=input_id, type=input_type, value=value, min=min_val, max=max_val, step=step, placeholder=placeholder, style=final_input_style), width=input_width)
    ], className="mb-1")

# Initial Empty Graph (created within the function now)
def create_empty_sc_figure():
    """ Creates an empty placeholder figure for the impedance variation graph. """
    fig = px.bar(title="Variação da Impedância (%)")
    fig.update_layout(
        template="plotly_white",
        yaxis_title="ΔZ (%)",
        xaxis_title="",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=f"rgba({int(APP_COLORS['background_card'][1:3], 16)},{int(APP_COLORS['background_card'][3:5], 16)},{int(APP_COLORS['background_card'][5:7], 16)},0.5)",
        font={"size": 10, "color": APP_COLORS['text_light']},
        xaxis={"gridcolor": APP_COLORS['border']},
        yaxis={"gridcolor": APP_COLORS['border']},
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
        ], className=SPACING_STYLES['row_margin']),

        # Título principal do módulo
        dbc.Card([
            dbc.CardHeader(
                html.Div([
                    html.H6("ANÁLISE DE CURTO-CIRCUITO", className="text-center m-0 d-inline-block", style=TYPOGRAPHY_STYLES.get('card_header', {})),
                    # Botão de ajuda
                    create_help_button("short_circuit", "Ajuda sobre Curto-Circuito")
                ], className="d-flex align-items-center justify-content-center"),
                style=COMPONENTS_STYLES.get('card_header', {})
            ),
            dbc.CardBody([

        # Layout principal com duas colunas
        dbc.Row([
            # --- Coluna Esquerda: Dados de Entrada e Resultados ---
            dbc.Col([
                # Card para Dados de Entrada
                dbc.Card([
                    dbc.CardHeader(
                        html.H6("Dados de Entrada do Ensaio", className="m-0", style=TYPOGRAPHY_STYLES.get('card_header', {})),
                        style=COMPONENTS_STYLES.get('card_header', {})
                    ),
                    dbc.CardBody([
                        # Alerta informativo
                        dbc.Alert([
                            html.P("Cálculos e verificações baseados na NBR 5356-5 / IEC 60076-5.",
                                  className="mb-0", style={"fontSize": "0.7rem"})
                        ], color="info", className="p-2 mb-3"), # Keep direct color for Alert

                        # Seção de Impedâncias
                        html.Div("Impedâncias Medidas (%)",
                                style={"fontSize": "0.8rem", "fontWeight": "bold", "marginBottom": "0.5rem", "color": APP_COLORS.get('text_light', '#e0e0e0')}),
                        dbc.Row([
                            dbc.Col([
                                create_labeled_input(
                                    "Pré-Ensaio (Z_antes):", "impedance-before", placeholder="Z% antes",
                                    label_width=6, input_width=6, step=0.01
                                ),
                            ], width=6),
                            dbc.Col([
                                create_labeled_input(
                                    "Pós-Ensaio (Z_depois):", "impedance-after", placeholder="Z% depois",
                                    label_width=6, input_width=6, step=0.01
                                ),
                            ], width=6),
                        ], className="mb-3"),

                        # Seção de Parâmetros Adicionais
                        html.Div("Parâmetros Adicionais",
                                style={"fontSize": "0.8rem", "fontWeight": "bold", "marginBottom": "0.5rem", "color": APP_COLORS.get('text_light', '#e0e0e0')}),
                        dbc.Row([
                            # Fator de Pico
                            dbc.Col([
                                create_labeled_input(
                                    "Fator Pico (k√2):", "peak-factor", placeholder="Ex: 2.55", value=2.55,
                                    label_width=6, input_width=6, step=0.01
                                ),
                            ], width=6),

                            # Lado de Cálculo
                            dbc.Col([
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Lado Cálculo Isc:", style=TYPOGRAPHY_STYLES.get('label', {}), html_for='isc-side'),
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
                                            style=COMPONENTS_STYLES.get('dropdown', {}),
                                            className="dash-dropdown-dark"
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
                                        dbc.Label("Categoria (Potência):", style=TYPOGRAPHY_STYLES.get('label', {}), html_for='power-category'),
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
                                            style=COMPONENTS_STYLES.get('dropdown', {}),
                                            className="dash-dropdown-dark"
                                        ),
                                    ], width=6),
                                ]),
                            ], width=6),

                            # Botão de Cálculo
                            dbc.Col([
                                dbc.Button("Calcular / Verificar", id="calc-short-circuit-btn", color="primary", # Keep direct color
                                          size="md", className="w-100 mt-1", style=COMPONENTS_STYLES.get('button', {})),
                            ], width=6, className="d-flex align-items-center"),
                        ], className="mb-2"),

                        # Mensagem de erro
                        html.Div(id='short-circuit-error-message', className="mt-2", style=TYPOGRAPHY_STYLES.get('error_text', {}))
                    ], style=COMPONENTS_STYLES.get('card_body', {}))
                ], style=COMPONENTS_STYLES.get('card', {}), className="mb-3"),

                # Card para Resultados
                dbc.Card([
                    dbc.CardHeader(
                        html.H6("Resultados do Cálculo", className="m-0", style=TYPOGRAPHY_STYLES.get('card_header', {})),
                        style=COMPONENTS_STYLES.get('card_header', {})
                    ),
                    dbc.CardBody([
                        dbc.Row([
                            # Coluna de resultados numéricos
                            dbc.Col([
                                dbc.Row([
                                    dbc.Col(html.Label("Isc Simétrica (kA):", style=TYPOGRAPHY_STYLES.get('label', {})), width=6),
                                    dbc.Col(dbc.Input(id="isc-sym-result", type="number", readonly=True, style=COMPONENTS_STYLES.get('read_only', {})), width=6)
                                ], className="mb-2 align-items-center"),
                                dbc.Row([
                                    dbc.Col(html.Label("Ip Pico (kA):", style=TYPOGRAPHY_STYLES.get('label', {})), width=6),
                                    dbc.Col(dbc.Input(id="isc-peak-result", type="number", readonly=True, style=COMPONENTS_STYLES.get('read_only', {})), width=6)
                                ], className="mb-2 align-items-center"),
                                dbc.Row([
                                    dbc.Col(html.Label("Variação ΔZ (%):", style=TYPOGRAPHY_STYLES.get('label', {})), width=6),
                                    dbc.Col(dbc.Input(id="delta-impedance-result", type="text", readonly=True, style=COMPONENTS_STYLES.get('read_only', {})), width=6)
                                ], className="mb-2 align-items-center"),
                            ], width=12),

                            # Status de verificação (destacado)
                            dbc.Col([
                                dbc.Row([
                                    dbc.Col(html.Label("Status Verificação:", style=TYPOGRAPHY_STYLES.get('label', {})), width=6),
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
                                    ], style=TYPOGRAPHY_STYLES.get('small_text', {}), className="mb-0")
                                ], color="light", className="py-1 px-2 mt-1", style={"borderColor": "#e9ecef", "borderRadius":"4px", "marginBottom": "0"})
                            ], width=12),
                        ]),

                        # Hidden notes div for compatibility
                        html.Div(id='short-circuit-notes', style={"display": "none"})
                    ], style=COMPONENTS_STYLES.get('card_body', {}))
                ], style=COMPONENTS_STYLES.get('card', {}))
            ], md=5, className=SPACING_STYLES['col_padding']),

            # --- Coluna Direita: Gráfico de Variação de Impedância (mais espaço) ---
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H6("Variação da Impedância", className="m-0", style=TYPOGRAPHY_STYLES.get('card_header', {})),
                        style=COMPONENTS_STYLES.get('card_header', {})
                    ),
                    dbc.CardBody([
                        # Descrição do gráfico
                        html.P([
                            "O gráfico abaixo mostra a variação percentual da impedância (ΔZ) medida antes e após o ensaio, ",
                            "comparada com os limites estabelecidos pela norma NBR 5356-5 / IEC 60076-5 para a categoria selecionada."
                        ], style={"fontSize": "0.75rem", "color": APP_COLORS.get('text_light', '#e0e0e0'), "marginBottom": "0.5rem"}),

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
                            html.Span("■ ", style={"color": APP_COLORS.get('primary', 'royalblue'), "fontSize": "1rem"}),
                            html.Span("Variação Medida (ΔZ)", style={"fontSize": "0.75rem", "color": APP_COLORS.get('text_light', '#e0e0e0')}),
                            html.Span(" | ", style={"margin": "0 0.5rem", "color": APP_COLORS.get('text_light', '#e0e0e0')}),
                            html.Span("■ ", style={"color": APP_COLORS.get('fail', 'firebrick'), "fontSize": "1rem"}),
                            html.Span("Limites Normativos", style={"fontSize": "0.75rem", "color": APP_COLORS.get('text_light', '#e0e0e0')}),
                        ], className="mt-2 text-center")
                    ], style=COMPONENTS_STYLES.get('card_body', {}))
                ], style=COMPONENTS_STYLES.get('card', {}), className="h-100")
            ], md=7, className=SPACING_STYLES['col_padding']),
        ], className=SPACING_STYLES['row_gutter'])
            ]), # Fechamento do CardBody
        ]), # Fechamento do Card

    ], fluid=True, className="p-0", style={"backgroundColor": APP_COLORS.get('background_main', '#1a1a1a')})
