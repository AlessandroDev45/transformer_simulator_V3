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
    from dash import html
    import dash_bootstrap_components as dbc
    return dbc.Card([
        dbc.CardHeader(html.H6(label, className="m-0")),
        dbc.CardBody([html.Div(f"Inputs para {label} ({identifier})")])
    ])

# Importações para obter dados do transformador
# <<< REMOVIDO import direto de 'app' >>>
# from app import app
log = logging.getLogger(__name__)

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
    "input": {"backgroundColor": COLORS["background_input"], "color": COLORS["text_light"], "border": f'1px solid {COLORS["border"]}', "borderRadius": "3px"},
    "dropdown": {"backgroundColor": COLORS["background_input"], "color": COLORS["text_light"], "border": f'1px solid {COLORS["border"]}', "borderRadius": "3px"},
    "read_only": {"backgroundColor": COLORS["background_card_header"], "color": COLORS["text_muted"], "border": f'1px solid {COLORS["border"]}', "borderRadius": "3px"},
    "alert": {"backgroundColor": COLORS["warning_bg"], "color": COLORS["warning"], "border": f'1px solid {COLORS["warning"]}', "borderRadius": "3px", "padding": "0.5rem"},
    "container": {"padding": "0.5rem 0.5rem 2rem 0.5rem", "maxWidth": "1400px", "margin": "0 auto"}
}
TYPOGRAPHY = {
    "label": {"fontSize": "0.75rem", "fontWeight": "500"},
    "section_title": {"fontSize": "0.9rem", "fontWeight": "bold", "marginTop": "1rem", "marginBottom": "0.5rem"},
    "card_header": {"fontSize": "1rem", "fontWeight": "bold"},
    "title": {"fontSize": "1.1rem", "fontWeight": "bold", "color": COLORS["accent"]},
    "small_text": {"fontSize": "0.7rem", "color": COLORS["text_muted"]},
    "button": {"fontSize": "0.85rem", "fontWeight": "bold", "letterSpacing": "0.02em"},
    "error_text": {"fontSize": "0.8rem", "color": COLORS["danger"]}
}
SPACING = {"row_margin": "mb-3", "row_gutter": "g-3", "col_padding": "px-2"}


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
            style=COMPONENTS["alert"],
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
                                        className=SPACING["row_margin"],
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
                className=SPACING["row_margin"],
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
                                    style=TYPOGRAPHY["card_header"],
                                ),
                                create_help_button(
                                    "dielectric_analysis", "Ajuda sobre Análise Dielétrica"
                                ),
                            ],
                            className="d-flex align-items-center justify-content-center",
                        ),
                        style=COMPONENTS["card_header"],
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
                                        className=SPACING["col_padding"],
                                    ),
                                    # Coluna BT
                                    dbc.Col(
                                        create_dielectric_input_column(
                                            verificador_instance, "Baixa Tensão", "bt"
                                        ),
                                        md=3,
                                        className=SPACING["col_padding"],
                                    ),
                                    # Coluna Terciário
                                    dbc.Col(
                                        create_dielectric_input_column(
                                            verificador_instance, "Terciário", "terciario"
                                        ),
                                        md=3,
                                        className=SPACING["col_padding"],
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
                                                            style=TYPOGRAPHY["card_header"],
                                                        ),
                                                        style=COMPONENTS["card_header"],
                                                    ),
                                                    dbc.CardBody(
                                                        [
                                                            html.H6(
                                                                "Informações Complementares",
                                                                className="text-center mb-2",
                                                                style=TYPOGRAPHY["section_title"],
                                                            ),
                                                            dbc.Row(
                                                                [
                                                                    dbc.Col(
                                                                        html.Label(
                                                                            "Tipo Isolamento:",
                                                                            style=TYPOGRAPHY[
                                                                                "label"
                                                                            ],
                                                                        ),
                                                                        width=6,
                                                                    ),
                                                                    dbc.Col(
                                                                        html.Div(
                                                                            id="tipo-isolamento",
                                                                            children="-",
                                                                            style=COMPONENTS[
                                                                                "read_only"
                                                                            ],
                                                                        ),
                                                                        width=6,
                                                                    ),  # Conteúdo via callback
                                                                ],
                                                                className=f"{SPACING['row_gutter']} mb-1 align-items-center",
                                                            ),
                                                            dbc.Row(
                                                                [
                                                                    dbc.Col(
                                                                        html.Label(
                                                                            "Tipo Trafo:",
                                                                            style=TYPOGRAPHY[
                                                                                "label"
                                                                            ],
                                                                        ),
                                                                        width=6,
                                                                    ),
                                                                    dbc.Col(
                                                                        html.Div(
                                                                            id="display-tipo-transformador-dieletric",
                                                                            children="-",
                                                                            style=COMPONENTS[
                                                                                "read_only"
                                                                            ],
                                                                        ),
                                                                        width=6,
                                                                    ),  # Conteúdo via callback
                                                                ],
                                                                className=f"{SPACING['row_gutter']} mb-1 align-items-center",
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
                                                        style=COMPONENTS["card_body"],
                                                    ),
                                                ],
                                                className="h-100",
                                                style=COMPONENTS["card"],
                                            )
                                        ],
                                        md=3,
                                        className=SPACING["col_padding"],
                                    ),
                                ],
                                className=SPACING["row_gutter"],
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

    return dbc.Container(dielectric_layout, fluid=True, style=COMPONENTS["container"])
