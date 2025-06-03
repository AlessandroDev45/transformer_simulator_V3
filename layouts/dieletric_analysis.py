# layouts/dieletric_analysis.py
"""
Define o layout para a seção de Análise Dielétrica.
"""
import logging

import dash_bootstrap_components as dbc
from dash import dcc, html

# Remove broken imports for helpers and define local fallbacks

def create_help_button(module_name, tooltip_text):
    return None

def create_dielectric_input_column(verificador_instance, label, identifier):
    # Styles are now globally available via COMPONENTS_STYLES, TYPOGRAPHY_STYLES
    # No need to redefine them here if they are correctly imported and used at module level.
    # However, for clarity and directness within this function, we can use .get()
    
    label_style = TYPOGRAPHY_STYLES.get("label", {})
    input_style = COMPONENTS_STYLES.get("input", {})
    dropdown_style = COMPONENTS_STYLES.get("dropdown", {})
    read_only_style = COMPONENTS_STYLES.get("read_only", {})
    card_header_style = COMPONENTS_STYLES.get("card_header", {})
    card_body_style = COMPONENTS_STYLES.get("card_body", {})

    # Options for Conexão dropdown (example, can be made more dynamic if needed)
    connection_options = [
        {"label": "YN", "value": "YN"},
        {"label": "Y", "value": "Y"},
        {"label": "D", "value": "D"},
        # Add other options like ZN, Z if applicable
    ]
    default_connection = "YN" if identifier == "at" else "D" if identifier == "bt" else None


    return dbc.Card([
        dbc.CardHeader(html.H6(label, className="m-0", style=card_header_style)),
        dbc.CardBody([
            dbc.Label(f"Um ({identifier.upper()}) (kV):", style=label_style, html_for={"type": "um", "index": identifier}),
            dcc.Dropdown(id={"type": "um", "index": identifier}, options=[], style=dropdown_style, className="dash-dropdown-dark mb-2"),

            dbc.Label(f"Conexão ({identifier.upper()}):", style=label_style, html_for={"type": "conexao", "index": identifier}),
            dcc.Dropdown(id={"type": "conexao", "index": identifier}, options=connection_options, value=default_connection, clearable=False, style=dropdown_style, className="dash-dropdown-dark mb-2"),
            
            html.Div(id={"type": "div-neutro", "index": identifier}, children=[
                dbc.Label(f"Neutro Um ({identifier.upper()}) (kV):", style=label_style, html_for={"type": "neutro-um", "index": identifier}),
                dcc.Dropdown(id={"type": "neutro-um", "index": identifier}, options=[], style=dropdown_style, className="dash-dropdown-dark mb-2"),
                
                dbc.Label(f"NBI Neutro ({identifier.upper()}) (kV):", style=label_style, html_for={"type": "impulso-atm-neutro", "index": identifier}),
                dcc.Dropdown(id={"type": "impulso-atm-neutro", "index": identifier}, options=[], style=dropdown_style, className="dash-dropdown-dark mb-2"),
            ], style={'display': 'none'} # Initially hidden, controlled by callback
            ),

            dbc.Label(f"IA/BIL ({identifier.upper()}) (kV):", style=label_style, html_for={"type": "ia", "index": identifier}),
            dcc.Dropdown(id={"type": "ia", "index": identifier}, options=[], style=dropdown_style, className="dash-dropdown-dark mb-2"),
            
            dbc.Label(f"IM/SIL ({identifier.upper()}) (kV):", style=label_style, html_for={"type": "im", "index": identifier}),
            dcc.Dropdown(id={"type": "im", "index": identifier}, options=[], style=dropdown_style, className="dash-dropdown-dark mb-2"),

            dbc.Label(f"Tensão Curta Duração ({identifier.upper()}) (kV):", style=label_style, html_for={"type": "tensao-curta", "index": identifier}),
            dcc.Dropdown(id={"type": "tensao-curta", "index": identifier}, options=[], style=dropdown_style, className="dash-dropdown-dark mb-2"),
            
            dbc.Label(f"Tensão Induzida ({identifier.upper()}) (kV):", style=label_style, html_for={"type": "tensao-induzida", "index": identifier}),
            dcc.Dropdown(id={"type": "tensao-induzida", "index": identifier}, options=[], style=dropdown_style, className="dash-dropdown-dark mb-2"),

            dbc.Label(f"IAC ({identifier.upper()}) (kV):", style=label_style, html_for={"type": "impulso-atm-cortado", "index": identifier}),
            dbc.Input(id={"type": "impulso-atm-cortado", "index": identifier}, type="text", readonly=True, style=read_only_style, className="mb-2"),

            html.Div(id={"type": "espacamentos-nbr", "index": identifier}, className="mt-2"),
            html.Div(id={"type": "espacamentos-ieee", "index": identifier}, className="mt-2"),

        ], style=card_body_style)
    ])

