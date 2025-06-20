# utils/theme_colors.py
"""
Centralizes the definitions of colors for light and dark themes.
These should match the CSS variables defined in the assets folder.
"""

# --- Paleta de Cores para o Tema Escuro ---
# Corresponde às variáveis CSS em assets/theme-dark-vars.css
DARK_COLORS = {
    # Cores principais (--dark-primary, --dark-secondary, --dark-accent)
    "primary": "#26427A",  # Azul principal (WEG-like)
    "secondary": "#6c757d",  # Cinza padrão
    "accent": "#00BFFF",  # Azul Ciano/Neon para cyberpunk
    "accent_alt": "#FFD700",  # Dourado/Amarelo como alternativa
    # Cores de fundo (--dark-background-*)
    "background_main": "#1a1a1a",  # Fundo principal mais escuro
    "background_card": "#2c2c2c",  # Fundo de cards cinza escuro
    "background_card_header": "#1f1f1f",  # Fundo de cabeçalhos (quase preto)
    "background_input": "#3a3a3a",  # Fundo de inputs (cinza médio)
    "background_header": "#1f1f1f",  # Fundo para cabeçalhos de tabela (igual card header)
    "background_faint": "#333333",  # Fundo sutil para elementos de destaque
    # Cores de texto (--dark-text-*)
    "text_light": "#e0e0e0",  # Texto claro (branco acinzentado)
    "text_dark": "#e0e0e0",  # Texto escuro (alterado para claro no tema escuro)
    "text_muted": "#a0a0a0",  # Texto atenuado (cinza claro)
    "text_header": "#FFFFFF",  # Texto para cabeçalhos (branco)
    # Cores de borda (--dark-border*)
    "border": "#444444",  # Borda cinza médio-escuro
    "border_light": "#555555",  # Borda clara sutil
    "border_strong": "#666666",  # Borda mais visível
    # Cores de status (--dark-success, --dark-danger, etc.)
    "success": "#28a745",  # Verde
    "danger": "#dc3545",  # Vermelho
    "warning": "#ffc107",  # Amarelo
    "info": "#00BFFF",  # Azul Ciano (Accent)
    "pass": "#28a745",  # Alias para sucesso
    "fail": "#dc3545",  # Alias para perigo
    # Cores para fundos de status (--dark-pass-bg, --dark-fail-bg, etc.)
    "pass_bg": "rgba(40, 167, 69, 0.2)",  # Fundo verde transparente
    "fail_bg": "rgba(220, 53, 69, 0.2)",  # Fundo vermelho transparente
    "warning_bg": "rgba(255, 193, 7, 0.2)",  # Fundo amarelo transparente
    # Cores para fundos de status em tabelas (mais opacos)
    "danger_bg": "#5c1c1c",
    "danger_bg_faint": "rgba(220, 53, 69, 0.3)",  # Faint Red BG
    "danger_text": "#f8d7da",  # Light Red Text
    "warning_bg_faint": "rgba(255, 193, 7, 0.3)",  # Faint Yellow BG
    "warning_high_bg_faint": "rgba(255, 165, 0, 0.3)",  # Faint Orange BG
    "warning_text": "#fff3cd",  # Light Yellow Text
    "ok_bg_faint": "rgba(40, 167, 69, 0.3)",  # Faint Green BG
    "ok_text": "#d1e7dd",  # Light Green Text
    "info_bg_faint": "rgba(0, 191, 255, 0.2)",  # Faint Cyan BG
    # Cores para relatórios PDF (ajustar conforme necessário)
    "reportlab_primary": "#26427A",
    "reportlab_secondary": "#495057",
    "reportlab_header_bg": "#1f1f1f",
    "reportlab_header_text": "#FFFFFF",
    "reportlab_cell_bg": "#2c2c2c",
    "reportlab_grid": "#444444",
}

