# layouts/induced_voltage.py
"""
Defines the layout for the Induced Voltage section as a function.
"""
# Importações para obter dados do transformador
import logging

import dash_bootstrap_components as dbc
from dash import dcc, html

# Import centralized styles
from utils.theme_colors import APP_COLORS, COMPONENTS_STYLES, TYPOGRAPHY_STYLES, SPACING_STYLES

# Remove broken imports for helpers and define local fallbacks
def create_help_button(module_name, tooltip_text):
    # This is a placeholder, actual implementation might be in a shared UI components module
    return html.Div() # Fallback to avoid errors if not fully implemented

def create_labeled_input(label, input_id, input_type="number", value=None, min_val=None, max_val=None, step=None, label_width=6, input_width=6, placeholder=None, style=None, input_style_key="input"):
    # Renamed min/max to min_val/max_val to avoid conflict with built-in functions if used directly
    # Added input_style_key to allow different input styles if needed (e.g., "read_only")
    import dash_bootstrap_components as dbc
    from dash import html

    # Use a copy of the base style and update if custom style is provided
    final_input_style = COMPONENTS_STYLES.get(input_style_key, {}).copy()
    if style:
        final_input_style.update(style)
    
    # Ensure label style is applied from TYPOGRAPHY_STYLES
    label_style = TYPOGRAPHY_STYLES.get("label", {"fontSize": "0.75rem", "color": APP_COLORS.get("text_light", "#e0e0e0")})


    return dbc.Row([
        dbc.Col(dbc.Label(label, style=label_style), width=label_width),
        dbc.Col(dbc.Input(id=input_id, type=input_type, value=value, min=min_val, max=max_val, step=step, placeholder=placeholder, style=final_input_style), width=input_width)
    ], className="mb-1")