# Importações para obter dados do transformador
# <<< REMOVIDO import direto de 'app' >>>
# from app import app
log = logging.getLogger(__name__)

# Import centralized styles
from utils.theme_colors import APP_COLORS, COMPONENTS_STYLES, TYPOGRAPHY_STYLES, SPACING_STYLES


# --- Layout Definition Function ---
def create_dielectric_layout():
    """Creates the layout component for the Dielectric Analysis section.

    Returns:
        dash.html.Div: O layout completo da seção de Análise Dielétrica
    """
    log.info("Creating Dielectric Analysis layout (from dieletric_analysis.py)...")

    # Não obter dados do cache aqui
    transformer_data = {}

    # --- Verificador Initialization (como antes) ---
    verificador_instance = None
    try:
        from app_core.standards import VerificadorTransformador

        verificador_instance = VerificadorTransformador()
        if not verificador_instance.is_valid():
            log.warning(
                "VerificadorTransformador is invalid upon creation in create_dielectric_layout."
            )
        else:
            log.info("VerificadorTransformador instantiated successfully.")
    except ImportError:
        log.error("Failed to import VerificadorTransformador in create_dielectric_layout.")
    except Exception as e:
        log.critical(f"CRITICAL error instantiating VerificadorTransformador: {e}", exc_info=True)
        return dbc.Alert(
            f"Erro crítico ao carregar dados das normas: {e}. Verifique a configuração e os arquivos.",
            color="danger",
            style=COMPONENTS_STYLES.get("alert", {}), # Use imported COMPONENTS_STYLES
        )

    # --- Layout Structure ---
    dielectric_layout = html.Div(
        [
            # <<< REMOVIDOS dcc.Store definidos aqui >>>
            # Os stores globais ('dieletric-analysis-store', 'transformer-inputs-store', etc.)
            # JÁ ESTÃO definidos em components/global_stores.py e incluídos no layout principal
            # Primeira seção - Informações do Transformador (Container a ser preenchido)
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    # Div onde o painel será renderizado - usando ID único para evitar conflitos
                                    html.Div(
                                        id="transformer-info-dieletric-page",
                                        className=SPACING_STYLES.get("row_margin", "mb-3"),
                                    ),
                                    # Div oculta para compatibilidade com o callback global_updates
                                    # Inicializado com conteúdo vazio para garantir que exista antes do callback
                                    html.Div(
                                        html.Div(),
                                        id="transformer-info-dieletric",
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
                                        id="transformer-info-applied",
                                        style={"display": "none"},
                                    ),
                                    html.Div(
                                        html.Div(),
                                        id="transformer-info-induced",
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
                className=SPACING_STYLES.get("row_margin", "mb-3"),
            ),
            # Título principal do módulo (como antes)
            dbc.Card(
                [
                    dbc.CardHeader(
                        html.Div(
                            [
                                html.H6(
                                    "ANÁLISE DIELÉTRICA",
                                    className="text-center m-0 d-inline-block",
                                    style=TYPOGRAPHY_STYLES.get("card_header", {}),
                                ),
                                create_help_button(
                                    "dielectric_analysis", "Ajuda sobre Análise Dielétrica"
                                ),
                            ],
                            className="d-flex align-items-center justify-content-center",
                        ),
                        style=COMPONENTS_STYLES.get("card_header", {}),
                    ),
                    dbc.CardBody(
                        [
                            # Linha principal com 4 colunas (AT, BT, Ter, Resultados/Info)
                            dbc.Row(
                                [
                                    # Coluna AT
                                    dbc.Col(
                                        create_dielectric_input_column(
                                            verificador_instance, "Alta Tensão", "at"
                                        ),
                                        md=3,
                                        className=SPACING_STYLES.get("col_padding", "px-2"),
                                    ),
                                    # Coluna BT
                                    dbc.Col(
                                        create_dielectric_input_column(
                                            verificador_instance, "Baixa Tensão", "bt"
                                        ),
                                        md=3,
                                        className=SPACING_STYLES.get("col_padding", "px-2"),
                                    ),
                                    # Coluna Terciário
                                    dbc.Col(
                                        create_dielectric_input_column(
                                            verificador_instance, "Terciário", "terciario"
                                        ),
                                        md=3,
                                        className=SPACING_STYLES.get("col_padding", "px-2"),
                                    ),
                                    # Coluna Direita: Informações Complementares e Resultados
                                    dbc.Col(
                                        [
                                            dbc.Card(
                                                [
                                                    dbc.CardHeader(
                                                        html.H6(
                                                            "Informações e Resultados",
                                                            className="m-0",
                                                            style=TYPOGRAPHY_STYLES.get("card_header", {}),
                                                        ),
                                                        style=COMPONENTS_STYLES.get("card_header", {}),
                                                    ),
                                                    dbc.CardBody(
                                                        [
                                                            html.H6(
                                                                "Informações Complementares",
                                                                className="text-center mb-2",
                                                                style=TYPOGRAPHY_STYLES.get("section_title", {}),
                                                            ),
                                                            dbc.Row(
                                                                [
                                                                    dbc.Col(
                                                                        html.Label(
                                                                            "Tipo Isolamento:",
                                                                            style=TYPOGRAPHY_STYLES.get("label", {}),
                                                                        ),
                                                                        width=6,
                                                                    ),
                                                                    dbc.Col(
                                                                        html.Div(
                                                                            id="tipo-isolamento",
                                                                            children="-",
                                                                            style=COMPONENTS_STYLES.get("read_only", {}),
                                                                        ),
                                                                        width=6,
                                                                    ),  # Conteúdo via callback
                                                                ],
                                                                className=f"{SPACING_STYLES.get('row_gutter', 'g-3')} mb-1 align-items-center",
                                                            ),
                                                            dbc.Row(
                                                                [
                                                                    dbc.Col(
                                                                        html.Label(
                                                                            "Tipo Trafo:",
                                                                            style=TYPOGRAPHY_STYLES.get("label", {}),
                                                                        ),
                                                                        width=6,
                                                                    ),
                                                                    dbc.Col(
                                                                        html.Div(
                                                                            id="display-tipo-transformador-dieletric",
                                                                            children="-",
                                                                            style=COMPONENTS_STYLES.get("read_only", {}),
                                                                        ),
                                                                        width=6,
                                                                    ),  # Conteúdo via callback
                                                                ],
                                                                className=f"{SPACING_STYLES.get('row_gutter', 'g-3')} mb-1 align-items-center",
                                                            ),
                                                            # Divs ocultas como antes
                                                            html.Div(
                                                                [
                                                                    html.Div(
                                                                        id="display-tensao-aplicada-at-dieletric",
                                                                        style={"display": "none"},
                                                                    ),
                                                                    html.Div(
                                                                        id="display-tensao-aplicada-bt-dieletric",
                                                                        style={"display": "none"},
                                                                    ),
                                                                    html.Div(
                                                                        id="display-tensao-aplicada-terciario-dieletric",
                                                                        style={"display": "none"},
                                                                    ),
                                                                ],
                                                                style={"display": "none"},
                                                            ),
                                                            html.Div(
                                                                dcc.Input(
                                                                    id="tipo_transformador",
                                                                    type="hidden",
                                                                    value=None,
                                                                ),
                                                                style={"display": "none"},
                                                            ),  # Mantido para compatibilidade
                                                            html.Hr(className="my-2"),
                                                            dbc.Row(
                                                                [
                                                                    dbc.Col(
                                                                        dbc.Button(
                                                                            [
                                                                                html.I(
                                                                                    className="fas fa-save me-1"
                                                                                ),
                                                                                "Salvar Parâmetros",
                                                                            ],
                                                                            id="save-dielectric-params-btn",
                                                                            color="success",
                                                                            className="mb-2 w-100",
                                                                            size="sm",
                                                                        ),
                                                                        width=12,
                                                                    ),
                                                                ]
                                                            ),
                                                            html.Div(
                                                                id="dielectric-save-confirmation",
                                                                className="text-center",
                                                                style={"minHeight": "20px"},
                                                            ),
                                                            html.Hr(className="my-2"),
                                                            dbc.Row(
                                                                [
                                                                    dbc.Col(
                                                                        [
                                                                            dbc.Button(
                                                                                [
                                                                                    html.I(
                                                                                        className="fas fa-search-plus me-1"
                                                                                    ),
                                                                                    "Análise Dielétrica Completa",
                                                                                ],
                                                                                href="/analise-dieletrica-completa",
                                                                                color="info",
                                                                                className="mt-2 mb-2 w-100",
                                                                                size="sm",
                                                                            )
                                                                        ],
                                                                        width=12,
                                                                    ),
                                                                ]
                                                            ),
                                                            html.Div(
                                                                id="area-informacoes-adicionais"
                                                            ),  # Área vazia
                                                        ],
                                                        style=COMPONENTS_STYLES.get("card_body", {}),
                                                    ),
                                                ],
                                                className="h-100",
                                                style=COMPONENTS_STYLES.get("card", {}),
                                            )
                                        ],
                                        md=3,
                                        className=SPACING_STYLES.get("col_padding", "px-2"),
                                    ),
                                ],
                                className=SPACING_STYLES.get("row_gutter", "g-3"),
                            ),
                            # Container para Alertas (como antes)
                            dbc.Row(
                                [dbc.Col(html.Div(id="alert-container-dieletric"), width=12)],
                                className="mt-2",
                            ),
                        ]
                    ),  # Fechamento do CardBody Principal
                ]
            ),  # Fechamento do Card Principal
        ],
        style={"padding": "0.25rem"},
    )

    return dbc.Container(dielectric_layout, fluid=True, style=COMPONENTS_STYLES.get("container", {}))
