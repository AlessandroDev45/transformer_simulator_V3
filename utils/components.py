# utils/components.py

import dash_bootstrap_components as dbc
from utils.styles import COLORS, COMPONENTS, TYPOGRAPHY

def create_input_row(label, id, placeholder, input_type="number"):
    """Creates a standard input row with label."""
    label_style = TYPOGRAPHY.get(
        "label", {"fontSize": "0.65rem", "fontWeight": "bold", "color": COLORS["text_light"]}
    )
    input_base_style = COMPONENTS.get(
        "input",
        {
            "fontSize": "0.7rem",
            "color": COLORS["text_light"],
            "backgroundColor": COLORS["background_input"],
            "border": f"1px solid {COLORS['border']}",
        },
    )
    final_input_style = {
        **input_base_style,
        "height": "26px",
        "padding": "0.15rem 0.3rem",
        "width": "75%",
    }
    return dbc.Row(
        [
            dbc.Col(dbc.Label(label, style=label_style), width=9, className="text-end pe-1"),
            dbc.Col(
                dbc.Input(
                    type=input_type,
                    id=id,
                    placeholder=placeholder,
                    persistence=True,
                    persistence_type="local",
                    style=final_input_style,
                ),
                width=3,
            ),
        ],
        className="g-1 mb-1",
    )