# --- Paleta de Cores para o Tema Claro ---
# Corresponde às variáveis CSS em assets/theme-light-vars.css
LIGHT_COLORS = {
    # Cores principais
    "primary": "#26427A",  # Azul principal (WEG-like)
    "secondary": "#6c757d",  # Cinza padrão
    "accent": "#007BFF",  # Azul de destaque
    "accent_alt": "#FFD700",  # Dourado/Amarelo
    # Cores de fundo
    "background_main": "#f0f2f5",  # Fundo principal (cinza muito claro)
    "background_card": "#ffffff",  # Fundo de cards (branco)
    "background_card_header": "#e9ecef",  # Fundo de cabeçalhos (cinza claro)
    "background_input": "#ffffff",  # Fundo de inputs (branco)
    "background_header": "#26427A",  # Fundo para cabeçalhos de tabela (azul escuro)
    "background_faint": "#f5f5f5",  # Fundo sutil para elementos de destaque
    # Cores de texto
    "text_light": "#f8f9fa",  # Texto claro (quase branco)
    "text_dark": "#212529",  # Texto escuro (preto/cinza escuro)
    "text_muted": "#6c757d",  # Texto atenuado (cinza médio)
    "text_header": "#FFFFFF",  # Texto para cabeçalhos (branco)
    # Cores de borda
    "border": "#dee2e6",  # Borda cinza clara
    "border_light": "#f8f9fa",  # Borda muito clara
    "border_strong": "#adb5bd",  # Borda cinza média
    # Cores de status
    "success": "#198754",
    "danger": "#dc3545",
    "warning": "#ffc107",
    "info": "#0dcaf0",
    "pass": "#198754",
    "fail": "#dc3545",
    # Cores para fundos de status
    "pass_bg": "#d1e7dd",  # Fundo verde claro
    "fail_bg": "#f8d7da",  # Fundo vermelho claro
    "warning_bg": "#fff3cd",  # Fundo amarelo claro
    # Cores para fundos de status em tabelas (pode usar os mesmos)
    "danger_bg": "#f8d7da",
    "danger_bg_faint": "rgba(248, 215, 218, 0.5)",
    "danger_text": "#842029",
    "warning_bg_faint": "rgba(255, 243, 205, 0.5)",
    "warning_high_bg_faint": "rgba(255, 235, 153, 0.5)",
    "warning_text": "#664d03",
    "ok_bg_faint": "rgba(209, 231, 221, 0.5)",
    "ok_text": "#0f5132",
    "info_bg_faint": "rgba(207, 244, 252, 0.5)",
    # Cores para relatórios PDF (ajustar conforme necessário)
    "reportlab_primary": "#26427A",
    "reportlab_secondary": "#495057",
    "reportlab_header_bg": "#26427A",
    "reportlab_header_text": "#FFFFFF",
    "reportlab_cell_bg": "#F8F9FA",
    "reportlab_grid": "#ADB5BD",
}

# --- Default Application Colors (Dark Theme) ---
APP_COLORS = DARK_COLORS

# --- Centralized Component Styles (Based on APP_COLORS) ---
COMPONENTS_STYLES = {
    "card": {"backgroundColor": APP_COLORS["background_card"], "border": f'1px solid {APP_COLORS["border"]}', "borderRadius": "4px", "boxShadow": "0 2px 5px rgba(0,0,0,0.25)", "marginBottom": "0.75rem"},
    "card_header": {"backgroundColor": APP_COLORS["background_card_header"], "color": APP_COLORS["text_header"], "padding": "0.4rem 0.75rem", "fontSize": "1rem", "fontWeight": "bold", "letterSpacing": "0.02em", "textTransform": "uppercase", "borderBottom": f'1px solid {APP_COLORS["border_strong"]}'},
    "card_body": {"padding": "0.75rem", "backgroundColor": APP_COLORS["background_card"]},
    "input": {"backgroundColor": APP_COLORS["background_input"], "color": APP_COLORS["text_light"], "border": f'1px solid {APP_COLORS["border"]}', "borderRadius": "3px", "padding": "0.3rem 0.5rem", "fontSize": "0.8rem"},
    "dropdown": {"backgroundColor": APP_COLORS["background_input"], "color": APP_COLORS.get("text_header", "#FFFFFF"), "border": f'1px solid {APP_COLORS["border"]}', "borderRadius": "3px"}, # Changed color to text_header
    "read_only": {"backgroundColor": APP_COLORS["background_card_header"], "color": APP_COLORS["text_muted"], "border": f'1px solid {APP_COLORS["border"]}', "borderRadius": "3px", "padding": "0.3rem 0.5rem", "fontSize": "0.8rem"},
    "button": {"backgroundColor": APP_COLORS["primary"], "color": APP_COLORS["text_header"]}, # Generic button
    "button_primary": {"backgroundColor": APP_COLORS["primary"], "color": APP_COLORS["text_header"]},
    "button_secondary": {"backgroundColor": APP_COLORS["secondary"], "color": APP_COLORS["text_header"]},
    "container": {"padding": "0.5rem 0.5rem 2rem 0.5rem", "maxWidth": "1400px", "margin": "0 auto"},
}

# --- Centralized Typography Styles (Based on APP_COLORS) ---
TYPOGRAPHY_STYLES = {
    "label": {"fontSize": "0.75rem", "fontWeight": "500", "color": APP_COLORS["text_light"]},
    "section_title": {"fontSize": "0.9rem", "fontWeight": "bold", "marginTop": "1rem", "marginBottom": "0.5rem", "color": APP_COLORS["text_light"]},
    "card_header": {"fontSize": "1rem", "fontWeight": "bold", "color": APP_COLORS["text_header"]}, # Already in COMPONENTS_STYLES, but can be here for text-specific aspects
    "title": {"fontSize": "1.1rem", "fontWeight": "bold", "color": APP_COLORS["accent"]},
    "small_text": {"fontSize": "0.7rem", "color": APP_COLORS["text_muted"]},
    "button": {"fontSize": "0.85rem", "fontWeight": "bold", "letterSpacing": "0.02em"}, # Text style for buttons
    "error_text": {"fontSize": "0.8rem", "color": APP_COLORS["danger"], "textAlign": "center"},
}

# --- Centralized Spacing Styles ---
SPACING_STYLES = {
    "row_margin": "mb-3",
    "row_gutter": "g-3",
    "col_padding": "px-2",
    "form_group_margin": "mb-2", # Example, can be expanded
}