# --- Layout Definition Function ---
def create_induced_voltage_layout():
    """Creates the layout component for the Induced Voltage section.

    Returns:
        dash.html.Div: O layout completo da seção de Tensão Induzida
    """
    print("--- Executando create_induced_voltage_layout ---")
    # Não obter dados do MCP ou cache diretamente aqui!
    # O layout deve ser puro, os dados do transformador são preenchidos via callback.

    return dbc.Container(
        [
            # <<< REMOVIDOS dcc.Store definidos aqui >>>
            # Stores ('induced-voltage-store', 'transformer-inputs-store', etc.)
            # JÁ ESTÃO definidos em components/global_stores.py e incluídos no layout principal
            # Primeira seção - Informações do Transformador (Container a ser preenchido)
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    # Div onde o painel será renderizado - usando ID único para evitar conflitos
                                    html.Div(id="transformer-info-induced-page", className="mb-2"),
                                    # Div oculta para compatibilidade com o callback global_updates
                                    html.Div(
                                        html.Div(),
                                        id="transformer-info-induced",
                                        style={"display": "none"},
                                    ),
                                    # Adicionado para compatibilidade com o callback global_updates
                                    html.Div(
                                        html.Div(),
                                        id="transformer-info-losses",
                                        style={"display": "none"},
                                    ),
                                    html.Div(
                                        html.Div(),
                                        id="transformer-info-impulse",
                                        style={"display": "none"},
                                    ),
                                    html.Div(
                                        html.Div(),
                                        id="transformer-info-dieletric",
                                        style={"display": "none"},
                                    ),
                                    html.Div(
                                        html.Div(),
                                        id="transformer-info-applied",
                                        style={"display": "none"},
                                    ),
                                    html.Div(
                                        html.Div(),
                                        id="transformer-info-short-circuit",
                                        style={"display": "none"},
                                    ),
                                    html.Div(
                                        html.Div(),
                                        id="transformer-info-temperature-rise",
                                        style={"display": "none"},
                                    ),
                                    html.Div(
                                        html.Div(),
                                        id="transformer-info-comprehensive",
                                        style={"display": "none"},
                                    ),
                                ]
                            )
                        ],
                        width=12,
                    )
                ],
                className=SPACING_STYLES["row_margin"],
            ),
            # Título principal do módulo (como antes)
            dbc.Card(
                [
                    dbc.CardHeader(
                        html.Div(
                            [
                                html.H6(
                                    "ANÁLISE DE TENSÃO INDUZIDA",
                                    className="text-center m-0 d-inline-block",
                                    style=TYPOGRAPHY_STYLES.get("card_header", {}),
                                ),
                                create_help_button(
                                    "induced_voltage", "Ajuda sobre Tensão Induzida"
                                ),
                            ],
                            className="d-flex align-items-center justify-content-center",
                        ),
                        style=COMPONENTS_STYLES.get("card_header", {}),
                    ),
                    dbc.CardBody(
                        [
                            # Parâmetros de Entrada em uma única linha (como antes)
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Card(
                                                [
                                                    dbc.CardHeader(
                                                        html.H6(
                                                            "Parâmetros de Entrada do Ensaio Tensão Induzida",
                                                            className="m-0",
                                                            style=TYPOGRAPHY_STYLES.get("card_header", {}),
                                                        ),
                                                        style=COMPONENTS_STYLES.get("card_header", {}),
                                                    ),
                                                    dbc.CardBody(
                                                        [
                                                            dbc.Row(
                                                                [
                                                                    dbc.Col(
                                                                        [
                                                                            dbc.Alert(
                                                                                "Cálculos baseados na NBR 5356-3 / IEC 60076-3 e estimativas com tabelas de aço M4.",
                                                                                color="info", # Keep direct color for Alert for now
                                                                                className="small py-2 px-3 mb-0 h-75",
                                                                                style={
                                                                                    **TYPOGRAPHY_STYLES.get("small_text", {}),
                                                                                    "display": "flex",
                                                                                    "alignItems": "center",
                                                                                },
                                                                            )
                                                                        ],
                                                                        md=2,
                                                                        className="d-flex align-items-center",
                                                                    ),
                                                                    dbc.Col(
                                                                        [
                                                                            dbc.Label(
                                                                                "Tipo:",
                                                                                style={
                                                                                    **TYPOGRAPHY_STYLES.get("label", {}),
                                                                                    "textAlign": "left",
                                                                                    "marginBottom": "0",
                                                                                    "whiteSpace": "nowrap",
                                                                                },
                                                                                html_for="tipo-transformador",
                                                                            ),
                                                                            dcc.Dropdown(
                                                                                id="tipo-transformador",
                                                                                options=[
                                                                                    {
                                                                                        "label": "Monofásico",
                                                                                        "value": "Monofásico",
                                                                                    },
                                                                                    {
                                                                                        "label": "Trifásico",
                                                                                        "value": "Trifásico",
                                                                                    },
                                                                                ],
                                                                                value="Trifásico",
                                                                                clearable=False,
                                                                                style={
                                                                                    **COMPONENTS_STYLES.get("dropdown", {}),
                                                                                    "height": "26px",
                                                                                    "minHeight": "26px",
                                                                                    "width": "120px",
                                                                                },
                                                                                className="dark-dropdown",
                                                                            ),
                                                                        ],
                                                                        md=2,
                                                                        className="d-flex align-items-center",
                                                                    ),
                                                                    dbc.Col(
                                                                        [
                                                                            create_labeled_input(
                                                                                "Teste (fp):",
                                                                                "frequencia-teste",
                                                                                placeholder="Ex: 120",
                                                                                value=120,
                                                                                label_width=5,
                                                                                input_width=7
                                                                            )
                                                                        ],
                                                                        md=2,
                                                                        className="d-flex align-items-center",
                                                                    ),
                                                                    dbc.Col(
                                                                        [
                                                                            create_labeled_input(
                                                                                "Cap. AT-GND (pF):",
                                                                                "capacitancia",
                                                                                placeholder="Cp AT-GND",
                                                                                min_val=0, # Renamed from min
                                                                                step="1",
                                                                                label_width=6,
                                                                                input_width=6
                                                                            )
                                                                        ],
                                                                        md=3,
                                                                        className="d-flex align-items-center",
                                                                    ),
                                                                    dbc.Col(
                                                                        [
                                                                            dbc.Button(
                                                                                "Calcular",
                                                                                id="calc-induced-voltage-btn",
                                                                                color="primary", # Keep direct color for now
                                                                                size="sm",
                                                                                className="w-100 h-75",
                                                                                style=TYPOGRAPHY_STYLES.get("button", {}),
                                                                            )
                                                                        ],
                                                                        md=3,
                                                                        className="d-flex align-items-center",
                                                                    ),
                                                                ],
                                                                className="g-2 align-items-center justify-content-between",
                                                            ),
                                                            html.Div(
                                                                id="induced-voltage-error-message",
                                                                className="mt-2",
                                                                style=TYPOGRAPHY_STYLES.get("error_text", {}),
                                                            ),
                                                        ],
                                                        style={
                                                            **COMPONENTS_STYLES.get("card_body", {}),
                                                            "padding": "0.5rem",
                                                        },
                                                    ),
                                                ],
                                                style=COMPONENTS_STYLES.get("card", {}),
                                            )
                                        ],
                                        width=12,
                                        className=SPACING_STYLES["col_padding"],
                                    )
                                ],
                                className=SPACING_STYLES["row_gutter"],
                            ),
                            # Resultados (como antes)
                            dbc.Row(
                                [
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
                                                            html.Div(
                                                                id="resultado-tensao-induzida"
                                                            ),
                                                            type="circle",
                                                            color=APP_COLORS.get("primary", "#26427A"),
                                                        ),
                                                        style={
                                                            **COMPONENTS_STYLES.get("card_body", {}),
                                                            "padding": "0.5rem",
                                                        },
                                                    ),
                                                ],
                                                style=COMPONENTS_STYLES.get("card", {}),
                                            )
                                        ],
                                        width=12,
                                        className=SPACING_STYLES["col_padding"],
                                    )
                                ],
                                className=SPACING_STYLES["row_gutter"],
                            ),
                            # Botões para tabela de frequências (como antes)
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.ButtonGroup(
                                                [
                                                    dbc.Button(
                                                        "Gerar Tabela de Frequências (100-240Hz)",
                                                        id="generate-frequency-table-button",
                                                        color="info", # Keep direct color
                                                        size="sm",
                                                        className="mt-3 mb-2",
                                                        style={
                                                            **TYPOGRAPHY_STYLES.get("button", {}),
                                                            "width": "auto",
                                                        },
                                                    ),
                                                    dbc.Button(
                                                        "Limpar Tabela",
                                                        id="clear-frequency-table-button",
                                                        color="secondary", # Keep direct color
                                                        size="sm",
                                                        className="mt-3 mb-2",
                                                        style={
                                                            **TYPOGRAPHY_STYLES.get("button", {}),
                                                            "width": "auto",
                                                        },
                                                    ),
                                                ]
                                            )
                                        ],
                                        width=12,
                                        className="d-flex justify-content-center",
                                    )
                                ],
                                className=SPACING_STYLES["row_gutter"],
                            ),
                            # Contêiner para a tabela de frequências (como antes)
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [html.Div(id="frequency-table-container")],
                                        width=12,
                                        className=SPACING_STYLES["col_padding"],
                                    )
                                ],
                                className=SPACING_STYLES["row_gutter"],
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
