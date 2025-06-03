# layouts/temperature_rise.py
"""
Defines the layout for the Temperature Rise section as a function.
"""
import logging
log = logging.getLogger(__name__)

import dash_bootstrap_components as dbc
from dash import dcc, html

from app import app  # Importa a instância app para acessar o cache de dados do transformador

# Import centralized styles
from utils.theme_colors import APP_COLORS, COMPONENTS_STYLES, TYPOGRAPHY_STYLES, SPACING_STYLES

# Definir helpers e estilos locais robustos
def create_help_button(module_name, tooltip_text):
    from dash import html
    return html.Div()  # Fallback

# Fallback para MATERIAL_OPTIONS se constants não estiver disponível
# Idealmente, isso também viria de um local centralizado se usado em múltiplos lugares.
MATERIAL_OPTIONS = [
    {"label": "Cobre", "value": "cobre"},
    {"label": "Alumínio", "value": "aluminio"},
]


# --- Layout Definition Function ---
def create_temperature_rise_layout():
    """Creates the layout component for the Temperature Rise section."""

    # Tenta obter os dados do transformador do cache da aplicação ou do MCP
    transformer_data = {}
    try:
        # Primeiro tenta obter do MCP (fonte mais confiável)
        if hasattr(app, "mcp") and app.mcp is not None:
            transformer_data = app.mcp.get_data("transformer-inputs-store")
            log.info(
                f"[Temperature Rise] Dados do transformador obtidos do MCP: {len(transformer_data) if isinstance(transformer_data, dict) else 'Não é dict'}"
            )
        # Se não conseguir do MCP, tenta do cache
        else:
            log.warning(
                "[Temperature Rise] Dados do transformador não encontrados no MCP nem no cache"
            )
    except Exception as e:
        log.error(f"[Temperature Rise] Erro ao obter dados do transformador: {e}")

    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        id="transformer-info-temperature-rise-page",
                                        className="mb-1",
                                    ),
                                    html.Div(
                                        html.Div(),
                                        id="transformer-info-temperature-rise",
                                        style={"display": "none"},
                                    ),
                                    html.Div(html.Div(),id="transformer-info-losses", style={"display": "none"}),
                                    html.Div(html.Div(),id="transformer-info-impulse", style={"display": "none"}),
                                    html.Div(html.Div(),id="transformer-info-dieletric", style={"display": "none"}),
                                    html.Div(html.Div(),id="transformer-info-applied", style={"display": "none"}),
                                    html.Div(html.Div(),id="transformer-info-induced", style={"display": "none"}),
                                    html.Div(html.Div(),id="transformer-info-short-circuit", style={"display": "none"}),
                                    html.Div(html.Div(),id="transformer-info-comprehensive", style={"display": "none"}),
                                ],
                                className="mb-2",
                            )
                        ],
                        width=12,
                    )
                ],
                className=SPACING_STYLES.get("row_margin", "mb-3"),
            ),
            dbc.Card(
                [
                    dbc.CardHeader(
                        html.Div(
                            [
                                html.H6(
                                    "ANÁLISE DE ELEVAÇÃO DE TEMPERATURA",
                                    className="text-center m-0 d-inline-block",
                                    style=TYPOGRAPHY_STYLES.get("card_header", {}),
                                ),
                                create_help_button(
                                    "temperature_rise", "Ajuda sobre Elevação de Temperatura"
                                ),
                            ],
                            className="d-flex align-items-center justify-content-center",
                        ),
                        style=COMPONENTS_STYLES.get("card_header", {}),
                    ),
                    dbc.CardBody(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Card(
                                                [
                                                    dbc.CardHeader(
                                                        html.H6(
                                                            "Dados de Entrada do Ensaio",
                                                            className="m-0",
                                                            style=TYPOGRAPHY_STYLES.get("card_header", {}),
                                                        ),
                                                        style=COMPONENTS_STYLES.get("card_header", {}),
                                                    ),
                                                    dbc.CardBody(
                                                        [
                                                            dbc.Alert(
                                                                [
                                                                    html.P(
                                                                        "Cálculos baseados na NBR 5356-2 / IEC 60076-2.",
                                                                        className="mb-0",
                                                                        style={"fontSize": "0.7rem"},
                                                                    )
                                                                ],
                                                                color="info",
                                                                className="p-2 mb-3",
                                                            ),
                                                            html.Div(
                                                                "Condições Ambientais e Material",
                                                                style={
                                                                    "fontSize": "0.8rem",
                                                                    "fontWeight": "bold",
                                                                    "marginBottom": "0.5rem",
                                                                    "color": APP_COLORS.get("text_light", "#e0e0e0"),
                                                                },
                                                            ),
                                                            dbc.Row(
                                                                [
                                                                    dbc.Col(
                                                                        [
                                                                            dbc.Label(
                                                                                "Temp. Ambiente (Θa) (°C):",
                                                                                style=TYPOGRAPHY_STYLES.get("label", {}),
                                                                                html_for="temp-amb",
                                                                            ),
                                                                            dbc.Input(
                                                                                id="temp-amb",
                                                                                type="number",
                                                                                placeholder="Ex: 25.0",
                                                                                style=COMPONENTS_STYLES.get("input", {}),
                                                                                step=0.1,
                                                                            ),
                                                                        ],
                                                                        width=6,
                                                                    ),
                                                                    dbc.Col(
                                                                        [
                                                                            dbc.Row(
                                                                                [
                                                                                    dbc.Col(
                                                                                        [
                                                                                            dbc.Label(
                                                                                                "Material Enrolamento:",
                                                                                                style=TYPOGRAPHY_STYLES.get("label", {}),
                                                                                                html_for="winding-material",
                                                                                            ),
                                                                                        ],
                                                                                        width=7,
                                                                                    ),
                                                                                    dbc.Col(
                                                                                        [
                                                                                            dcc.Dropdown(
                                                                                                id="winding-material",
                                                                                                options=MATERIAL_OPTIONS,
                                                                                                value="cobre",
                                                                                                clearable=False,
                                                                                                style=COMPONENTS_STYLES.get("dropdown", {}),
                                                                                                className="dash-dropdown-dark",
                                                                                            ),
                                                                                        ],
                                                                                        width=5,
                                                                                    ),
                                                                                ]
                                                                            ),
                                                                        ],
                                                                        width=6,
                                                                    ),
                                                                ],
                                                                className="mb-3",
                                                            ),
                                                            html.Div(
                                                                "Medições a Frio",
                                                                style={
                                                                    "fontSize": "0.8rem",
                                                                    "fontWeight": "bold",
                                                                    "marginBottom": "0.5rem",
                                                                    "color": APP_COLORS.get("text_light", "#e0e0e0"),
                                                                },
                                                            ),
                                                            dbc.Row(
                                                                [
                                                                    dbc.Col(
                                                                        [
                                                                            dbc.Label(
                                                                                "Res. Fria (Rc) (Ohm):",
                                                                                style=TYPOGRAPHY_STYLES.get("label", {}),
                                                                                html_for="res-cold",
                                                                            ),
                                                                            dbc.Input(
                                                                                id="res-cold",
                                                                                type="number",
                                                                                placeholder="Ohm @ Θc",
                                                                                style=COMPONENTS_STYLES.get("input", {}),
                                                                                step="any",
                                                                            ),
                                                                        ],
                                                                        width=6,
                                                                    ),
                                                                    dbc.Col(
                                                                        [
                                                                            dbc.Label(
                                                                                "Temp. Ref. Fria (Θc) (°C):",
                                                                                style=TYPOGRAPHY_STYLES.get("label", {}),
                                                                                html_for="temp-cold",
                                                                            ),
                                                                            dbc.Input(
                                                                                id="temp-cold",
                                                                                type="number",
                                                                                placeholder="Temp. Rc",
                                                                                style=COMPONENTS_STYLES.get("input", {}),
                                                                            ),
                                                                        ],
                                                                        width=6,
                                                                    ),
                                                                ],
                                                                className="mb-3",
                                                            ),
                                                            html.Div(
                                                                "Medições a Quente",
                                                                style={
                                                                    "fontSize": "0.8rem",
                                                                    "fontWeight": "bold",
                                                                    "marginBottom": "0.5rem",
                                                                    "color": APP_COLORS.get("text_light", "#e0e0e0"),
                                                                },
                                                            ),
                                                            dbc.Row(
                                                                [
                                                                    dbc.Col(
                                                                        [
                                                                            dbc.Label(
                                                                                "Res. Quente (Rw) (Ohm):",
                                                                                style=TYPOGRAPHY_STYLES.get("label", {}),
                                                                                html_for="res-hot",
                                                                            ),
                                                                            dbc.Input(
                                                                                id="res-hot",
                                                                                type="number",
                                                                                placeholder="Ohm @ t=0",
                                                                                style=COMPONENTS_STYLES.get("input", {}),
                                                                                step="any",
                                                                            ),
                                                                            dbc.Tooltip(
                                                                                "Resistência extrapolada para t=0 após desligamento (conforme NBR 5356-2)",
                                                                                target="res-hot",
                                                                                placement="bottom",
                                                                            ),
                                                                        ],
                                                                        width=6,
                                                                    ),
                                                                    dbc.Col(
                                                                        [
                                                                            dbc.Label(
                                                                                "Temp. Topo Óleo (Θoil) (°C):",
                                                                                style=TYPOGRAPHY_STYLES.get("label", {}),
                                                                                html_for="temp-top-oil",
                                                                            ),
                                                                            dbc.Input(
                                                                                id="temp-top-oil",
                                                                                type="number",
                                                                                placeholder="Final",
                                                                                style=COMPONENTS_STYLES.get("input", {}),
                                                                            ),
                                                                        ],
                                                                        width=6,
                                                                    ),
                                                                ],
                                                                className="mb-3",
                                                            ),
                                                            html.Div(
                                                                "Parâmetro para Constante de Tempo Térmica",
                                                                style={
                                                                    "fontSize": "0.8rem",
                                                                    "fontWeight": "bold",
                                                                    "marginBottom": "0.5rem",
                                                                    "color": APP_COLORS.get("text_light", "#e0e0e0"),
                                                                },
                                                            ),
                                                            dbc.Row(
                                                                [
                                                                    dbc.Col(
                                                                        [
                                                                            dbc.Row(
                                                                                [
                                                                                    dbc.Col(
                                                                                        [
                                                                                            dbc.Label(
                                                                                                "Elevação Máx Óleo (ΔΘoil_max) (K):",
                                                                                                style=TYPOGRAPHY_STYLES.get("label", {}),
                                                                                                html_for="delta-theta-oil-max",
                                                                                            ),
                                                                                        ],
                                                                                        width=7,
                                                                                    ),
                                                                                    dbc.Col(
                                                                                        [
                                                                                            dbc.Input(
                                                                                                type="number",
                                                                                                id="delta-theta-oil-max",
                                                                                                style=COMPONENTS_STYLES.get("input", {}),
                                                                                                placeholder="Opcional p/ τ₀",
                                                                                                step=0.1,
                                                                                            ),
                                                                                        ],
                                                                                        width=5,
                                                                                    ),
                                                                                ]
                                                                            ),
                                                                            dbc.Tooltip(
                                                                                "Elevação final do óleo sobre o ambiente (da 1ª etapa do ensaio). Necessário para calcular τ₀.",
                                                                                target="delta-theta-oil-max",
                                                                                placement="bottom",
                                                                            ),
                                                                        ],
                                                                        width=12,
                                                                    ),
                                                                ],
                                                                className="mb-3",
                                                            ),
                                                            dbc.Row(
                                                                [
                                                                    dbc.Col(
                                                                        dbc.Button(
                                                                            "Calcular Elevação",
                                                                            id="limpar-temp-rise", # ID seems incorrect, should be 'calc-temp-rise-btn' or similar
                                                                            color="primary",
                                                                            size="md",
                                                                            className="w-100",
                                                                            style=TYPOGRAPHY_STYLES.get("button", {}),
                                                                            n_clicks=0,
                                                                        ),
                                                                        width=12,
                                                                    ),
                                                                ],
                                                                className="mb-2",
                                                            ),
                                                            html.Div(
                                                                id="temp-rise-error-message",
                                                                className="mt-2",
                                                                style=TYPOGRAPHY_STYLES.get("error_text", {}),
                                                            ),
                                                        ],
                                                        style=COMPONENTS_STYLES.get("card_body", {}),
                                                    ),
                                                ],
                                                style=COMPONENTS_STYLES.get("card", {}),
                                                className="mb-3",
                                            ),
                                            dbc.Card(
                                                [
                                                    dbc.CardHeader(
                                                        html.H6(
                                                            "Diagrama de Elevação de Temperatura",
                                                            className="m-0",
                                                            style=TYPOGRAPHY_STYLES.get("card_header", {}),
                                                        ),
                                                        style=COMPONENTS_STYLES.get("card_header", {}),
                                                    ),
                                                    dbc.CardBody(
                                                        [
                                                            html.Div(
                                                                [
                                                                    html.Div(
                                                                        [
                                                                            html.I(
                                                                                className="fas fa-temperature-high fa-4x"
                                                                            ),
                                                                            html.P(
                                                                                "Diagrama de Elevação de Temperatura",
                                                                                className="mt-2",
                                                                            ),
                                                                        ],
                                                                        className="text-center p-4",
                                                                        style={
                                                                            "width": "100%",
                                                                            "maxWidth": "500px",
                                                                            "margin": "0 auto",
                                                                            "display": "block",
                                                                            "color": "#aaa", 
                                                                        },
                                                                    )
                                                                ],
                                                                className="text-center",
                                                            )
                                                        ],
                                                        style=COMPONENTS_STYLES.get("card_body", {}),
                                                    ),
                                                ],
                                                style=COMPONENTS_STYLES.get("card", {}),
                                            ),
                                        ],
                                        md=6,
                                        className=SPACING_STYLES.get("col_padding", "px-2"),
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Card(
                                                [
                                                    dbc.CardHeader(
                                                        html.H6(
                                                            "Resultados Calculados",
                                                            className="m-0",
                                                            style=TYPOGRAPHY_STYLES.get("card_header", {}),
                                                        ),
                                                        style=COMPONENTS_STYLES.get("card_header", {}),
                                                    ),
                                                    dbc.CardBody(
                                                        dcc.Loading(
                                                            [
                                                                html.Div(
                                                                    "Temperaturas e Elevações",
                                                                    style={
                                                                        "fontSize": "0.8rem",
                                                                        "fontWeight": "bold",
                                                                        "marginBottom": "0.5rem",
                                                                        "color": APP_COLORS.get("text_light", "#e0e0e0"),
                                                                    },
                                                                ),
                                                                dbc.Row(
                                                                    [
                                                                        dbc.Col(
                                                                            [
                                                                                dbc.Row(
                                                                                    [
                                                                                        dbc.Col(
                                                                                            html.Label(
                                                                                                "Temp. Média Enrol. Final (Θw):",
                                                                                                style=TYPOGRAPHY_STYLES.get("label", {}),
                                                                                            ),
                                                                                            width=7,
                                                                                        ),
                                                                                        dbc.Col(
                                                                                            dbc.Input(
                                                                                                id="avg-winding-temp",
                                                                                                type="number",
                                                                                                readonly=True,
                                                                                                style=COMPONENTS_STYLES.get("read_only", {}),
                                                                                            ),
                                                                                            width=5,
                                                                                        ),
                                                                                    ],
                                                                                    className="mb-2 align-items-center",
                                                                                ),
                                                                            ],
                                                                            width=12,
                                                                        ),
                                                                        dbc.Col(
                                                                            [
                                                                                dbc.Row(
                                                                                    [
                                                                                        dbc.Col(
                                                                                            html.Label(
                                                                                                "Elevação Média Enrol. (ΔΘw):",
                                                                                                style=TYPOGRAPHY_STYLES.get("label", {}),
                                                                                            ),
                                                                                            width=7,
                                                                                        ),
                                                                                        dbc.Col(
                                                                                            dbc.Input(
                                                                                                id="avg-winding-rise",
                                                                                                type="number",
                                                                                                readonly=True,
                                                                                                style=COMPONENTS_STYLES.get("read_only", {}),
                                                                                            ),
                                                                                            width=5,
                                                                                        ),
                                                                                    ],
                                                                                    className="mb-2 align-items-center",
                                                                                ),
                                                                            ],
                                                                            width=12,
                                                                        ),
                                                                        dbc.Col(
                                                                            [
                                                                                dbc.Row(
                                                                                    [
                                                                                        dbc.Col(
                                                                                            html.Label(
                                                                                                "Elevação Topo Óleo (ΔΘoil):",
                                                                                                style=TYPOGRAPHY_STYLES.get("label", {}),
                                                                                            ),
                                                                                            width=7,
                                                                                        ),
                                                                                        dbc.Col(
                                                                                            dbc.Input(
                                                                                                id="top-oil-rise",
                                                                                                type="number",
                                                                                                readonly=True,
                                                                                                style=COMPONENTS_STYLES.get("read_only", {}),
                                                                                            ),
                                                                                            width=5,
                                                                                        ),
                                                                                    ],
                                                                                    className="mb-2 align-items-center",
                                                                                ),
                                                                            ],
                                                                            width=12,
                                                                        ),
                                                                    ]
                                                                ),
                                                                html.Div(
                                                                    "Parâmetros Térmicos",
                                                                    style={
                                                                        "fontSize": "0.8rem",
                                                                        "fontWeight": "bold",
                                                                        "marginTop": "1rem",
                                                                        "marginBottom": "0.5rem",
                                                                        "color": APP_COLORS.get("text_light", "#e0e0e0"),
                                                                    },
                                                                ),
                                                                dbc.Row(
                                                                    [
                                                                        dbc.Col(
                                                                            [
                                                                                dbc.Row(
                                                                                    [
                                                                                        dbc.Col(
                                                                                            html.Label(
                                                                                                "Perdas Totais Usadas (Ptot):",
                                                                                                style=TYPOGRAPHY_STYLES.get("label", {}),
                                                                                            ),
                                                                                            width=7,
                                                                                        ),
                                                                                        dbc.Col(
                                                                                            dbc.Input(
                                                                                                id="ptot-used",
                                                                                                type="number",
                                                                                                readonly=True,
                                                                                                placeholder="kW",
                                                                                                style=COMPONENTS_STYLES.get("read_only", {}),
                                                                                            ),
                                                                                            width=5,
                                                                                        ),
                                                                                    ],
                                                                                    className="mb-2 align-items-center",
                                                                                ),
                                                                            ],
                                                                            width=12,
                                                                        ),
                                                                        dbc.Col(
                                                                            [
                                                                                dbc.Row(
                                                                                    [
                                                                                        dbc.Col(
                                                                                            html.Label(
                                                                                                "Const. Tempo Térmica (τ₀):",
                                                                                                style=TYPOGRAPHY_STYLES.get("label", {}),
                                                                                            ),
                                                                                            width=7,
                                                                                        ),
                                                                                        dbc.Col(
                                                                                            dbc.Input(
                                                                                                id="tau0-result",
                                                                                                type="number",
                                                                                                readonly=True,
                                                                                                placeholder="horas",
                                                                                                style=COMPONENTS_STYLES.get("read_only", {}),
                                                                                            ),
                                                                                            width=5,
                                                                                        ),
                                                                                    ],
                                                                                    className="mb-2 align-items-center",
                                                                                ),
                                                                            ],
                                                                            width=12,
                                                                        ),
                                                                    ]
                                                                ),
                                                                html.Div(
                                                                    "Fórmulas Utilizadas",
                                                                    style={
                                                                        "fontSize": "0.8rem",
                                                                        "fontWeight": "bold",
                                                                        "marginTop": "1rem",
                                                                        "marginBottom": "0.5rem",
                                                                        "color": APP_COLORS.get("text_light", "#e0e0e0"),
                                                                    },
                                                                ),
                                                                dbc.Card(
                                                                    [
                                                                        dbc.CardBody(
                                                                            [
                                                                                html.P(
                                                                                    [
                                                                                        html.Span(
                                                                                            "Temperatura Média do Enrolamento:",
                                                                                            style={"fontWeight": "bold"},
                                                                                        ),
                                                                                        html.Br(),
                                                                                        "Θw = Θa + [(Rw/Rc) × (C + Θc) - C]",
                                                                                    ],
                                                                                    style={"fontSize": "0.7rem", "marginBottom": "0.5rem"},
                                                                                ),
                                                                                html.P(
                                                                                    [
                                                                                        html.Span(
                                                                                            "Elevação Média do Enrolamento:",
                                                                                            style={"fontWeight": "bold"},
                                                                                        ),
                                                                                        html.Br(),
                                                                                        "ΔΘw = Θw - Θa",
                                                                                    ],
                                                                                    style={"fontSize": "0.7rem", "marginBottom": "0.5rem"},
                                                                                ),
                                                                                html.P(
                                                                                    [
                                                                                        html.Span(
                                                                                            "Elevação do Topo do Óleo:",
                                                                                            style={"fontWeight": "bold"},
                                                                                        ),
                                                                                        html.Br(),
                                                                                        "ΔΘoil = Θoil - Θa",
                                                                                    ],
                                                                                    style={"fontSize": "0.7rem", "marginBottom": "0.5rem"},
                                                                                ),
                                                                                html.P(
                                                                                    [
                                                                                        html.Span(
                                                                                            "Constante de Tempo Térmica:",
                                                                                            style={"fontWeight": "bold"},
                                                                                        ),
                                                                                        html.Br(),
                                                                                        "τ₀ = 0.132 × (mT - 0.5 × mO) × ΔΘoil_max / Ptot",
                                                                                    ],
                                                                                    style={"fontSize": "0.7rem", "marginBottom": "0"},
                                                                                ),
                                                                            ],
                                                                            style={"padding": "0.5rem"}
                                                                        )
                                                                    ],
                                                                    style={
                                                                        "backgroundColor": APP_COLORS.get("background_card", "#2c2c2c"),
                                                                        "border": f"1px solid {APP_COLORS.get('border', '#444444')}",
                                                                    },
                                                                ),
                                                                html.Hr(className="my-3"),
                                                                dbc.Alert(
                                                                    [
                                                                        html.P(
                                                                            [
                                                                                html.Strong("Nota 1:"),
                                                                                " Cálculos conforme NBR 5356-2. Rw deve ser o valor extrapolado para t=0.",
                                                                                html.Br(),
                                                                                html.Strong("Nota 2:"),
                                                                                " O cálculo de τ₀ requer ΔΘoil_max, Pesos (Dados Básicos) e Perdas Totais (Perdas).",
                                                                                html.Br(),
                                                                                html.Strong("Nota 3:"),
                                                                                " C = 234,5 para cobre e 225 para alumínio.",
                                                                            ],
                                                                            style=TYPOGRAPHY_STYLES.get("small_text", {}),
                                                                            className="mb-0",
                                                                        )
                                                                    ],
                                                                    color="light",
                                                                    className="py-1 px-2 mt-1",
                                                                    style={
                                                                        "borderColor": "#e9ecef", 
                                                                        "borderRadius": "4px",
                                                                        "marginBottom": "0",
                                                                    },
                                                                ),
                                                            ]
                                                        ),
                                                        style=COMPONENTS_STYLES.get("card_body", {}),
                                                    ),
                                                ],
                                                style=COMPONENTS_STYLES.get("card", {}),
                                                className="h-100",
                                            )
                                        ],
                                        md=6,
                                        className=SPACING_STYLES.get("col_padding", "px-2"),
                                    ),
                                ],
                                className=SPACING_STYLES.get("row_gutter", "g-3"),
                            ),
                        ]
                    ),
                ]
            ),
        ],
        fluid=True,
        className="p-0",
        style={"backgroundColor": APP_COLORS.get("background_main", "#1a1a1a")},
    )
