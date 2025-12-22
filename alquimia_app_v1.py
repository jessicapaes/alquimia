import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import os
from pathlib import Path
from PIL import Image
import io
from streamlit_quill import st_quill
import requests
from urllib.parse import urlparse, parse_qs

# Pinterest integration
try:
    from pinterest_integration import (
        PinterestAPI, 
        extract_pinterest_url_info,
        download_image_from_url,
        get_pinterest_oauth_url,
        exchange_code_for_token,
        map_pins_to_vision_areas
    )
    PINTEREST_AVAILABLE = True
except ImportError:
    PINTEREST_AVAILABLE = False

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

DATA_FILE = "alquimia_data.json"
DEFAULT_RODA_SCORES = {
    'Saúde': 0,
    'Carreira': 0,
    'Finanças': 0,
    'Relacionamentos': 0,
    'Família': 0,
    'Espiritualidade': 0,
    'Diversão': 0,
    'Crescimento Pessoal': 0,
    'Ambiente Físico': 0,
    'Criatividade': 0
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_data():
    """Load data from JSON file if it exists"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Migrate old bilingual area names to Portuguese-only
                if 'roda_scores' in data:
                    old_to_new = {
                        'Saúde/Health': 'Saúde',
                        'Carreira/Career': 'Carreira',
                        'Finanças/Finances': 'Finanças',
                        'Relacionamentos/Relationships': 'Relacionamentos',
                        'Família/Family': 'Família',
                        'Espiritualidade/Spirituality': 'Espiritualidade',
                        'Diversão/Fun': 'Diversão',
                        'Crescimento Pessoal/Growth': 'Crescimento Pessoal',
                        'Ambiente Físico/Home': 'Ambiente Físico',
                        'Criatividade/Creativity': 'Criatividade'
                    }
                    
                    # Create new dict with migrated keys
                    migrated_scores = {}
                    for old_key, new_key in old_to_new.items():
                        if old_key in data['roda_scores']:
                            migrated_scores[new_key] = data['roda_scores'][old_key]
                        elif new_key in data['roda_scores']:
                            migrated_scores[new_key] = data['roda_scores'][new_key]
                    
                    # Update if migration happened
                    if migrated_scores:
                        data['roda_scores'] = migrated_scores
                
                # Migrate area names in smart_goals
                if 'smart_goals' in data:
                    old_to_new = {
                        'Saúde/Health': 'Saúde',
                        'Carreira/Career': 'Carreira',
                        'Finanças/Finances': 'Finanças',
                        'Relacionamentos/Relationships': 'Relacionamentos',
                        'Família/Family': 'Família',
                        'Espiritualidade/Spirituality': 'Espiritualidade',
                        'Diversão/Fun': 'Diversão',
                        'Crescimento Pessoal/Growth': 'Crescimento Pessoal',
                        'Ambiente Físico/Home': 'Ambiente Físico',
                        'Criatividade/Creativity': 'Criatividade'
                    }
                    
                    for goal in data['smart_goals']:
                        if 'area' in goal:
                            # Migrate area name if it's in old format
                            for old_key, new_key in old_to_new.items():
                                if goal['area'] == old_key:
                                    goal['area'] = new_key
                                    break
                
                return data
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
            return None
    return None

def save_data():
    """Save all session state data to JSON file"""
    try:
        data = {
            "roda_scores": st.session_state.roda_scores,
            "smart_goals": st.session_state.smart_goals,
            "reflections": {
                "conquistas_2025": st.session_state.get("conquistas_2025", ""),
                "desafios_2025": st.session_state.get("desafios_2025", ""),
                "aprendizados_2025": st.session_state.get("aprendizados_2025", ""),
                "gratidao_2025": st.session_state.get("gratidao_2025", "")
            },
            "vision_intentions": {
                area: st.session_state.get(f"vision_{area}", "")
                for area in [
                    "💼 Carreira & Projetos",
                    "🌿 Saúde & Bem-Estar",
                    "🔮 Espiritualidade",
                    "🦋 Crescimento Pessoal",
                    "💕 Amor Próprio",
                    "✈️ Viagens & Aventuras",
                    "💰 Abundância",
                    "🎨 Criatividade"
                ]
            },
            "archetype_scores": {
                key: st.session_state.get(key, 5)
                for key in st.session_state.keys()
                if key.startswith("arch_")
            },
            "history": st.session_state.get("history", []),
            "last_updated": datetime.now().isoformat()
        }
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar dados: {e}")
        return False

def create_vision_collage(images_dict, max_width=2000):
    """Create a collage from uploaded images"""
    all_images = []
    for area, imgs in images_dict.items():
        for img_file in imgs:
            try:
                img = Image.open(img_file)
                all_images.append(img)
            except:
                continue
    
    if not all_images:
        return None
    
    # Calculate grid dimensions
    num_images = len(all_images)
    cols = 4
    rows = (num_images + cols - 1) // cols
    
    # Resize images to consistent size
    img_size = max_width // cols
    resized_images = []
    for img in all_images:
        img_resized = img.resize((img_size, img_size), Image.Resampling.LANCZOS)
        resized_images.append(img_resized)
    
    # Create collage
    collage_width = img_size * cols
    collage_height = img_size * rows
    collage = Image.new('RGB', (collage_width, collage_height), color='white')
    
    for idx, img in enumerate(resized_images):
        row = idx // cols
        col = idx % cols
        x = col * img_size
        y = row * img_size
        collage.paste(img, (x, y))
    
    return collage

def analyze_roda_insights():
    """
    Analyzes Roda da Vida scores and existing goals to generate insights.
    Returns a dict with recommendations, priority areas, and metrics.
    """
    roda_scores = st.session_state.roda_scores
    smart_goals = st.session_state.smart_goals

    # Sort areas by score (ascending) to find lowest scores
    sorted_areas = sorted(roda_scores.items(), key=lambda x: x[1])

    # Define thresholds
    LOW_SCORE_THRESHOLD = 5
    CRITICAL_THRESHOLD = 3

    # Identify low-scoring areas
    low_areas = [(area, score) for area, score in sorted_areas if score <= LOW_SCORE_THRESHOLD]
    critical_areas = [(area, score) for area, score in sorted_areas if score <= CRITICAL_THRESHOLD]
    bottom_3_areas = sorted_areas[:3]

    # Analyze goal coverage for each area
    goals_by_area = {}
    for goal in smart_goals:
        area = goal['area']
        if area not in goals_by_area:
            goals_by_area[area] = {'total': 0, 'completed': 0, 'pending': 0}
        goals_by_area[area]['total'] += 1
        if goal.get('completed', False):
            goals_by_area[area]['completed'] += 1
        else:
            goals_by_area[area]['pending'] += 1

    # Generate insights
    insights = {
        'bottom_3': bottom_3_areas,
        'critical_areas': critical_areas,
        'low_areas': low_areas,
        'areas_without_goals': [],
        'priority_recommendations': []
    }

    # Generate priority recommendations for bottom 3
    for area, score in bottom_3_areas:
        rec = {
            'area': area,
            'score': score,
            'has_goals': area in goals_by_area,
            'goal_count': goals_by_area.get(area, {}).get('total', 0),
            'pending_count': goals_by_area.get(area, {}).get('pending', 0),
            'completed_count': goals_by_area.get(area, {}).get('completed', 0),
            'priority_level': 'critical' if score <= CRITICAL_THRESHOLD else 'high' if score <= 5 else 'medium'
        }

        # Generate specific message and action
        if not rec['has_goals']:
            rec['message'] = "Nenhuma meta criada ainda"
            rec['action'] = "create_first"
        elif rec['pending_count'] == 0 and rec['completed_count'] > 0:
            rec['message'] = f"Todas as {rec['goal_count']} meta(s) completadas, mas pontuação ainda baixa"
            rec['action'] = "create_more"
        elif rec['pending_count'] > 0:
            rec['message'] = f"{rec['pending_count']} meta(s) pendente(s)"
            rec['action'] = "focus_existing"
        else:
            rec['message'] = "Área precisa de atenção"
            rec['action'] = "create_first"

        insights['priority_recommendations'].append(rec)

    # Find areas without goals in low scoring areas
    for area, score in low_areas:
        if area not in goals_by_area:
            insights['areas_without_goals'].append({
                'area': area,
                'score': score,
                'severity': 'critical' if score <= CRITICAL_THRESHOLD else 'high'
            })

    return insights

def should_show_insights():
    """Determine if insights section should be displayed."""
    avg_score = sum(st.session_state.roda_scores.values()) / len(st.session_state.roda_scores)
    return avg_score < 7.5

def render_celebration():
    """Show celebration when all scores are high."""
    st.markdown("""
    <div class="glass-card" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
                                  border-left: 4px solid #10b981; margin: 1.5rem 0;">
        <h3 style="color: #1a202c; margin: 0 0 10px 0;">
            🌟 Excelente Equilíbrio!
        </h3>
        <p style="color: #334155; margin: 0; line-height: 1.6;">
            Suas pontuações da Roda da Vida estão ótimas! Continue criando metas para manter
            e aprimorar esse equilíbrio em 2026.
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_insight_card(rec):
    """Renders a single insight card for a Roda area."""
    area_name = rec['area']
    score = rec['score']

    # Area emojis mapping
    area_emojis = {
        "Saúde": "😊",
        "Carreira": "👩🏻‍💻",
        "Finanças": "💸",
        "Relacionamentos": "❤️",
        "Família": "🤗",
        "Espiritualidade": "🧘🏼‍♀️",
        "Diversão": "🎉",
        "Crescimento Pessoal": "🌱",
        "Ambiente Físico": "🏡",
        "Criatividade": "🎨"
    }

    # Get area emoji
    icon = area_emojis.get(area_name, "💡")

    # Determine visual styling
    if rec['priority_level'] == 'critical':
        border_color = "#ef4444"
        bg_color = "rgba(239, 68, 68, 0.05)"
    elif rec['priority_level'] == 'high':
        border_color = "#f59e0b"
        bg_color = "rgba(245, 158, 11, 0.05)"
    else:
        border_color = "#eab308"
        bg_color = "rgba(234, 179, 8, 0.05)"

    # Card HTML
    st.markdown(f"""
    <div style="background: white;
                padding: 1.5rem;
                border-radius: 16px;
                border-left: 5px solid {border_color};
                margin-bottom: 1.25rem;
                min-height: 200px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08), 0 2px 4px rgba(0, 0, 0, 0.04);
                transition: all 0.3s ease;
                border: 1px solid rgba(0, 0, 0, 0.06);">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 2rem; line-height: 1;">{icon}</span>
                <h4 style="color: #1a202c; margin: 0; font-size: 1.2rem; font-weight: 700;">
                    {area_name}
                </h4>
            </div>
            <span style="background: linear-gradient(135deg, {border_color} 0%, {border_color}dd 100%);
                         padding: 0.4rem 0.9rem;
                         border-radius: 24px;
                         font-size: 0.95rem;
                         font-weight: 700;
                         color: white;
                         box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);">
                {score}/10
            </span>
        </div>
        <p style="color: #475569; margin: 0 0 1rem 0; font-size: 0.98rem; line-height: 1.6;">
            {rec['message']}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # CTA Button
    if rec['action'] == 'create_first':
        button_label = f"✨ Criar Meta para {area_name}"
        button_key = f"cta_create_{rec['area']}"
        if st.button(button_label, key=button_key, use_container_width=True, type="primary"):
            st.session_state.prefill_area = rec['area']
            st.session_state.expand_goal_form = True
            st.rerun()

    elif rec['action'] == 'create_more':
        button_label = f"➕ Adicionar Mais Metas"
        button_key = f"cta_more_{rec['area']}"
        if st.button(button_label, key=button_key, use_container_width=True, type="primary"):
            st.session_state.prefill_area = rec['area']
            st.session_state.expand_goal_form = True
            st.rerun()

def render_roda_insights():
    """Renders the Roda da Vida insights section at the top of SMART Goals tab."""
    insights = analyze_roda_insights()

    # Only show if there are meaningful insights
    if not insights['priority_recommendations']:
        return

    st.markdown("""
    <div class="glass-card" style="margin: 2rem 0; padding: 0; overflow: hidden; border: 2px solid rgba(102, 126, 234, 0.15);">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 1.5rem 2rem;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);">
            <h3 style="color: white; margin: 0 0 0.5rem 0; font-size: 1.4rem; font-weight: 700; display: flex; align-items: center; gap: 0.75rem;">
                💡 Insights da Roda da Vida
            </h3>
            <p style="color: rgba(255, 255, 255, 0.95); margin: 0; font-size: 1rem; line-height: 1.5;">
                Áreas que Precisam de Atenção
            </p>
        </div>
        <div style="padding: 2rem;">
            <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
                        padding: 1.25rem 1.75rem; border-radius: 12px; margin-bottom: 2rem;
                        border: 1px solid rgba(102, 126, 234, 0.2);
                        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.08);">
                <p style="margin: 0; color: #1a202c; font-size: 1rem; line-height: 1.7; font-weight: 500;">
                    ✨ <strong style="color: #667eea;">Baseado na sua Roda da Vida 2025,</strong> identificamos áreas que podem se beneficiar
                    de metas SMART para transformação em 2026.
                </p>
            </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():

        # Render recommendations in columns
        if len(insights['priority_recommendations']) >= 3:
            cols = st.columns(3)
        else:
            cols = st.columns(len(insights['priority_recommendations']))

        for idx, rec in enumerate(insights['priority_recommendations']):
            with cols[idx]:
                render_insight_card(rec)

        # Button removed per user request

        # Additional context for areas without goals
        if insights['areas_without_goals'] and len(insights['areas_without_goals']) > 3:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.03) 100%);
                        padding: 1.25rem 1.5rem;
                        border-radius: 12px;
                        margin-top: 1.5rem;
                        border: 1px solid rgba(102, 126, 234, 0.15);">
                <h4 style="color: #667eea; margin: 0 0 0.75rem 0; font-size: 1.1rem; font-weight: 700;">
                    🎯 Outras Áreas sem Metas
                </h4>
            </div>
            """, unsafe_allow_html=True)
            areas_text = ", ".join([item['area'] for item in insights['areas_without_goals'][3:]])
            st.markdown(f"<p style='color: #64748b; margin: 0.75rem 0 0 0; font-size: 0.95rem;'>Também considere criar metas para: <strong style='color: #1a202c;'>{areas_text}</strong></p>", unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize or load session state from file"""
    data = load_data()
    
    if data:
        # Load saved data - ALWAYS update roda_scores from file
        st.session_state.roda_scores = data.get("roda_scores", DEFAULT_RODA_SCORES).copy()
        st.session_state.smart_goals = data.get("smart_goals", [])
        st.session_state.history = data.get("history", [])
        
        # Load reflections
        reflections = data.get("reflections", {})
        for key, value in reflections.items():
            if key not in st.session_state:
                st.session_state[key] = value
        
        # Load vision intentions
        vision_intentions = data.get("vision_intentions", {})
        for area, value in vision_intentions.items():
            key = f"vision_{area}"
            if key not in st.session_state:
                st.session_state[key] = value
        
        # Load archetype scores
        archetype_scores = data.get("archetype_scores", {})
        for key, value in archetype_scores.items():
            if key not in st.session_state:
                st.session_state[key] = value
    else:
        # Initialize with defaults
        st.session_state.roda_scores = DEFAULT_RODA_SCORES.copy()
        st.session_state.smart_goals = []
        st.session_state.history = []

        # Initialize reflection fields
        reflection_keys = [
            "conquistas_2025", "desafios_2025", "aprendizados_2025", "gratidao_2025"
        ]
        for key in reflection_keys:
            if key not in st.session_state:
                st.session_state[key] = ""

    # Initialize vision_images (always needed regardless of data load)
    if 'vision_images' not in st.session_state:
        st.session_state.vision_images = {
            "💼 Carreira & Projetos": [],
            "🌿 Saúde & Bem-Estar": [],
            "🔮 Espiritualidade": [],
            "🦋 Crescimento Pessoal": [],
            "💕 Amor Próprio": [],
            "✈️ Viagens & Aventuras": [],
            "💰 Abundância": [],
            "🎨 Criatividade": []
        }
    
    # Migrate old area names to new ones
    old_to_new_mapping = {
        "🌸 EVA - Minha Criação Sagrada": "💼 Carreira & Projetos",
        "🇮🇹 Italia & Aventuras": "✈️ Viagens & Aventuras"
    }
    
    # Migrate vision_images
    if 'vision_images' in st.session_state:
        for old_name, new_name in old_to_new_mapping.items():
            if old_name in st.session_state.vision_images:
                st.session_state.vision_images[new_name] = st.session_state.vision_images.pop(old_name)
        
        # Ensure all new keys exist
        for area in ["💼 Carreira & Projetos", "🌿 Saúde & Bem-Estar", "🔮 Espiritualidade", 
                     "🦋 Crescimento Pessoal", "💕 Amor Próprio", "✈️ Viagens & Aventuras", 
                     "💰 Abundância", "🎨 Criatividade"]:
            if area not in st.session_state.vision_images:
                st.session_state.vision_images[area] = []

def add_to_history():
    """Add current roda scores to history for progress tracking"""
    if "history" not in st.session_state:
        st.session_state.history = []
    
    entry = {
        "date": datetime.now().isoformat(),
        "roda_scores": st.session_state.roda_scores.copy(),
        "avg_score": sum(st.session_state.roda_scores.values()) / len(st.session_state.roda_scores)
    }
    st.session_state.history.append(entry)
    
    # Keep only last 12 entries (monthly check-ins for a year)
    if len(st.session_state.history) > 12:
        st.session_state.history = st.session_state.history[-12:]

def create_radar_chart(values, categories, name='2025', show_target=False, target_values=None):
    """Create a radar chart with purple gradient theme matching app design"""
    fig = go.Figure()
    
    # Main trace with purple gradient fill
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(102, 126, 234, 0.25)',  # Purple with transparency
        line=dict(
            color='#667eea',  # Purple line
            width=4,
            smoothing=1.3
        ),
        marker=dict(
            size=10,
            color='#764ba2',  # Darker purple for markers
            line=dict(width=2, color='white')
        ),
        name=name,
        hovertemplate='<b>%{theta}</b><br>Score: %{r}/10<extra></extra>'
    ))
    
    if show_target and target_values:
        fig.add_trace(go.Scatterpolar(
            r=target_values,
            theta=categories,
            fill='toself',
            fillcolor='rgba(236, 72, 153, 0.15)',  # Pink for target
            line=dict(
                color='#ec4899',  # Pink line
                width=3,
                dash='dash',
                smoothing=1.3
            ),
            marker=dict(
                size=8,
                color='#ec4899',
                line=dict(width=2, color='white')
            ),
            name='Target 2026',
            hovertemplate='<b>%{theta}</b><br>Target: %{r}/10<extra></extra>'
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                tickmode='linear',
                tick0=0,
                dtick=2,
                tickfont=dict(
                    size=13,
                    color='#64748b',
                    family='Inter'
                ),
                gridcolor='rgba(102, 126, 234, 0.15)',
                gridwidth=1,
                linecolor='rgba(102, 126, 234, 0.3)',
                linewidth=2,
                showline=True,
                layer='below traces'
            ),
            angularaxis=dict(
                tickfont=dict(
                    size=13,
                    color='#334155',
                    family='Inter',
                    weight=600
                ),
                gridcolor='rgba(102, 126, 234, 0.1)',
                gridwidth=1,
                linecolor='rgba(102, 126, 234, 0.2)',
                linewidth=1,
                rotation=90,
                direction='counterclockwise'
            ),
            bgcolor='rgba(255, 255, 255, 0.95)',
            hole=0.1  # Add inner hole for modern look
        ),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.15,
            xanchor='center',
            x=0.5,
            font=dict(
                size=14,
                color='#334155',
                family='Inter',
                weight=600
            ),
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='rgba(102, 126, 234, 0.2)',
            borderwidth=0
        ),
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent to match app background
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            color='#1a202c',
            family='Inter',
            size=14
        ),
        height=650,
        margin=dict(l=50, r=50, t=50, b=120),
        hovermode='closest',
        hoverlabel=dict(
            bgcolor='rgba(255, 255, 255, 0.95)',
            bordercolor='#667eea',
            font_size=13,
            font_family='Inter',
            font_color='#1a202c'
        )
    )
    
    return fig

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Meu Plano de 2026",
    page_icon="📔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS
# ============================================================================

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
    /* CSS Layer with highest priority - CANNOT be overridden */
    @layer streamlit-override {
        [data-testid="stTabs"] {
            padding: 2rem 3rem 3rem 3rem !important;
            margin: 2rem -3rem 3rem -3rem !important;
            width: calc(100% + 6rem) !important;
            max-width: calc(100% + 6rem) !important;
            background: rgba(255, 255, 255, 0.98) !important;
            backdrop-filter: blur(10px) !important;
            border-radius: 25px !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07),
                        0 10px 15px rgba(0, 0, 0, 0.1),
                        0 20px 25px rgba(0, 0, 0, 0.08) !important;
            border: 1px solid rgba(0, 0, 0, 0.05) !important;
            box-sizing: border-box !important;
            position: relative !important;
        }
    }

    .main {
        background: #f8f9fa;
    }
    .stApp {
        background: #f8f9fa;
    }
    /* Page container margins and padding */
    .block-container {
        padding-left: 3rem !important;
        padding-right: 3rem !important;
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
    }
    h1 {
        font-family: 'Cinzel', serif;
        color: #667eea;
        text-align: center;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    h2 {
        font-family: 'Cormorant Garamond', serif;
        color: #764ba2;
    }
    
    /* Header banner - Top tag inside purple box (Bearable style) */
    .header-banner {
        background: rgba(255, 255, 255, 0.2) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 12px !important;
        padding: 0.5rem 1rem !important;
        margin: 0 auto 1.5rem auto !important;
        display: block !important;
        width: fit-content !important;
        text-align: center !important;
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        color: white !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif !important;
    }
    
    /* Header box - Purple gradient card container (Bearable style) */
    .header-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 25px !important;
        padding: 3rem 2rem !important;
        margin: 0 auto 3rem auto !important;
        max-width: 1200px !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07),
                    0 10px 15px rgba(0, 0, 0, 0.1),
                    0 20px 25px rgba(0, 0, 0, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        text-align: center !important;
    }
    
    /* Header title styling - white text on purple background (Bearable size) */
    .header-title {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif !important;
        color: white !important;
        text-align: center !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2) !important;
        margin: 0 0 1rem 0 !important;
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        line-height: 1.2 !important;
        letter-spacing: -0.5px !important;
    }
    
    /* Header subtitle styling - white text below title (Bearable style) */
    .header-subtitle {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif !important;
        color: white !important;
        text-align: center !important;
        margin: 0 !important;
        font-size: 1.5rem !important;
        font-weight: 500 !important;
        line-height: 1.4 !important;
        opacity: 0.95 !important;
    }
    
    h3 {
        color: #667eea;
    }
    /* TABS - Modern Design with white box around tab buttons */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(10px) !important;
        padding: 15px !important;
        border-radius: 20px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08),
                    0 2px 4px rgba(0, 0, 0, 0.06) !important;
        width: 100% !important;
        box-sizing: border-box !important;
        margin: 0 0 1.5rem 0 !important;
        max-width: none !important;
        border-bottom: none !important;
        display: flex !important;
        flex-wrap: wrap !important;
        justify-content: flex-start !important;
        overflow: visible !important;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        border: none !important;
        border-bottom: none !important;
        background-color: transparent !important;
        color: #334155 !important;
        white-space: nowrap !important;
        flex-shrink: 0 !important;
        overflow: visible !important;
        position: relative !important;
        z-index: 1 !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(102, 126, 234, 0.1) !important;
        transform: translateY(-2px) !important;
        color: #667eea !important;
        border: none !important;
        border-bottom: none !important;
        text-decoration: none !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3) !important;
        border: none !important;
        border-bottom: none !important;
    }
    
    /* Ensure text stays white on selected tab - all child elements */
    .stTabs [aria-selected="true"] * {
        color: white !important;
    }
    
    /* Selected tab on click/active */
    .stTabs [aria-selected="true"]:active,
    .stTabs [aria-selected="true"]:focus,
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: white !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    .stTabs [aria-selected="true"]:active *,
    .stTabs [aria-selected="true"]:focus *,
    .stTabs [data-baseweb="tab"][aria-selected="true"] * {
        color: white !important;
    }
    
    /* Remove tab underline/indicator bar */
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: transparent !important;
        display: none !important;
    }
    
    .stTabs [data-baseweb="tab-border"] {
        background-color: transparent !important;
        display: none !important;
    }
    
    /* Remove any red default underlines on tabs */
    button[data-baseweb="tab"] {
        border: none !important;
        border-bottom: none !important;
        text-decoration: none !important;
    }
    
    button[data-baseweb="tab"]:hover {
        border: none !important;
        border-bottom: none !important;
        text-decoration: none !important;
    }
    
    button[data-baseweb="tab"]:focus {
        border: none !important;
        border-bottom: none !important;
        text-decoration: none !important;
        outline: none !important;
    }
    
    button[data-baseweb="tab"]:active {
        border: none !important;
        border-bottom: none !important;
        text-decoration: none !important;
    }
    /* White container box - Bearable Style with negative margins */
    .stTabs,
    div[data-testid="stTabs"],
    section[data-testid="stTabs"],
    [data-testid="stTabs"],
    div.stTabs,
    section.stTabs {
        background: rgba(255, 255, 255, 0.98) !important;
        background-color: rgba(255, 255, 255, 0.98) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border-radius: 25px !important;
        padding: 2rem 3rem 3rem 3rem !important;
        margin: 2rem -3rem 3rem -3rem !important;
        width: calc(100% + 6rem) !important;
        max-width: calc(100% + 6rem) !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07) !important,
                    0 10px 15px rgba(0, 0, 0, 0.1) !important,
                    0 20px 25px rgba(0, 0, 0, 0.08) !important;
        border: 1px solid rgba(0, 0, 0, 0.05) !important;
        box-sizing: border-box !important;
        position: relative !important;
    }

    /* Pseudo-element background that persists */
    .stTabs::before,
    [data-testid="stTabs"]::before {
        content: "" !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        bottom: 0 !important;
        background: #ffffff !important;
        border-radius: 25px !important;
        z-index: -1 !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07),
                    0 10px 15px rgba(0, 0, 0, 0.1),
                    0 20px 25px rgba(0, 0, 0, 0.08) !important;
    }

    /* Make sure child divs don't override the background or padding */
    [data-testid="stTabs"] > div,
    [data-testid="stTabs"] > div:first-child,
    [data-testid="stTabs"] > div:last-child,
    .stTabs > div,
    .stTabs > div:first-child,
    .stTabs > div:last-child {
        background: transparent !important;
        background-color: transparent !important;
        padding-top: 1.5rem !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }

    /* Force padding with keyframe animation trick */
    @keyframes keepPadding {
        0%, 100% {
            padding: 2rem 3rem 3rem 3rem !important;
            margin: 2rem 0 3rem 0 !important;
        }
    }

    .stTabs,
    [data-testid="stTabs"] {
        animation: keepPadding 0.001s infinite !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2em;
        color: #667eea;
    }

    /* HOW IT WORKS CARDS - Hover Effect */
    .how-it-works-card {
        transition: all 0.3s ease !important;
    }

    .how-it-works-card:hover {
        transform: translateY(-8px) !important;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.2) !important;
        border-color: #667eea !important;
    }

    /* Hide anchor link icons and remove decorations from how-it-works card titles */
    .how-it-works-card h3 {
        text-decoration: none !important;
        border: none !important;
        text-align: center !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }

    .how-it-works-card h3 a,
    .how-it-works-card h3 .header-link,
    .how-it-works-card h3 .header-anchor {
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
        text-decoration: none !important;
        border-bottom: none !important;
    }

    /* Remove any orange underlines and center all text in titles */
    .how-it-works-card h3 *,
    .how-it-works-card h3 span,
    .how-it-works-card h3::after,
    .how-it-works-card h3::before {
        text-decoration: none !important;
        border-bottom: none !important;
        text-align: center !important;
        display: inline !important;
        width: auto !important;
    }

    /* Force centering on all content inside how-it-works h3 */
    .how-it-works-card h3 > * {
        margin: 0 auto !important;
        text-align: center !important;
    }

    /* PREMIUM CARDS - Clean White Boxes (Bearable Style) */
    .glass-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 30px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
        position: relative;
        overflow: visible;
    }
    
    .glass-card::before {
        display: none;
    }
    
    .glass-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-color: #cbd5e1;
    }

    .glass-card:hover::before {
        display: none;
    }
    
    /* Section Headers - Gradient Background (From Bearable) */
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 2rem 0 1rem 0;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
    }
    
    .section-header h3 {
        color: white !important;
        margin: 0;
        font-size: 1.4rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    
    .section-header p {
        color: rgba(255,255,255,0.9);
        margin: 0.3rem 0 0 0;
        font-size: 0.9rem;
    }
    
    /* Goal Cards - Enhanced with smooth transitions */
    .goal-card {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .goal-card:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12), 0 4px 8px rgba(102, 126, 234, 0.15) !important;
    }
    
    /* Archetype Card - Updated to match Bearable */
    .archetype-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        padding: 20px;
        border-radius: 20px;
        border-left: 6px solid #667eea;
        margin: 10px 0;
        box-shadow: 0 8px 30px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .archetype-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2);
    }
    
    /* Success/Info Messages - Updated */
    .success-message {
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid #10b981;
        padding: 15px 20px;
        border-radius: 12px;
        margin: 10px 0;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.15);
    }
    
    /* Clean section spacing */
    .element-container {
        margin-bottom: 1.5rem;
    }
    
    /* BUTTONS - Modern sleek design (From Bearable) */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        font-size: 0.95rem !important;
        border: 2px solid #e2e8f0 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
        background: white !important;
        color: #334155 !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2) !important;
        border-color: #667eea !important;
        background: #f8f9ff !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Primary buttons - Purple gradient */
    .stButton > button[kind="primary"],
    button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
    }

    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
        background: linear-gradient(135deg, #5568d3 0%, #6a3f91 100%) !important;
    }

    /* Secondary/Delete Buttons - Soft style */
    .stButton > button:not([kind="primary"]) {
        background: white !important;
        color: #64748b !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
    }

    .stButton > button:not([kind="primary"]):hover {
        background: #fee2e2 !important;
        color: #dc2626 !important;
        border-color: #fecaca !important;
        box-shadow: 0 4px 12px rgba(220, 38, 38, 0.15) !important;
        transform: translateY(-1px) !important;
    }
    
    /* FORMS - Enhanced Input Fields with Gradient Accents */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input {
        border-radius: 25px !important;
        border: 2px solid transparent !important;
        padding: 16px 20px !important;
        font-size: 15px !important;
        font-weight: 400 !important;
        transition: all 0.3s ease !important;
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.25) 50%, rgba(226, 232, 240, 0.4) 100%) border-box !important;
        color: #1a202c !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05),
                    0 1px 3px rgba(0, 0, 0, 0.03),
                    0 4px 16px rgba(102, 126, 234, 0.05) !important;
    }

    .stTextArea > div > div > textarea {
        min-height: 120px !important;
        line-height: 1.6 !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }

    .stTextInput > div > div > input:hover,
    .stTextArea > div > div > textarea:hover,
    .stSelectbox > div > div > select:hover,
    .stNumberInput > div > div > input:hover {
        background: linear-gradient(#fafafa, #fafafa) padding-box,
                    linear-gradient(135deg, rgba(102, 126, 234, 0.5) 0%, rgba(118, 75, 162, 0.4) 50%, rgba(102, 126, 234, 0.5) 100%) border-box !important;
        box-shadow: 0 3px 12px rgba(0, 0, 0, 0.06),
                    0 2px 4px rgba(0, 0, 0, 0.04),
                    0 6px 20px rgba(102, 126, 234, 0.1) !important;
        transform: translateY(-1px) !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus,
    .stNumberInput > div > div > input:focus {
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(135deg, rgba(102, 126, 234, 0.6) 0%, rgba(118, 75, 162, 0.5) 100%) border-box !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08),
                    0 4px 8px rgba(0, 0, 0, 0.08),
                    0 12px 40px rgba(102, 126, 234, 0.25) !important;
        outline: none !important;
        transform: translateY(-2px) !important;
    }

    /* Input placeholders */
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #94a3b8 !important;
        font-weight: 400 !important;
        font-style: italic !important;
    }

    /* Form Labels - Enhanced with gradient color */
    .stTextInput > label,
    .stTextArea > label,
    .stSelectbox > label,
    .stNumberInput > label {
        font-size: 15px !important;
        font-weight: 700 !important;
        color: #334155 !important;
        margin-bottom: 10px !important;
        letter-spacing: 0.3px !important;
    }

    /* Add subtle gradient to labels on hover */
    .stTextArea:hover > label,
    .stTextInput:hover > label {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    /* SLIDERS - SOLID PURPLE WITH WHITE OUTLINE */
    .stSlider {
        padding: 10px 0 !important;
    }

    /* Slider track - Solid purple without outline */
    .stSlider > div > div > div > div,
    div[data-testid="stSlider"] > div > div > div > div,
    .stSlider [data-baseweb="slider"] > div:first-child > div {
        background: #8b5cf6 !important;
        height: 10px !important;
        border-radius: 10px !important;
        border: none !important;
    }

    /* Slider thumb (handle) - Solid purple with white border */
    .stSlider > div > div > div > div > div,
    div[data-testid="stSlider"] > div > div > div > div > div,
    .stSlider [data-baseweb="slider"] [role="slider"],
    .stSlider div[role="slider"] {
        background: #8b5cf6 !important;
        border: 4px solid white !important;
        width: 20px !important;
        height: 20px !important;
        box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.1), 0 3px 10px rgba(139, 92, 246, 0.4) !important;
        border-radius: 50% !important;
        transition: all 0.2s ease !important;
    }

    .stSlider > div > div > div > div > div:hover,
    div[data-testid="stSlider"] [role="slider"]:hover {
        box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.1), 0 4px 15px rgba(139, 92, 246, 0.6) !important;
    }

    /* Override Streamlit's accent-color (this controls slider/checkbox colors) */
    input, select, textarea {
        accent-color: #8b5cf6 !important;
    }

    /* Force all range inputs to use solid purple */
    input[type="range"],
    input[type="checkbox"],
    input[type="radio"] {
        accent-color: #8b5cf6 !important;
    }

    input[type="range"]::-webkit-slider-thumb {
        background: #8b5cf6 !important;
        border: 4px solid white !important;
        width: 20px !important;
        height: 20px !important;
        border-radius: 50% !important;
        box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.1), 0 3px 10px rgba(139, 92, 246, 0.4) !important;
        cursor: pointer !important;
    }

    input[type="range"]::-webkit-slider-runnable-track {
        background: #8b5cf6 !important;
        height: 10px !important;
        border-radius: 10px !important;
        border: none !important;
    }

    input[type="range"]::-moz-range-thumb {
        background: #8b5cf6 !important;
        border: 4px solid white !important;
        width: 20px !important;
        height: 20px !important;
        border-radius: 50% !important;
        box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.1), 0 3px 10px rgba(139, 92, 246, 0.4) !important;
        cursor: pointer !important;
    }

    input[type="range"]::-moz-range-track {
        background: #8b5cf6 !important;
        height: 10px !important;
        border-radius: 10px !important;
        border: none !important;
    }
    
    /* Checkbox - Modern styled */
    input[type="checkbox"] {
        width: 22px !important;
        height: 22px !important;
        border-radius: 6px !important;
        border: 2px solid #cbd5e1 !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        appearance: none !important;
        -webkit-appearance: none !important;
        background: white !important;
    }

    input[type="checkbox"]:hover {
        border-color: #667eea !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2) !important;
    }

    input[type="checkbox"]:checked {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border-color: #667eea !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
    }

    /* Checkbox container label styling */
    .stCheckbox {
        padding: 8px 12px !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }

    .stCheckbox:hover {
        background: rgba(102, 126, 234, 0.05) !important;
    }

    .stCheckbox label {
        font-weight: 600 !important;
        color: #334155 !important;
        font-size: 15px !important;
    }

    /* Show slider value - simple number above handle */
    .stSlider [data-baseweb="slider"] [role="slider"] > div {
        background: none !important;
        background-color: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        color: #667eea !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        padding: 0 !important;
        margin: 0 !important;
        box-shadow: none !important;
        width: auto !important;
        height: auto !important;
    }

    /* Style min/max labels - keep visible */
    .stSlider [data-baseweb="slider"] [data-testid="stTickBarMin"],
    .stSlider [data-baseweb="slider"] [data-testid="stTickBarMax"] {
        font-weight: 600 !important;
        color: #64748b !important;
        font-size: 13px !important;
    }

    /* FIXED: Remove purple dot at end of slider */
    .stSlider > div > div > div::after,
    .stSlider > div > div > div > div::after,
    .stSlider [data-baseweb="slider"]::after {
        display: none !important;
    }

    /* Remove any extra elements at slider ends */
    .stSlider [data-baseweb="slider"] > div:last-child:not([role="slider"]) {
        display: none !important;
    }

    /* FIXED: Ensure only ONE circle on slider handle */
    .stSlider [role="slider"]::before,
    .stSlider [role="slider"]::after {
        display: none !important;
    }

    /* Hide any duplicate slider thumbs */
    .stSlider [data-baseweb="slider"] > div[aria-hidden="true"] {
        display: none !important;
    }
    /* Override any red colors in tabs */
    .stTabs [data-baseweb="tab"][aria-selected="true"],
    .stTabs [data-baseweb="tab"]:focus-visible,
    .stTabs [data-baseweb="tab"]:active {
        color: #667eea !important;
        border-color: #667eea !important;
    }
    /* Remove any red box-shadow or outline */
    .stTabs [data-baseweb="tab"]:focus {
        outline: 2px solid #667eea !important;
        outline-offset: 2px;
    }
    /* EXPANDER - Stylish (From Bearable) */
    .streamlit-expanderHeader {
        border-radius: 12px !important;
        background: rgba(255, 255, 255, 0.9) !important;
        backdrop-filter: blur(10px) !important;
        padding: 18px 24px !important;
        font-weight: 700 !important;
        font-size: 18px !important;
        border: 2px solid #e2e8f0 !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #667eea !important;
        background: rgba(102, 126, 234, 0.05) !important;
    }
    
    [data-testid="stExpander"] {
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        margin-bottom: 1rem;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    [data-testid="stExpander"]:hover {
        border-color: #667eea;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.15);
    }
    
    /* Tab Content Wrapper - White container box around each tab */
    .tab-content-wrapper {
        background: rgba(255, 255, 255, 0.98) !important;
        border-radius: 24px !important;
        padding: 2.5rem !important;
        margin: 1.5rem 0 !important;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08),
                    0 4px 12px rgba(0, 0, 0, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.9) !important;
    }

    /* Container styling - Apply glass card effect (removed to prevent unwanted white boxes) */
    /* [data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 20px !important;
        padding: 2rem !important;
        box-shadow: 0 8px 30px rgba(0,0,0,0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
    } */

    /* Remove white boxes from empty Streamlit containers */
    [data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"]:empty,
    [data-testid="element-container"]:empty {
        display: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Remove background and styling from plotly chart containers */
    [data-testid="stPlotlyChart"] {
        background: transparent !important;
    }
    
    /* Remove white background from containers holding plotly charts */
    div:has([data-testid="stPlotlyChart"]) {
        background: transparent !important;
        padding: 0 !important;
        border: none !important;
        box-shadow: none !important;
        border-radius: 0 !important;
    }
    
    /* Alternative selector for browsers that don't support :has() */
    [data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] > div:first-child:has([data-testid="stPlotlyChart"]) {
        background: transparent !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        font-size: 48px !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 16px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #64748b !important;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 18px !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# Add JavaScript to force slider colors (runs after CSS)
st.markdown("""
<script>
    // Ultra-aggressive function to change ALL red colors to purple in sliders
    function forcePurpleSliders() {
        const purpleColor = '#8b5cf6';
        const purpleRGB = 'rgb(139, 92, 246)';
        
        // Find all sliders
        const sliders = document.querySelectorAll('[data-baseweb="slider"], .stSlider, [data-testid="stSlider"]');
        
        sliders.forEach(slider => {
            // Get ALL elements inside slider
            const allInside = slider.querySelectorAll('*');
            
            allInside.forEach(el => {
                // Check computed style
                const computed = window.getComputedStyle(el);
                const bgColor = computed.backgroundColor;
                const bgImage = computed.backgroundImage;
                
                // Check if it's any shade of red
                const isRed = bgColor && (
                    bgColor.includes('rgb(255') || 
                    bgColor.includes('rgb(239') || 
                    bgColor.includes('rgb(244') ||
                    bgColor.includes('rgb(220') ||
                    bgColor.includes('rgb(211') ||
                    bgColor.includes('rgb(248') ||
                    bgColor.includes('rgb(254')
                );
                
                // Force change to purple if red
                if (isRed) {
                    el.style.setProperty('background-color', purpleColor, 'important');
                    el.style.setProperty('background', purpleColor, 'important');
                }
                
                // Check inline style attribute
                const inlineStyle = el.getAttribute('style');
                if (inlineStyle) {
                    // Check for red RGB values in inline style
                    const redPatterns = [
                        /rgb\(255,\s*\d+,\s*\d+\)/g,
                        /rgb\(239,\s*\d+,\s*\d+\)/g,
                        /rgb\(244,\s*\d+,\s*\d+\)/g,
                        /rgb\(220,\s*\d+,\s*\d+\)/g,
                        /#ff[0-9a-f]{4}/gi,
                        /#f[34][0-9a-f]{4}/gi
                    ];
                    
                    let newStyle = inlineStyle;
                    redPatterns.forEach(pattern => {
                        newStyle = newStyle.replace(pattern, purpleColor);
                    });

                    if (newStyle !== inlineStyle) {
                        el.setAttribute('style', newStyle);
                        el.style.setProperty('background-color', purpleColor, 'important');
                    }
                }
                
                // Check background-image for gradients with red
                if (bgImage && (bgImage.includes('rgb(255') || bgImage.includes('rgb(239') || bgImage.includes('rgb(244'))) {
                    el.style.setProperty('background-image', 'none', 'important');
                    el.style.setProperty('background-color', purpleColor, 'important');
                }
            });
        });
        
        // Also inject a global style rule for slider tracks (more targeted)
        if (!document.getElementById('slider-purple-override')) {
            const style = document.createElement('style');
            style.id = 'slider-purple-override';
            style.textContent = `
                /* Target only elements with red backgrounds inside sliders */
                [data-baseweb="slider"] div[style*="rgb(255"],
                [data-baseweb="slider"] div[style*="rgb(239"],
                [data-baseweb="slider"] div[style*="rgb(244"],
                [data-baseweb="slider"] div[style*="#ff"],
                [data-baseweb="slider"] div[style*="#f3"],
                [data-baseweb="slider"] div[style*="#f4"] {
                    background-color: ${purpleColor} !important;
                    background: ${purpleColor} !important;
                    background-image: none !important;
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    // Run immediately and repeatedly
    forcePurpleSliders();
    
    // Run on various events
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', forcePurpleSliders);
    }
    
    // Run after delays
    [100, 300, 500, 1000, 2000, 3000].forEach(delay => {
        setTimeout(forcePurpleSliders, delay);
    });
    
    // Continuous monitoring
    const observer = new MutationObserver(() => {
        forcePurpleSliders();
    });
    observer.observe(document.body, { 
        childList: true, 
        subtree: true,
        attributes: true,
        attributeFilter: ['style']
    });
    
    // Also run on any slider interaction
    document.addEventListener('mousedown', () => setTimeout(forcePurpleSliders, 10));
    document.addEventListener('mouseup', () => setTimeout(forcePurpleSliders, 10));
    document.addEventListener('input', () => setTimeout(forcePurpleSliders, 10));

    // Force tab container padding to persist with maximum priority
    function forceTabPadding() {
        const tabs = document.querySelectorAll('[data-testid="stTabs"]');
        tabs.forEach(tab => {
            // Use cssText for stronger enforcement
            const styleStr = 'padding: 2rem 3rem 3rem 3rem !important; margin: 2rem -3rem 3rem -3rem !important; width: calc(100% + 6rem) !important; max-width: calc(100% + 6rem) !important; background: rgba(255, 255, 255, 0.98) !important; background-color: rgba(255, 255, 255, 0.98) !important; backdrop-filter: blur(10px) !important; border-radius: 25px !important; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07), 0 10px 15px rgba(0, 0, 0, 0.1), 0 20px 25px rgba(0, 0, 0, 0.08) !important; border: 1px solid rgba(0, 0, 0, 0.05) !important; position: relative !important; box-sizing: border-box !important;';

            tab.style.cssText += styleStr;
            tab.setAttribute('style', tab.getAttribute('style') + '; ' + styleStr);
        });
    }

    // Run immediately
    forceTabPadding();

    // Watch for style attribute changes on tabs
    const tabObserver = new MutationObserver(() => {
        forceTabPadding();
    });

    // Observe tabs
    function observeTabs() {
        document.querySelectorAll('[data-testid="stTabs"]').forEach(tab => {
            tabObserver.observe(tab, {
                attributes: true,
                attributeFilter: ['style', 'class']
            });
        });
    }

    observeTabs();

    // Watch for new tabs being added
    const mainObserver = new MutationObserver(() => {
        forceTabPadding();
        observeTabs();
    });

    mainObserver.observe(document.body, {
        childList: true,
        subtree: true
    });

    // Aggressive continuous enforcement
    setInterval(forceTabPadding, 50);

    // On interactions
    document.addEventListener('click', () => setTimeout(forceTabPadding, 10));
    window.addEventListener('load', forceTabPadding);
</script>
""", unsafe_allow_html=True)

# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================

initialize_session_state()

# ============================================================================
# HEADER
# ============================================================================

# Header in a purple box with banner inside (Bearable style)
st.markdown("""
<div class="header-box">
    <div class="header-banner">✨ LIFE ASSESSMENT • GOAL SETTING • VISION BOARD • PERSONAL GROWTH</div>
    <h1 class="header-title">Meu Plano de 2026 📔</h1>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("### 📔 Plano de 2026")
    st.markdown("""
    **Transforme sua vida com clareza e intenção**
    
    📊 Avalie suas áreas de vida  
    🎯 Defina metas SMART  
    🌟 Crie seu Vision Board  
    📈 Acompanhe seu progresso  
    
    ---
    
    Organize suas intenções e transforme seus sonhos em realidade.
    """)
    
    st.markdown("---")
    st.markdown("### 📅 Hoje")
    st.markdown(f"**{datetime.now().strftime('%d de %B, %Y')}**")
    
    st.markdown("---")
    st.markdown("### 💾 Gerenciamento de Dados")
    
    if st.button("💾 Salvar Dados", use_container_width=True):
        if save_data():
            st.success("✅ Dados salvos com sucesso!")
        else:
            st.error("❌ Erro ao salvar dados")
    
    if st.button("🔄 Recarregar Dados", use_container_width=True):
        initialize_session_state()
        st.success("✅ Dados recarregados!")
        st.rerun()
    
    if os.path.exists(DATA_FILE):
        file_size = os.path.getsize(DATA_FILE) / 1024  # KB
        st.caption(f"📁 Arquivo: {DATA_FILE} ({file_size:.1f} KB)")
        mod_time = datetime.fromtimestamp(os.path.getmtime(DATA_FILE))
        st.caption(f"🕒 Última atualização: {mod_time.strftime('%d/%m/%Y %H:%M')}")

# ============================================================================
# HOW IT WORKS SECTION
# ============================================================================

st.markdown("""
<div style="margin: 1.5rem 0 1rem 0;">
    <h3 style="color: #1a202c; margin: 0; font-size: 1.3rem; font-weight: 700;">
        Como Funciona
    </h3>
</div>
""", unsafe_allow_html=True)

how_it_works_cols = st.columns(5)

steps = [
    {
        "number": "1",
        "title": "Avalie sua Vida",
        "description": "Comece com a Roda da Vida para avaliar suas 10 áreas de vida. Reflita sobre onde você está agora em 2025.",
        "color": "#667eea"
    },
    {
        "number": "2",
        "title": "Defina Metas SMART",
        "description": "Crie metas específicas, mensuráveis e alcançáveis para as áreas que precisam de atenção. Baseie-se nos insights da sua Roda da Vida.",
        "color": "#667eea"
    },
    {
        "number": "3",
        "title": "Visualize seus Sonhos",
        "description": "Monte seu Vision Board 2026 com intenções e imagens que representam seus desejos para o novo ano.",
        "color": "#667eea"
    },
    {
        "number": "4",
        "title": "Acompanhe o Progresso",
        "description": "Registre sua evolução ao longo do tempo. Marque metas completadas e observe seu crescimento.",
        "color": "#667eea"
    },
    {
        "number": "5",
        "title": "Analise no Dashboard",
        "description": "Visualize todas as suas conquistas e áreas de melhoria em um só lugar. Tome decisões baseadas em dados.",
        "color": "#667eea"
    }
]

for idx, step in enumerate(steps):
    with how_it_works_cols[idx]:
        st.markdown(f"""
        <div class="how-it-works-card" style="background: white;
                    padding: 2rem 1.5rem;
                    border-radius: 16px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                    text-align: center;
                    height: 340px;
                    display: flex;
                    flex-direction: column;
                    justify-content: flex-start;
                    border: 1px solid #e2e8f0;">
            <div style="background: {step['color']};
                        width: 60px;
                        height: 60px;
                        border-radius: 12px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin: 0 auto 1.5rem auto;">
                <span style="color: white;
                             font-size: 2rem;
                             font-weight: 800;
                             font-family: 'Inter', sans-serif;">
                    {step['number']}
                </span>
            </div>
            <h3 style="color: #1a202c;
                       margin: 0 0 1rem 0;
                       font-size: 1.1rem;
                       font-weight: 700;
                       font-family: 'Inter', sans-serif;
                       text-align: center !important;
                       width: 100%;
                       display: block;
                       padding: 0 0.5rem;">
                {step['title']}
            </h3>
            <p style="color: #64748b;
                      margin: 0;
                      font-size: 0.9rem;
                      line-height: 1.6;
                      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                      text-align: center !important;
                      width: 100%;
                      display: block;
                      padding: 0 0.5rem;">
                {step['description']}
            </p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("")

# ============================================================================
# MAIN TABS
# ============================================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Roda da Vida 2025",
    "📋 SMART Goals 2026",
    "🌟 Vision Board 2026",
    "📊 Dashboard",
    "📈 Progresso"
])

# ============================================================================
# TAB 1: SUA RODA DA VIDA 2025
# ============================================================================

with tab1:
    # Check if all scores are zero and reload data if needed
    if all(score == 0 for score in st.session_state.roda_scores.values()):
        data = load_data()
        if data and data.get("roda_scores"):
            # Check if saved data has non-zero scores
            if any(score != 0 for score in data["roda_scores"].values()):
                st.session_state.roda_scores = data["roda_scores"].copy()
                st.rerun()
    
    st.markdown("""
    <div class="section-header">
        <h2 style="color: white; margin: 0; font-size: 2rem; font-weight: 800; letter-spacing: -0.5px;">
            🎯 Roda da Vida 2025
        </h2>
        <p style="color: rgba(255,255,255,0.95); margin: 0.5rem 0 0 0; font-size: 1rem;">
            Avalie cada área da sua vida de 0-10
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Roda da Vida Chart with emojis (full width)
        
    area_emojis = {
        "Saúde": "😊",
        "Carreira": "👩🏻‍💻",
        "Finanças": "💸",
        "Relacionamentos": "❤️",
        "Família": "🤗",
        "Espiritualidade": "🧘🏼‍♀️",
        "Diversão": "🎉",
        "Crescimento Pessoal": "🌱",
        "Ambiente Físico": "🏡",
        "Criatividade": "🎨"
    }

    categories = list(st.session_state.roda_scores.keys())
    values = list(st.session_state.roda_scores.values())

    # Add emojis to category labels
    categories_with_emojis = []
    for category in categories:
        area_name = category
        emoji = area_emojis.get(area_name, "")
        display_label = f"{emoji} {category}" if emoji else category
        categories_with_emojis.append(display_label)

    fig = create_radar_chart(values, categories_with_emojis)
    st.plotly_chart(fig, use_container_width=True, config={
        'displayModeBar': False,
        'staticPlot': False
    })

    st.markdown('</div>', unsafe_allow_html=True)

    # Color legend below chart
    st.markdown("""
    <div style="background: rgba(102, 126, 234, 0.05); padding: 1rem 1.5rem; border-radius: 12px; margin: 1.5rem 0;">
        <p style="margin: 0; color: #334155; font-size: 0.95rem; line-height: 1.8;">
            <strong>0-3:</strong> Precisa atenção urgente  •
            <strong>4-6:</strong> Área em desenvolvimento  •
            <strong>7-8:</strong> Indo bem  •
            <strong>9-10:</strong> Excelente!
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Metrics row below chart
    col_metric1, col_metric2, col_metric3 = st.columns([1, 1.5, 1.5])
    
    # Helper function to get color based on score
    def get_score_color(score):
        if score >= 8:
            return "#10b981"  # Green
        elif score >= 7:
            return "#3b82f6"  # Blue
        elif score >= 5:
            return "#f59e0b"  # Orange
        else:
            return "#ef4444"  # Red
    
    # Helper function to get heart emoji based on score
    def get_heart_emoji(score):
        if score >= 8:
            return "💚"  # Green heart
        elif score >= 7:
            return "💙"  # Blue heart
        elif score >= 5:
            return "🧡"  # Orange heart
        else:
            return "❤️"  # Red heart
    
    with col_metric1:
        avg_score = sum(values) / len(values)
        avg_color = get_score_color(avg_score)
        heart = get_heart_emoji(avg_score)
        st.markdown(f"""
        <div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #e5e7eb;">
            <div style="color: #64748b; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.5rem;">PONTUAÇÃO MÉDIA</div>
            <div style="color: {avg_color}; font-size: 2rem; font-weight: 700;">{heart} {avg_score:.1f}/10</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_metric2:
        max_area = max(st.session_state.roda_scores.items(), key=lambda x: x[1])
        if max_area[1] > 0:  # Only show if score is greater than 0
            max_area_name = max_area[0]
            max_area_emoji = area_emojis.get(max_area_name, "")
            if max_area_name == "Crescimento Pessoal":
                max_area_name = "Crescimento"
            max_color = get_score_color(max_area[1])
            st.markdown(f"""
            <div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #e5e7eb;">
                <div style="color: #64748b; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.5rem;">ÁREA MAIS FORTE</div>
                <div style="color: {max_color}; font-size: 2rem; font-weight: 700;">{max_area_emoji} {max_area_name}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #e5e7eb;">
                <div style="color: #64748b; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.5rem;">ÁREA MAIS FORTE</div>
                <div style="color: #94a3b8; font-size: 1rem; font-weight: 500; padding: 1rem 0;">Complete a avaliação abaixo</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col_metric3:
        min_area = min(st.session_state.roda_scores.items(), key=lambda x: x[1])
        if max(st.session_state.roda_scores.values()) > 0:  # Only show if any scores exist
            min_area_name = min_area[0]
            min_area_emoji = area_emojis.get(min_area_name, "")
            if min_area_name == "Crescimento Pessoal":
                min_area_name = "Crescimento"
            min_color = get_score_color(min_area[1])
            st.markdown(f"""
            <div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #e5e7eb;">
                <div style="color: #64748b; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.5rem;">ÁREA PARA CRESCER</div>
                <div style="color: {min_color}; font-size: 2rem; font-weight: 700;">{min_area_emoji} {min_area_name}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #e5e7eb;">
                <div style="color: #64748b; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.5rem;">ÁREA PARA CRESCER</div>
                <div style="color: #94a3b8; font-size: 1rem; font-weight: 500; padding: 1rem 0;">Complete a avaliação abaixo</div>
            </div>
            """, unsafe_allow_html=True)

    # Progress indicator
    if avg_score < 5:
        st.warning("💡 Há espaço para crescimento em várias áreas!")
    elif avg_score < 7:
        st.info("✨ Você está no caminho certo!")
    else:
        st.success("🌟 Excelente! Você está prosperando!")
    
    st.markdown("---")

    # Assessment method selector
    st.markdown("""
    <div class="section-header" style="margin: 0 0 1.5rem 0;">
        <h3 style="color: white; margin: 0; font-size: 1.4rem; font-weight: 700;">
            📊 Como você quer avaliar?
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    assessment_method = st.radio(
        "Escolha seu método de avaliação:",
        ["🎯 Quiz Guiado (Recomendado)", "🎚️ Avaliação Manual"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    if assessment_method == "🎯 Quiz Guiado (Recomendado)":
        st.markdown("""
        <div style="background: rgba(102, 126, 234, 0.1); padding: 1rem 1.5rem; border-radius: 12px; border-left: 4px solid #667eea; margin-bottom: 1.5rem;">
            <p style="margin: 0; color: #1a202c; font-size: 0.95rem;">
                💡 <strong>Responda perguntas simples</strong> para cada área e receba sua pontuação automaticamente!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quiz questions for each area
        quiz_questions = {
            "Saúde": [
                "Você se sente energizado(a) e disposto(a) na maior parte do dia?",
                "Você pratica exercícios físicos regularmente?",
                "Você dorme bem e acorda descansado(a)?",
                "Sua alimentação é balanceada e saudável?",
                "Você cuida da sua saúde mental e emocional?"
            ],
            "Carreira": [
                "Você está satisfeito(a) com seu trabalho atual?",
                "Você sente que está crescendo profissionalmente?",
                "Seu trabalho tem propósito e significado para você?",
                "Você se sente valorizado(a) e reconhecido(a)?",
                "Há equilíbrio entre desafios e suas habilidades?"
            ],
            "Finanças": [
                "Você está satisfeito(a) com sua situação financeira atual?",
                "Você consegue poupar dinheiro regularmente?",
                "Você tem controle sobre seus gastos?",
                "Você se sente seguro(a) financeiramente?",
                "Você tem objetivos financeiros claros e está progredindo?"
            ],
            "Relacionamentos": [
                "Você tem relacionamentos (amigos, parceiro(a), etc.) saudáveis e satisfatórios?",
                "Você se sente amado(a) e apoiado(a) pelas pessoas importantes na sua vida?",
                "Há comunicação aberta e honesta nos seus relacionamentos?",
                "Você resolve conflitos de forma construtiva?",
                "Seus relacionamentos trazem alegria e crescimento?"
            ],
            "Família": [
                "Você passa tempo de qualidade com sua família?",
                "Há harmonia e apoio mútuo na sua família?",
                "Você se sente conectado(a) com seus familiares?",
                "Os relacionamentos familiares são saudáveis?",
                "Você consegue equilibrar família e outras áreas da vida?"
            ],
            "Espiritualidade": [
                "Você dedica tempo para reflexão e autoconhecimento?",
                "Você se sente conectado(a) com a natureza ou o universo?",
                "Você tem valores e princípios que guiam suas decisões?",
                "Você encontra momentos de paz e silêncio interior?",
                "Você sente que sua vida tem propósito e significado?"
            ],
            "Diversão": [
                "Você se diverte e se permite relaxar regularmente?",
                "Você tem hobbies que trazem alegria?",
                "Você equilibra trabalho e lazer?",
                "Você se permite momentos de prazer sem culpa?",
                "Você tem experiências divertidas e memoráveis?"
            ],
            "Crescimento Pessoal": [
                "Você está aprendendo coisas novas regularmente?",
                "Você sai da sua zona de conforto com frequência?",
                "Você está se tornando a melhor versão de si mesmo(a)?",
                "Você tem objetivos de desenvolvimento pessoal claros?",
                "Você se sente em evolução constante?"
            ],
            "Ambiente Físico": [
                "Você está satisfeito(a) com seu espaço de moradia?",
                "Seu ambiente é organizado e funcional?",
                "Você se sente confortável e seguro(a) no seu espaço?",
                "Seu ambiente reflete quem você é?",
                "Você cuida e mantém seu espaço com carinho?"
            ],
            "Criatividade": [
                "Você expressa sua criatividade regularmente?",
                "Você tem projetos criativos que te entusiasmam?",
                "Você se permite experimentar e inovar?",
                "Sua criatividade tem espaço na sua rotina?",
                "Você se sente realizado(a) criativamente?"
            ]
        }
        
        # Create quiz interface
        areas_list = list(st.session_state.roda_scores.keys())
        
        # Use expanders for each area
        for area in areas_list:
            area_name = area
            emoji = area_emojis.get(area_name, "")
            
            with st.expander(f"{emoji} {area}", expanded=False):
                questions = quiz_questions.get(area, [])
                
                if questions:
                    st.markdown(f"**Responda as perguntas abaixo:**")
                    st.markdown("*Sempre = 2 pts | Frequentemente = 1.5 pts | Às vezes = 1 pt | Raramente = 0.5 pts | Nunca = 0 pts*")
                    
                    total_score = 0
                    all_answered = True
                    
                    for i, question in enumerate(questions):
                        response = st.radio(
                            question,
                            ["Nunca", "Raramente", "Às vezes", "Frequentemente", "Sempre"],
                            horizontal=True,
                            key=f"quiz_{area}_{i}",
                            index=None  # No default selection
                        )
                        
                        if response is None:
                            all_answered = False
                        elif response == "Sempre":
                            total_score += 2
                        elif response == "Frequentemente":
                            total_score += 1.5
                        elif response == "Às vezes":
                            total_score += 1
                        elif response == "Raramente":
                            total_score += 0.5
                    
                    # Convert to 0-10 scale (5 questions x 2 points = 10 max)
                    final_score = total_score
                    
                    # Only update session state if user has answered all questions
                    if all_answered:
                        st.session_state.roda_scores[area] = final_score
                    
                    # Show score only if all questions answered
                    if all_answered:
                        # Show score
                        if final_score >= 8:
                            color = "#10b981"
                            message = "Excelente! 🌟"
                        elif final_score >= 6:
                            color = "#3b82f6"
                            message = "Muito bom! 💙"
                        elif final_score >= 4:
                            color = "#f59e0b"
                            message = "Precisa atenção 🧡"
                        else:
                            color = "#ef4444"
                            message = "Priorize esta área ❤️"
                        
                        st.markdown(f"""
                        <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid {color}; margin-top: 1rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="color: #64748b; font-weight: 600;">Pontuação desta área:</span>
                                <span style="color: {color}; font-size: 1.5rem; font-weight: 800;">{final_score}/10</span>
                            </div>
                            <div style="color: {color}; font-weight: 600; margin-top: 0.5rem; text-align: center;">
                                {message}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        
        # Save button for quiz
        st.markdown("---")
        col_quiz_btn1, col_quiz_btn2, col_quiz_btn3 = st.columns([1, 2, 1])
        with col_quiz_btn2:
            if st.button("💾 Salvar Avaliação do Quiz", use_container_width=True, type="primary"):
                if save_data():
                    st.success("✅ Avaliação salva! Role para cima para ver seu gráfico atualizado.")
                    st.rerun()
    
    else:  # Manual assessment
        st.markdown("""
        <div class="section-header" style="margin: 1.5rem 0 1.5rem 0;">
            <h3 style="color: white; margin: 0; font-size: 1.4rem; font-weight: 700;">
                🎚️ Ajuste manualmente cada área
            </h3>
        </div>
        """, unsafe_allow_html=True)

    # Sliders below in two columns (only show if manual mode)
    # Sliders below in two columns (only show if manual mode)
    if assessment_method == "🎚️ Avaliação Manual":
        st.markdown("""
        <div style="background: rgba(102, 126, 234, 0.1); padding: 1rem 1.5rem; border-radius: 12px; border-left: 4px solid #667eea; margin-bottom: 1.5rem;">
            <p style="margin: 0; color: #1a202c; font-size: 0.95rem;">
                💡 <strong>Use os sliders</strong> para avaliar cada área de 0-10 baseado na sua intuição.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)

        # Split areas into two columns
        areas_list = list(st.session_state.roda_scores.keys())
        mid_point = len(areas_list) // 2

        with col1:
            for area in areas_list[:mid_point]:
                # Get area name and emoji
                area_name = area
                emoji = area_emojis.get(area_name, "")
                display_label = f"{emoji} {area}" if emoji else area

                st.session_state.roda_scores[area] = st.slider(
                    display_label,
                    min_value=0.0,
                    max_value=10.0,
                    value=float(st.session_state.roda_scores[area]),
                    step=0.5,
                    key=f"slider_{area}"
                )

        with col2:
            for area in areas_list[mid_point:]:
                # Get area name and emoji
                area_name = area
                emoji = area_emojis.get(area_name, "")
                display_label = f"{emoji} {area}" if emoji else area

                st.session_state.roda_scores[area] = st.slider(
                    display_label,
                    min_value=0.0,
                    max_value=10.0,
                    value=float(st.session_state.roda_scores[area]),
                    step=0.5,
                    key=f"slider_{area}"
                )
        
        # Save button centered
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("💾 Salvar Avaliação", use_container_width=True, type="primary"):
                if save_data():
                    st.success("✅ Avaliação salva!")
                    st.rerun()

    # Reflection questions
    st.markdown("---")
    st.markdown("""
    <div class="section-header">
        <h3 style="color: white; margin: 0; font-size: 1.3rem; font-weight: 700;">
            💭 Reflexões 2025
        </h3>
    </div>
    """, unsafe_allow_html=True)

    reflection_col1, reflection_col2 = st.columns(2)
    
    with reflection_col1:
        st.text_area(
            "🌟 Quais foram suas maiores conquistas em 2025?",
            value=st.session_state.get("conquistas_2025", ""),
            height=150,
            key="conquistas_2025"
        )
        st.text_area(
            "💪 Que desafios você superou?",
            value=st.session_state.get("desafios_2025", ""),
            height=150,
            key="desafios_2025"
        )
    
    with reflection_col2:
        st.text_area(
            "📚 O que você aprendeu sobre si mesma?",
            value=st.session_state.get("aprendizados_2025", ""),
            height=150,
            key="aprendizados_2025"
        )
        st.text_area(
            "🙏 Pelo que você é grata em 2025?",
            value=st.session_state.get("gratidao_2025", ""),
            height=150,
            key="gratidao_2025"
        )
    
    # Save reflections button
    col_ref_btn1, col_ref_btn2, col_ref_btn3 = st.columns([1, 2, 1])
    with col_ref_btn2:
        if st.button("💾 Salvar Reflexões", use_container_width=True, type="primary", key="save_reflections"):
            if save_data():
                st.success("✅ Reflexões salvas com sucesso!")

# ============================================================================
# TAB 2: SMART GOALS 2026
# ============================================================================

with tab3:
    st.markdown("""
    <div class="section-header">
        <h2 style="color: white; margin: 0; font-size: 2rem; font-weight: 800; letter-spacing: -0.5px;">
            🌟 Vision Board 2026
        </h2>
        <p style="color: rgba(255,255,255,0.95); margin: 0.5rem 0 0 0; font-size: 1rem;">
            Visualize e manifeste seus sonhos para o próximo ano
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    vision_areas = {
        "💼 Carreira & Projetos": {
            "keywords": ["Crescimento Profissional", "Novos Projetos", "Realizações", "Propósito"],
            "affirmation": "Eu crio valor e impacto através do meu trabalho e paixão."
        },
        "🌿 Saúde & Bem-Estar": {
            "keywords": ["Pain Management", "Holistic Healing", "Gentle Movement", "Self-Care"],
            "affirmation": "Eu honro a sabedoria do meu corpo e confio no processo de cura."
        },
        "🔮 Espiritualidade": {
            "keywords": ["Rituais", "Moon Work", "Intuição", "Astrologia"],
            "affirmation": "Eu confio na minha intuição e na magia que flui através de mim."
        },
        "🦋 Crescimento Pessoal": {
            "keywords": ["Saturn Return", "Autenticidade", "Boundaries", "Self-Discovery"],
            "affirmation": "Eu abraço minha transformação e entro no meu poder autêntico."
        },
        "💕 Amor Próprio": {
            "keywords": ["Autocuidado", "Self-Love", "Clareza", "Autoconhecimento"],
            "affirmation": "Eu me amo e me aceito completamente."
        },
        "✈️ Viagens & Aventuras": {
            "keywords": ["Novos Lugares", "Experiências", "Cultura", "Descobertas"],
            "affirmation": "Eu abraço a beleza e magia de explorar o mundo."
        },
        "💰 Abundância": {
            "keywords": ["Crescimento Financeiro", "Prosperidade", "Investimentos", "Estabilidade"],
            "affirmation": "Dinheiro flui para mim facilmente enquanto crio valor para outros."
        },
        "🎨 Criatividade": {
            "keywords": ["AI Learning", "Tech Skills", "Innovation", "Problem-Solving"],
            "affirmation": "Eu confio no meu gênio criativo e capacidade de aprender qualquer coisa."
        }
    }
    
    # Pinterest Integration Section
    if PINTEREST_AVAILABLE:
        st.markdown("---")
        st.markdown("""
        <div class="glass-card" style="background: linear-gradient(135deg, rgba(203, 32, 39, 0.05) 0%, rgba(189, 8, 28, 0.05) 100%); border: 2px solid rgba(203, 32, 39, 0.2);">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <h3 style="color: #1a202c; margin: 0 0 10px 0; font-size: 1.3rem; font-weight: 700; display: flex; align-items: center; gap: 0.5rem;">
                        📌 Integração Pinterest
                    </h3>
                    <p style="color: #64748b; margin: 0; font-size: 0.95rem;">
                        Conecte seus boards do Pinterest para importar imagens diretamente para seu Vision Board
                    </p>
                </div>
                <div style="margin-left: 1rem;">
                    <a href="https://github.com/your-repo/blob/main/PINTEREST_SETUP.md" target="_blank" style="color: #667eea; text-decoration: none; font-size: 0.85rem; font-weight: 600;">
                        📖 Guia de Setup →
                    </a>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        pinterest_tab1, pinterest_tab2 = st.tabs(["🔗 Importar por URL", "🔐 Conectar com API"])
        
        with pinterest_tab1:
            st.markdown("""
            <div style="background: rgba(102, 126, 234, 0.05); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                <p style="margin: 0; color: #334155; font-size: 0.9rem;">
                    💡 <strong>Cole URLs</strong> de pins ou boards do Pinterest. Você pode colar múltiplas URLs, uma por linha.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            pinterest_urls = st.text_area(
                "URLs do Pinterest (uma por linha):",
                height=100,
                placeholder="https://www.pinterest.com/username/board-name/\nhttps://www.pinterest.com/pin/123456789/",
                key="pinterest_urls"
            )
            
            col_url1, col_url2 = st.columns([2, 1])
            with col_url1:
                import_from_urls = st.button("📥 Importar Imagens das URLs", type="primary", use_container_width=True)
            
            with col_url2:
                max_images = st.number_input("Máx. imagens", min_value=1, max_value=50, value=10, key="max_pinterest_images")
            
            if import_from_urls and pinterest_urls:
                with st.spinner("🔄 Processando URLs do Pinterest..."):
                    urls_list = [url.strip() for url in pinterest_urls.split('\n') if url.strip()]
                    imported_count = 0
                    
                    for url in urls_list:
                        if 'pinterest.com' in url or 'pinterest.' in url:
                            try:
                                parsed_info = extract_pinterest_url_info(url)
                                st.info(f"📌 Processando: {url}")
                                
                                if parsed_info["type"] == "pin":
                                    st.info("💡 Para importar imagens de pins individuais, use a opção 'Conectar com API' ou baixe a imagem manualmente.")
                                elif parsed_info["type"] == "board":
                                    st.info("💡 Para importar boards completos, conecte com a API do Pinterest usando a aba 'Conectar com API'.")
                                
                                # Try to extract image URL from Pinterest page (simplified approach)
                                # Note: Pinterest requires proper authentication for API access
                                st.warning("⚠️ Importação direta de imagens requer autenticação. Use a aba 'Conectar com API' para acesso completo.")
                                
                            except Exception as e:
                                st.error(f"Erro ao processar URL {url}: {e}")
                    
                    if imported_count > 0:
                        st.success(f"✅ {imported_count} imagem(ns) importada(s) com sucesso!")
                        st.rerun()
        
        with pinterest_tab2:
            st.markdown("""
            <div style="background: rgba(102, 126, 234, 0.05); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                <p style="margin: 0; color: #334155; font-size: 0.9rem;">
                    🔐 Para acessar seus boards privados e pins, você precisa autenticar com a API do Pinterest.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Check if credentials are set
            try:
                pinterest_app_id = st.secrets.get("pinterest", {}).get("app_id", "")
                pinterest_app_secret = st.secrets.get("pinterest", {}).get("app_secret", "")
            except Exception:
                pinterest_app_id = ""
                pinterest_app_secret = ""
            
            if not pinterest_app_id or not pinterest_app_secret:
                st.markdown("""
                <div style="background: rgba(245, 158, 11, 0.1); padding: 1rem; border-radius: 8px; border-left: 4px solid #f59e0b;">
                    <p style="margin: 0; color: #92400e; font-size: 0.9rem;">
                        ⚙️ <strong>Configuração necessária:</strong> Para usar a integração com API, configure suas credenciais do Pinterest.
                    </p>
                    <p style="margin: 0.5rem 0 0 0; color: #92400e; font-size: 0.85rem;">
                        1. Crie um app em <a href="https://developers.pinterest.com/apps/" target="_blank">developers.pinterest.com</a><br>
                        2. Adicione as credenciais em <code>.streamlit/secrets.toml</code>:
                    </p>
                    <pre style="background: #1a202c; color: #10b981; padding: 0.75rem; border-radius: 4px; margin-top: 0.5rem; font-size: 0.8rem;">
[pinterest]
app_id = "seu_app_id"
app_secret = "seu_app_secret"
                    </pre>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Initialize session state for Pinterest
                if 'pinterest_access_token' not in st.session_state:
                    st.session_state.pinterest_access_token = None
                
                if st.session_state.pinterest_access_token:
                    st.success("✅ Conectado ao Pinterest!")
                    
                    # Fetch user boards
                    api = PinterestAPI(st.session_state.pinterest_access_token)
                    
                    if st.button("🔄 Atualizar Lista de Boards"):
                        st.rerun()
                    
                    boards = api.get_user_boards(limit=50)
                    
                    if boards:
                        st.markdown(f"**Seus Boards ({len(boards)}):**")
                        
                        selected_board_id = st.selectbox(
                            "Selecione um board para importar:",
                            options=[b['id'] for b in boards],
                            format_func=lambda x: next((b['name'] for b in boards if b['id'] == x), x),
                            key="selected_pinterest_board"
                        )
                        
                        if selected_board_id:
                            if st.button("📥 Importar Pins do Board", type="primary"):
                                with st.spinner("🔄 Buscando pins..."):
                                    pins = api.get_board_pins(selected_board_id, limit=max_images)
                                    
                                    if pins:
                                        st.success(f"✅ {len(pins)} pin(s) encontrado(s)!")
                                        
                                        # Map pins to vision areas
                                        mapping = map_pins_to_vision_areas(pins, vision_areas, st.session_state.smart_goals)
                                        
                                        # Show mapping preview
                                        st.markdown("**Preview do Mapeamento:**")
                                        for area, area_pins in mapping.items():
                                            if area_pins:
                                                st.markdown(f"**{area}:** {len(area_pins)} pin(s)")
                                        
                                        if st.button("✨ Adicionar ao Vision Board", type="primary"):
                                            added_count = 0
                                            for area, area_pins in mapping.items():
                                                for pin in area_pins:
                                                    # Get pin image URL
                                                    if 'media' in pin and 'images' in pin['media']:
                                                        image_url = pin['media']['images'].get('originals', {}).get('url')
                                                        if image_url:
                                                            try:
                                                                img = download_image_from_url(image_url)
                                                                if img:
                                                                    # Convert PIL Image to bytes for storage
                                                                    buf = io.BytesIO()
                                                                    img.save(buf, format='PNG')
                                                                    buf.seek(0)
                                                                    st.session_state.vision_images[area].append(buf)
                                                                    added_count += 1
                                                            except Exception as e:
                                                                st.warning(f"Não foi possível baixar imagem do pin {pin.get('id', 'unknown')}: {e}")
                                            
                                            if added_count > 0:
                                                st.success(f"✅ {added_count} imagem(ns) adicionada(s) ao Vision Board!")
                                                save_data()
                                                st.rerun()
                                    else:
                                        st.info("Este board não possui pins.")
                    else:
                        st.info("Nenhum board encontrado. Crie boards no Pinterest primeiro.")
                    
                    if st.button("🔌 Desconectar do Pinterest"):
                        st.session_state.pinterest_access_token = None
                        st.rerun()
                else:
                    # OAuth flow
                    st.markdown("**Autenticação OAuth:**")
                    
                    # For OAuth, we need a redirect URI
                    # In Streamlit Cloud, this would be your app URL + /callback
                    redirect_uri = st.text_input(
                        "Redirect URI (URL de callback):",
                        value="http://localhost:8501" if "localhost" in st.get_option("server.headless") else "",
                        help="Configure esta URL nas configurações do seu app Pinterest",
                        key="pinterest_redirect_uri"
                    )
                    
                    if redirect_uri:
                        oauth_url = get_pinterest_oauth_url(pinterest_app_id, redirect_uri)
                        
                        st.markdown(f"""
                        <div style="background: white; padding: 1rem; border-radius: 8px; border: 2px solid #e2e8f0;">
                            <p style="margin: 0 0 0.75rem 0; color: #334155; font-size: 0.9rem; font-weight: 600;">
                                1. Clique no link abaixo para autorizar
                            </p>
                            <a href="{oauth_url}" target="_blank" style="color: #667eea; font-weight: 700; text-decoration: none;">
                                🔐 Autorizar no Pinterest →
                            </a>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Handle OAuth callback
                        auth_code = st.text_input(
                            "Cole o código de autorização recebido:",
                            key="pinterest_auth_code"
                        )
                        
                        if auth_code and st.button("🔐 Conectar"):
                            with st.spinner("Autenticando..."):
                                access_token = exchange_code_for_token(
                                    pinterest_app_id,
                                    pinterest_app_secret,
                                    auth_code,
                                    redirect_uri
                                )
                                
                                if access_token:
                                    st.session_state.pinterest_access_token = access_token
                                    st.success("✅ Conectado com sucesso!")
                                    st.rerun()
                                else:
                                    st.error("❌ Falha na autenticação. Verifique suas credenciais.")
        
        st.markdown("---")
    
    # View mode selector
    view_mode = st.radio(
        "🔍 Modo de Visualização",
        ["📝 Texto & Intenções", "🖼️ Collage Digital", "📋 Ver Tudo"],
        horizontal=True
    )
    
    if view_mode == "🖼️ Collage Digital" or view_mode == "📋 Ver Tudo":
        st.markdown("""
        <div class="glass-card" style="margin-top: 1.5rem;">
            <h3 style="color: #1a202c; margin: 0 0 15px 0; font-size: 1.3rem; font-weight: 700;">
                🎨 Collage Visual 2026
            </h3>
        """, unsafe_allow_html=True)
        
        # Display all images in a grid
        all_images = []
        for area, images in st.session_state.vision_images.items():
            all_images.extend(images)
        
        if all_images:
            # Create a masonry-style grid
            cols_collage = st.columns(4)
            for idx, img in enumerate(all_images):
                with cols_collage[idx % 4]:
                    st.image(img, use_container_width=True)
        else:
            st.info("📸 Adicione imagens nas áreas abaixo para criar seu collage!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    if view_mode == "📝 Texto & Intenções" or view_mode == "📋 Ver Tudo":
        cols = st.columns(2)
        
        for idx, (area, details) in enumerate(vision_areas.items()):
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="glass-card">
                    <h3 style="color: #1a202c; margin: 0 0 15px 0; font-size: 1.3rem; font-weight: 800;">{area}</h3>
                    <p style="color: #64748b; margin: 0 0 15px 0; font-size: 0.95rem; font-weight: 600;">
                        <strong>Keywords:</strong> {', '.join(details['keywords'])}
                    </p>
                    <div style="background: rgba(102, 126, 234, 0.1); padding: 15px; border-radius: 10px; border-left: 4px solid #667eea; margin-bottom: 15px;">
                        <p style="margin: 0; color: #334155; font-size: 0.95rem; font-style: italic;">
                            💭 {details['affirmation']}
                        </p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Image upload section
                with st.expander("📸 Adicionar Imagens", expanded=False):
                    uploaded_files = st.file_uploader(
                        f"Upload fotos para {area}",
                        type=['png', 'jpg', 'jpeg', 'gif'],
                        accept_multiple_files=True,
                        key=f"upload_{area}"
                    )
                    
                    if uploaded_files:
                        for uploaded_file in uploaded_files:
                            if uploaded_file not in st.session_state.vision_images[area]:
                                st.session_state.vision_images[area].append(uploaded_file)
                        st.success(f"✨ {len(uploaded_files)} imagem(ns) adicionada(s)!")
                    
                    # Display uploaded images for this area
                    if st.session_state.vision_images[area]:
                        st.markdown(f"**Imagens ({len(st.session_state.vision_images[area])}):**")
                        img_cols = st.columns(3)
                        for img_idx, img in enumerate(st.session_state.vision_images[area]):
                            with img_cols[img_idx % 3]:
                                st.image(img, use_container_width=True)
                                if st.button("🗑️", key=f"delete_img_{area}_{img_idx}"):
                                    st.session_state.vision_images[area].pop(img_idx)
                                    st.rerun()
                
                key = f"vision_{area}"
                current_value = st.session_state.get(key, "")
                st.text_area(
                    "Suas intenções para esta área:",
                    value=current_value,
                    height=100,
                    key=key
                )
                
                st.markdown("---")
    
    # Export Vision Board
    st.markdown("---")
    st.markdown("""
    <div class="glass-card">
        <h3 style="color: #1a202c; margin: 0 0 15px 0; font-size: 1.5rem; font-weight: 800;">
            💾 Exportar Vision Board
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Check if there are images to export
        total_images = sum(len(imgs) for imgs in st.session_state.vision_images.values())
        
        if total_images > 0:
            if st.button("🖼️ Gerar Collage", type="primary"):
                with st.spinner("Criando seu collage mágico..."):
                    collage = create_vision_collage(st.session_state.vision_images)
                    if collage:
                        # Convert to bytes
                        buf = io.BytesIO()
                        collage.save(buf, format='PNG')
                        byte_im = buf.getvalue()
                        
                        st.download_button(
                            label="📥 Download Collage PNG",
                            data=byte_im,
                            file_name=f"plano_de_2026_vision_board_{datetime.now().strftime('%Y%m%d')}.png",
                            mime="image/png"
                        )
                        
                        # Show preview
                        st.image(collage, caption="Seu Vision Board 2026 ✨", use_container_width=True)
        else:
            st.info("📸 Adicione imagens primeiro para gerar o collage!")
    
    with col2:
        # Count total images
        st.metric("Total de Imagens", total_images)
    
    with col3:
        if total_images > 0:
            if st.button("🗑️ Limpar Todas Imagens"):
                if st.checkbox("Tem certeza?", key="confirm_clear_images"):
                    for area in st.session_state.vision_images.keys():
                        st.session_state.vision_images[area] = []
                    st.success("✨ Imagens limpas!")
                    st.rerun()

# ============================================================================
# TAB 3: VISION BOARD 2026
# ============================================================================

with tab2:
    st.markdown("""
    <div class="section-header">
        <h2 style="color: white; margin: 0; font-size: 2rem; font-weight: 800; letter-spacing: -0.5px;">
            📋 SMART Goals 2026
        </h2>
        <p style="color: rgba(255,255,255,0.95); margin: 0.5rem 0 0 0; font-size: 1rem;">
            Crie metas específicas, mensuráveis e alcançáveis
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card" style="margin: 2rem 0; background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%); border: 2px solid rgba(102, 126, 234, 0.15);">
        <div style="text-align: center;">
            <h3 style="color: #667eea; margin: 0 0 1rem 0; font-size: 1.3rem; font-weight: 700;">Framework SMART</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-top: 1rem;">
                <div style="text-align: center; padding: 0.75rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎯</div>
                    <div style="color: #667eea; font-weight: 700; font-size: 1.1rem; margin-bottom: 0.25rem;">Specific</div>
                    <div style="color: #64748b; font-size: 0.85rem;">Seja claro e detalhado</div>
                </div>
                <div style="text-align: center; padding: 0.75rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                    <div style="color: #667eea; font-weight: 700; font-size: 1.1rem; margin-bottom: 0.25rem;">Measurable</div>
                    <div style="color: #64748b; font-size: 0.85rem;">Defina métricas</div>
                </div>
                <div style="text-align: center; padding: 0.75rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">✅</div>
                    <div style="color: #667eea; font-weight: 700; font-size: 1.1rem; margin-bottom: 0.25rem;">Achievable</div>
                    <div style="color: #64748b; font-size: 0.85rem;">Seja realista</div>
                </div>
                <div style="text-align: center; padding: 0.75rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">💫</div>
                    <div style="color: #667eea; font-weight: 700; font-size: 1.1rem; margin-bottom: 0.25rem;">Relevant</div>
                    <div style="color: #64748b; font-size: 0.85rem;">Alinhe com valores</div>
                </div>
                <div style="text-align: center; padding: 0.75rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">⏰</div>
                    <div style="color: #667eea; font-weight: 700; font-size: 1.1rem; margin-bottom: 0.25rem;">Time-bound</div>
                    <div style="color: #64748b; font-size: 0.85rem;">Defina prazos</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Show Roda da Vida insights or celebration
    if should_show_insights():
        render_roda_insights()
    else:
        render_celebration()

    st.markdown("---")

    # Add new goal
    # Check for prefill state from insights CTA buttons
    form_expanded = st.session_state.get('expand_goal_form', False)
    prefill_area = st.session_state.get('prefill_area', None)

    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2rem 2.5rem;
                border-radius: 20px;
                margin: 2.5rem 0;
                box-shadow: 0 8px 24px rgba(102, 126, 234, 0.25), 0 4px 12px rgba(0, 0, 0, 0.1);
                position: relative;
                overflow: hidden;">
        <div style="position: absolute; top: -50px; right: -50px; width: 200px; height: 200px; 
                    background: rgba(255, 255, 255, 0.1); border-radius: 50%; filter: blur(40px);"></div>
        <div style="position: relative; z-index: 1;">
            <h3 style="color: white; margin: 0 0 0.75rem 0; font-size: 1.8rem; font-weight: 800; 
                       display: flex; align-items: center; gap: 0.75rem;
                       text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                ✨ Criar Nova Meta SMART
            </h3>
            <p style="color: rgba(255, 255, 255, 0.95); margin: 0; font-size: 1.05rem; line-height: 1.6;">
                Defina uma meta clara, mensurável e alcançável para transformar 2026
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("➕ Preencha o formulário abaixo para criar sua meta", expanded=form_expanded):
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.05) 100%);
                    padding: 1rem 1.5rem;
                    border-radius: 12px;
                    margin-bottom: 1.5rem;
                    border-left: 4px solid #667eea;">
            <p style="margin: 0; color: #1a202c; font-size: 0.95rem; line-height: 1.6;">
                📝 <strong>Formulário de Criação de Meta SMART</strong> — Complete todos os campos abaixo para definir uma meta clara e alcançável
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("new_goal_form"):
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.03) 100%);
                        padding: 1.5rem;
                        border-radius: 12px;
                        margin-bottom: 1.5rem;
                        border: 2px solid rgba(102, 126, 234, 0.1);">
                <h4 style="color: #667eea; margin: 0 0 0.5rem 0; font-size: 1.1rem; font-weight: 700; display: flex; align-items: center; gap: 0.5rem;">
                    🎯 Configure sua Meta
                </h4>
                <p style="color: #64748b; margin: 0; font-size: 0.9rem;">Escolha a área da vida que deseja transformar</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Determine default area (prefilled or first in list)
            area_list = list(st.session_state.roda_scores.keys())
            if prefill_area and prefill_area in area_list:
                default_index = area_list.index(prefill_area)
            else:
                default_index = 0

            goal_area = st.selectbox(
                "📍 Área da Vida",
                area_list,
                index=default_index,
                help="Selecione a área da vida relacionada a esta meta"
            )
            
            st.markdown("""
            <div style="margin: 2rem 0 1.5rem 0;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            padding: 1rem 1.5rem;
                            border-radius: 12px;
                            margin-bottom: 1.5rem;">
                    <h4 style="color: white; margin: 0; font-size: 1.1rem; font-weight: 700; display: flex; align-items: center; gap: 0.5rem;">
                        📝 Critérios SMART
                    </h4>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            # Area-specific examples for SMART criteria
            area_examples = {
                "Saúde": {
                    "specific": "Correr 5km sem parar 3x por semana",
                    "measurable": "Treinar toda segunda, quarta e sexta + aumentar 500m a cada 2 semanas",
                    "achievable": "Tenho tênis de corrida, parque perto de casa e 40min disponíveis pela manhã",
                    "relevant": "Quero ter mais energia, melhorar minha saúde cardiovascular e me sentir mais disposto(a)",
                    "time_bound": "Até 30 de junho de 2026"
                },
                "Carreira": {
                    "specific": "Conseguir uma promoção para cargo de liderança na minha área",
                    "measurable": "Liderar 2 projetos estratégicos + completar curso de gestão de pessoas",
                    "achievable": "Tenho 5 anos de experiência, apoio do gestor e budget aprovado para curso",
                    "relevant": "Quero desenvolver habilidades de liderança e ter mais impacto na empresa",
                    "time_bound": "Até dezembro de 2026"
                },
                "Finanças": {
                    "specific": "Economizar R$ 20.000 para fundo de emergência",
                    "measurable": "Poupar R$ 2.000 por mês + rastrear gastos semanalmente",
                    "achievable": "Vou reduzir gastos supérfluos em 30% e usar método 50/30/20",
                    "relevant": "Quero ter segurança financeira e paz de espírito para imprevistos",
                    "time_bound": "Até outubro de 2026"
                },
                "Relacionamentos": {
                    "specific": "Fortalecer amizades com encontros mensais de qualidade",
                    "measurable": "Organizar 1 jantar/atividade por mês com amigos próximos",
                    "achievable": "Tenho tempo nos fins de semana e amigos disponíveis e interessados",
                    "relevant": "Quero me sentir mais conectado(a) e ter relacionamentos mais profundos",
                    "time_bound": "Manter durante todo 2026"
                },
                "Família": {
                    "specific": "Passar tempo de qualidade com família toda semana",
                    "measurable": "Jantar em família 2x por semana + 1 atividade especial mensal",
                    "achievable": "Vou bloquear terças e quintas na agenda + fins de semana alternados",
                    "relevant": "Quero fortalecer vínculos familiares e criar memórias afetivas",
                    "time_bound": "Compromisso para todo 2026"
                },
                "Espiritualidade": {
                    "specific": "Estabelecer prática diária de meditação e reflexão",
                    "measurable": "Meditar 15min todas as manhãs + journal 10min antes de dormir",
                    "achievable": "Tenho app de meditação, alarme configurado e caderno dedicado",
                    "relevant": "Quero mais paz interior, clareza mental e conexão com meu propósito",
                    "time_bound": "Hábito consolidado até março de 2026"
                },
                "Diversão": {
                    "specific": "Explorar 12 atividades/lugares novos este ano",
                    "measurable": "1 experiência nova por mês (restaurante, trilha, show, museu, etc.)",
                    "achievable": "Vou reservar 1 sábado por mês e pesquisar opções com antecedência",
                    "relevant": "Quero sair da rotina, me divertir mais e aproveitar a vida",
                    "time_bound": "12 experiências até dezembro de 2026"
                },
                "Crescimento Pessoal": {
                    "specific": "Ler 24 livros de desenvolvimento pessoal/profissional",
                    "measurable": "2 livros por mês + fazer resumo de cada um",
                    "achievable": "Vou ler 30min antes de dormir e nos fins de semana",
                    "relevant": "Quero expandir conhecimento, desenvolver novas habilidades e evoluir constantemente",
                    "time_bound": "Meta anual - revisão mensal"
                },
                "Ambiente Físico": {
                    "specific": "Reformar e organizar completamente meu quarto/escritório",
                    "measurable": "Pintar paredes + comprar móveis novos + sistema de organização implementado",
                    "achievable": "Tenho orçamento de R$ 5.000 e posso fazer aos finais de semana",
                    "relevant": "Quero um espaço que me inspire, seja funcional e reflita quem eu sou",
                    "time_bound": "Finalizar até maio de 2026"
                },
                "Criatividade": {
                    "specific": "Criar portfólio com 12 projetos criativos originais",
                    "measurable": "1 projeto completo por mês (arte, design, escrita, música, etc.)",
                    "achievable": "Vou dedicar 3 horas por semana + tenho materiais e ferramentas necessárias",
                    "relevant": "Quero expressar minha criatividade, desenvolver meu estilo e compartilhar minha arte",
                    "time_bound": "Portfólio completo até dezembro de 2026"
                }
            }
            
            # Get examples for selected area
            examples = area_examples.get(goal_area, area_examples["Saúde"])
            
            # Row 1: Specific & Measurable
            with col1:
                st.markdown("""
                <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.06) 0%, rgba(118, 75, 162, 0.04) 100%);
                            padding: 1rem;
                            border-radius: 10px;
                            margin-bottom: 1rem;
                            border-left: 3px solid #667eea;">
                    <p style="margin: 0; color: #667eea; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                        🎯 Specific
                    </p>
                    <p style="margin: 0.25rem 0 0 0; color: #64748b; font-size: 0.85rem;">
                        O que exatamente você quer alcançar?
                    </p>
                </div>
                """, unsafe_allow_html=True)
                specific = st_quill(
                    placeholder=f"Ex: {examples['specific']}",
                    html=True,
                    key="specific_editor",
                    toolbar=["bold", "italic", "underline", "strike", "blockquote", 
                            {"list": "ordered"}, {"list": "bullet"}, "link"]
                )
            
            with col2:
                st.markdown("""
                <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.06) 0%, rgba(118, 75, 162, 0.04) 100%);
                            padding: 1rem;
                            border-radius: 10px;
                            margin-bottom: 1rem;
                            border-left: 3px solid #667eea;">
                    <p style="margin: 0; color: #667eea; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                        📊 Measurable
                    </p>
                    <p style="margin: 0.25rem 0 0 0; color: #64748b; font-size: 0.85rem;">
                        Como você vai medir o progresso?
                    </p>
                </div>
                """, unsafe_allow_html=True)
                measurable = st_quill(
                    placeholder=f"Ex: {examples['measurable']}",
                    html=True,
                    key="measurable_editor",
                    toolbar=["bold", "italic", "underline", "strike", "blockquote", 
                            {"list": "ordered"}, {"list": "bullet"}, "link"]
                )
            
            # Row 2: Achievable & Relevant
            col3, col4 = st.columns(2)
            
            with col3:
                st.markdown("""
                <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.06) 0%, rgba(118, 75, 162, 0.04) 100%);
                            padding: 1rem;
                            border-radius: 10px;
                            margin-bottom: 1rem;
                            border-left: 3px solid #667eea;">
                    <p style="margin: 0; color: #667eea; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                        ✅ Achievable
                    </p>
                    <p style="margin: 0.25rem 0 0 0; color: #64748b; font-size: 0.85rem;">
                        É realista? Você tem recursos?
                    </p>
                </div>
                """, unsafe_allow_html=True)
                achievable = st_quill(
                    placeholder=f"Ex: {examples['achievable']}",
                    html=True,
                    key="achievable_editor",
                    toolbar=["bold", "italic", "underline", "strike", "blockquote", 
                            {"list": "ordered"}, {"list": "bullet"}, "link"]
                )
            
            with col4:
                st.markdown("""
                <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.06) 0%, rgba(118, 75, 162, 0.04) 100%);
                            padding: 1rem;
                            border-radius: 10px;
                            margin-bottom: 1rem;
                            border-left: 3px solid #667eea;">
                    <p style="margin: 0; color: #667eea; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                        💫 Relevant
                    </p>
                    <p style="margin: 0.25rem 0 0 0; color: #64748b; font-size: 0.85rem;">
                        Por que isso é importante para você?
                    </p>
                </div>
                """, unsafe_allow_html=True)
                relevant = st_quill(
                    placeholder=f"Ex: {examples['relevant']}",
                    html=True,
                    key="relevant_editor",
                    toolbar=["bold", "italic", "underline", "strike", "blockquote", 
                            {"list": "ordered"}, {"list": "bullet"}, "link"]
                )
            
            # Row 3: Priority & Time-bound
            col5, col6 = st.columns(2)
            
            with col5:
                st.markdown("""
                <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.06) 0%, rgba(118, 75, 162, 0.04) 100%);
                            padding: 1rem;
                            border-radius: 10px;
                            margin-bottom: 1rem;
                            border-left: 3px solid #667eea;">
                    <p style="margin: 0; color: #667eea; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                        ⭐ Prioridade da Meta
                    </p>
                    <p style="margin: 0.25rem 0 0 0; color: #64748b; font-size: 0.85rem;">
                        Defina o quão importante é esta meta para você
                    </p>
                </div>
                """, unsafe_allow_html=True)
                priority = st.select_slider(
                    "⭐ Nível de Prioridade",
                    options=["Baixa", "Média", "Alta", "Crítica"],
                    value="Média",
                    help="Defina o quão importante é esta meta para você",
                    label_visibility="collapsed"
                )
            
            with col6:
                st.markdown("""
                <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.06) 0%, rgba(118, 75, 162, 0.04) 100%);
                            padding: 1rem;
                            border-radius: 10px;
                            margin-bottom: 1rem;
                            border-left: 3px solid #667eea;">
                    <p style="margin: 0; color: #667eea; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                        ⏰ Time-bound
                    </p>
                    <p style="margin: 0.25rem 0 0 0; color: #64748b; font-size: 0.85rem;">
                        Qual o prazo?
                    </p>
                </div>
                """, unsafe_allow_html=True)
                time_bound = st.date_input(
                    "time_bound_label",
                    help="Defina uma data realista para alcançar esta meta",
                    label_visibility="collapsed",
                    format="DD/MM/YYYY"
                )
            
            st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
            submit_goal = st.form_submit_button("✨ Criar Meta", type="primary", use_container_width=True)
            
            if submit_goal and specific:
                new_goal = {
                    "area": goal_area,
                    "specific": specific,
                    "measurable": measurable,
                    "achievable": achievable,
                    "relevant": relevant,
                    "time_bound": time_bound.isoformat() if time_bound else "",
                    "priority": priority,
                    "completed": False,
                    "created_date": datetime.now().isoformat()
                }
                st.session_state.smart_goals.append(new_goal)
                save_data()

                # Clear prefill state after successful submission
                if 'prefill_area' in st.session_state:
                    del st.session_state.prefill_area
                if 'expand_goal_form' in st.session_state:
                    del st.session_state.expand_goal_form

                st.success("✨ Meta adicionada com sucesso!")
                st.rerun()

    # Edit goal dialog
    if 'editing_goal_idx' in st.session_state and st.session_state.editing_goal_idx is not None:
        edit_idx = st.session_state.editing_goal_idx
        if edit_idx < len(st.session_state.smart_goals):
            edit_goal = st.session_state.smart_goals[edit_idx]

            st.markdown("---")
            st.markdown("### ✏️ Editar Meta")

            with st.form("edit_goal_form"):
                # Area dropdown
                area_list = list(st.session_state.roda_scores.keys())
                current_area_idx = area_list.index(edit_goal['area']) if edit_goal['area'] in area_list else 0

                edit_area = st.selectbox(
                    "Área da Vida",
                    area_list,
                    index=current_area_idx
                )

                col1, col2 = st.columns(2)

                with col1:
                    edit_specific = st.text_area(
                        "📍 Specific - O que exatamente você quer alcançar?",
                        value=edit_goal.get('specific', '')
                    )
                    edit_measurable = st.text_area(
                        "📊 Measurable - Como você vai medir o progresso?",
                        value=edit_goal.get('measurable', '')
                    )
                    edit_achievable = st.text_area(
                        "✅ Achievable - É realista? Você tem recursos?",
                        value=edit_goal.get('achievable', '')
                    )

                with col2:
                    edit_relevant = st.text_area(
                        "🎯 Relevant - Por que isso é importante para você?",
                        value=edit_goal.get('relevant', '')
                    )
                    # Handle existing text dates or date objects
                    existing_time_bound = edit_goal.get('time_bound', '')
                    if existing_time_bound:
                        if isinstance(existing_time_bound, str):
                            try:
                                from datetime import datetime
                                edit_time_bound = st.date_input(
                                    "⏰ Time-bound - Qual o prazo?",
                                    value=datetime.fromisoformat(existing_time_bound).date()
                                )
                            except:
                                edit_time_bound = st.date_input("⏰ Time-bound - Qual o prazo?")
                        else:
                            edit_time_bound = st.date_input(
                                "⏰ Time-bound - Qual o prazo?",
                                value=existing_time_bound
                            )
                    else:
                        edit_time_bound = st.date_input("⏰ Time-bound - Qual o prazo?")

                current_priority = edit_goal.get('priority', 'Média')
                priority_options = ["Baixa", "Média", "Alta", "Crítica"]
                priority_idx = priority_options.index(current_priority) if current_priority in priority_options else 1

                edit_priority = st.select_slider(
                    "⭐ Prioridade",
                    options=priority_options,
                    value=priority_options[priority_idx]
                )

                # Form buttons
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    save_changes = st.form_submit_button("💾 Salvar Alterações", use_container_width=True, type="primary")
                with btn_col2:
                    cancel_edit = st.form_submit_button("❌ Cancelar", use_container_width=True)

                if save_changes and edit_specific:
                    # Update the goal
                    st.session_state.smart_goals[edit_idx].update({
                        "area": edit_area,
                        "specific": edit_specific,
                        "measurable": edit_measurable,
                        "achievable": edit_achievable,
                        "relevant": edit_relevant,
                        "time_bound": edit_time_bound.isoformat() if edit_time_bound else "",
                        "priority": edit_priority
                    })
                    save_data()
                    del st.session_state.editing_goal_idx
                    st.success("✅ Meta atualizada com sucesso!")
                    st.rerun()

                if cancel_edit:
                    del st.session_state.editing_goal_idx
                    st.rerun()

            st.markdown("---")

    # Display existing goals
    if st.session_state.smart_goals:
        # Stats section
        total_goals = len(st.session_state.smart_goals)
        completed_goals = len([g for g in st.session_state.smart_goals if g.get('completed', False)])
        pending_goals = total_goals - completed_goals
        completion_rate = (completed_goals / total_goals * 100) if total_goals > 0 else 0

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 1.5rem 2rem;
                    border-radius: 16px;
                    margin: 0 0 1.5rem 0;
                    box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2);">
            <h3 style="color: white; margin: 0 0 1.25rem 0; font-size: 1.4rem; font-weight: 700;">
                🎯 Suas Metas 2026
            </h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem;">
                <div style="background: rgba(255, 255, 255, 0.15);
                            backdrop-filter: blur(10px);
                            padding: 1.25rem;
                            border-radius: 12px;
                            border: 1px solid rgba(255, 255, 255, 0.2);">
                    <div style="color: rgba(255, 255, 255, 0.9); font-size: 0.85rem; font-weight: 500; margin-bottom: 0.5rem;">
                        Total de Metas
                    </div>
                    <div style="color: white; font-size: 2rem; font-weight: 800;">
                        {total_goals}
                    </div>
                </div>
                <div style="background: rgba(255, 255, 255, 0.15);
                            backdrop-filter: blur(10px);
                            padding: 1.25rem;
                            border-radius: 12px;
                            border: 1px solid rgba(255, 255, 255, 0.2);">
                    <div style="color: rgba(255, 255, 255, 0.9); font-size: 0.85rem; font-weight: 500; margin-bottom: 0.5rem;">
                        Completadas
                    </div>
                    <div style="color: white; font-size: 2rem; font-weight: 800;">
                        {completed_goals}
                    </div>
                </div>
                <div style="background: rgba(255, 255, 255, 0.15);
                            backdrop-filter: blur(10px);
                            padding: 1.25rem;
                            border-radius: 12px;
                            border: 1px solid rgba(255, 255, 255, 0.2);">
                    <div style="color: rgba(255, 255, 255, 0.9); font-size: 0.85rem; font-weight: 500; margin-bottom: 0.5rem;">
                        Em Progresso
                    </div>
                    <div style="color: white; font-size: 2rem; font-weight: 800;">
                        {pending_goals}
                    </div>
                </div>
                <div style="background: rgba(255, 255, 255, 0.15);
                            backdrop-filter: blur(10px);
                            padding: 1.25rem;
                            border-radius: 12px;
                            border: 1px solid rgba(255, 255, 255, 0.2);">
                    <div style="color: rgba(255, 255, 255, 0.9); font-size: 0.85rem; font-weight: 500; margin-bottom: 0.5rem;">
                        Taxa de Conclusão
                    </div>
                    <div style="color: white; font-size: 2rem; font-weight: 800;">
                        {completion_rate:.0f}%
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Check for filter state from insights CTA buttons
        filter_area_default = st.session_state.get('filter_to_area', "Todas")
        filter_status_default = st.session_state.get('filter_to_status', "Todas")

        # Compact filter section
        st.markdown("""
        <div style="margin: 1rem 0 1.5rem 0;">
            <h4 style="color: #667eea; margin: 0 0 0.75rem 0; font-size: 0.95rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                🔍 Filtrar
            </h4>
        </div>
        """, unsafe_allow_html=True)

        # Filter options
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        with filter_col1:
            area_options = ["Todas"] + list(st.session_state.roda_scores.keys())
            area_index = 0
            if filter_area_default != "Todas" and filter_area_default in area_options:
                area_index = area_options.index(filter_area_default)
            filter_area = st.selectbox("📍 Área", area_options, index=area_index)

        with filter_col2:
            status_options = ["Todas", "Completadas", "Pendentes"]
            status_index = status_options.index(filter_status_default) if filter_status_default in status_options else 0
            filter_status = st.selectbox("✓ Status", status_options, index=status_index)

        with filter_col3:
            filter_priority = st.selectbox("⭐ Prioridade", ["Todas", "Crítica", "Alta", "Média", "Baixa"])

        # Clear filter state after applying (so it doesn't persist on next load)
        if 'filter_to_area' in st.session_state:
            del st.session_state.filter_to_area
        if 'filter_to_status' in st.session_state:
            del st.session_state.filter_to_status
        
        filtered_goals = st.session_state.smart_goals.copy()
        
        if filter_area != "Todas":
            filtered_goals = [g for g in filtered_goals if g['area'] == filter_area]
        if filter_status == "Completadas":
            filtered_goals = [g for g in filtered_goals if g.get('completed', False)]
        elif filter_status == "Pendentes":
            filtered_goals = [g for g in filtered_goals if not g.get('completed', False)]
        if filter_priority != "Todas":
            filtered_goals = [g for g in filtered_goals if g.get('priority', 'Média') == filter_priority]
        
        # Area emojis mapping
        area_emojis = {
            "Saúde": "😊",
            "Carreira": "👩🏻‍💻",
            "Finanças": "💸",
            "Relacionamentos": "❤️",
            "Família": "🤗",
            "Espiritualidade": "🧘🏼‍♀️",
            "Diversão": "🎉",
            "Crescimento Pessoal": "🌱",
            "Ambiente Físico": "🏡",
            "Criatividade": "🎨"
        }

        # Priority colors
        priority_colors = {
            "Crítica": "#ef4444",
            "Alta": "#f59e0b",
            "Média": "#3b82f6",
            "Baixa": "#64748b"
        }

        st.markdown("""
        <div style="margin: 1.5rem 0 1rem 0;">
            <h3 style="color: #1a202c; margin: 0; font-size: 1.2rem; font-weight: 700; display: flex; align-items: center; gap: 0.5rem;">
                <span style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">📋 Lista de Metas</span>
            </h3>
        </div>
        """, unsafe_allow_html=True)

        # Initialize expanded goals state
        if 'expanded_goals' not in st.session_state:
            st.session_state.expanded_goals = set()

        for idx, goal in enumerate(filtered_goals):
            # Find original index
            original_idx = st.session_state.smart_goals.index(goal)

            # Get area emoji
            area_name = goal['area'].split('/')[0]  # Extract Portuguese part
            area_emoji = area_emojis.get(area_name, "")

            # Format deadline for display
            time_bound_display = goal['time_bound']
            if time_bound_display:
                try:
                    date_obj = datetime.fromisoformat(goal['time_bound']).date()
                    time_bound_display = date_obj.strftime('%d/%m/%Y')
                except:
                    pass

            # Get priority color
            priority = goal.get('priority', 'Média')
            priority_color = priority_colors.get(priority, "#64748b")

            # Check if completed
            is_completed = goal.get('completed', False)
            card_opacity = "0.6" if is_completed else "1"
            completed_badge = "✓ Completada" if is_completed else "Em Progresso"
            completed_color = "#10b981" if is_completed else "#667eea"

            # Check if this goal is expanded
            is_expanded = original_idx in st.session_state.expanded_goals
            expand_icon = "▼" if is_expanded else "▶"

            # Always visible card header
            st.markdown(f"""
            <div style="background: white;
                        border-radius: 16px;
                        border-left: 6px solid {priority_color};
                        padding: 0;
                        margin-bottom: 1.5rem;
                        opacity: {card_opacity};
                        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06), 0 4px 24px rgba({priority_color[1:]}, 0.08);
                        transition: all 0.3s ease;
                        overflow: hidden;">
                <div style="padding: 1.75rem;">
                    <div style="display: flex; justify-content: space-between; align-items: start; gap: 1rem;">
                        <div style="flex: 1;">
                            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
                                <span style="font-size: 1.5rem;">{area_emoji}</span>
                                <h4 style="color: #1a202c; margin: 0; font-size: 1.2rem; font-weight: 700;">
                                    {goal['area']}
                                </h4>
                            </div>
                            <p style="color: #64748b; margin: 0 0 1.25rem 0; font-size: 1rem; line-height: 1.6;">
                                {goal['specific'][:120]}{"..." if len(goal['specific']) > 120 else ""}
                            </p>
                            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem;">
                                <span style="background: {priority_color};
                                             color: white;
                                             padding: 0.4rem 0.9rem;
                                             border-radius: 24px;
                                             font-size: 0.85rem;
                                             font-weight: 600;
                                             box-shadow: 0 2px 8px rgba({priority_color[1:]}, 0.25);">
                                    ⭐ {priority}
                                </span>
                                <span style="background: {completed_color};
                                             color: white;
                                             padding: 0.4rem 0.9rem;
                                             border-radius: 24px;
                                             font-size: 0.85rem;
                                             font-weight: 600;
                                             box-shadow: 0 2px 8px rgba({completed_color[1:]}, 0.25);">
                                    {completed_badge}
                                </span>
                                <span style="background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
                                             color: #334155;
                                             padding: 0.4rem 0.9rem;
                                             border-radius: 24px;
                                             font-size: 0.85rem;
                                             font-weight: 600;
                                             border: 1px solid #cbd5e1;">
                                    ⏰ {time_bound_display}
                                </span>
                            </div>
            """, unsafe_allow_html=True)
            
            # Expand button inside the card
            expand_button_label = f"{expand_icon}  Ver Detalhes" if not is_expanded else f"{expand_icon}  Ocultar Detalhes"
            if st.button(
                expand_button_label,
                key=f"expand_goal_{original_idx}",
                use_container_width=True,
                help="Clique para expandir/recolher os detalhes SMART"
            ):
                if is_expanded:
                    st.session_state.expanded_goals.remove(original_idx)
                else:
                    st.session_state.expanded_goals.add(original_idx)
                st.rerun()
            
            st.markdown("""
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Expandable content
            if is_expanded:
                st.markdown("""
                <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.03) 0%, rgba(118, 75, 162, 0.02) 100%); 
                            padding: 2rem; 
                            border-radius: 0 0 16px 16px; 
                            margin-top: -1.5rem;
                            margin-bottom: 1.5rem;
                            border: 1px solid rgba(102, 126, 234, 0.1);
                            border-top: none;">
                    <h4 style="color: #667eea; margin: 0 0 1.5rem 0; font-size: 1.2rem; font-weight: 700;">
                        📋 Detalhes da Meta SMART
                    </h4>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.06) 0%, rgba(118, 75, 162, 0.04) 100%);
                                padding: 1.25rem;
                                border-radius: 12px;
                                margin-bottom: 1rem;
                                border-left: 3px solid #667eea;
                                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);">
                        <p style="margin: 0 0 0.75rem 0; color: #667eea; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                            🎯 Específico
                        </p>
                        <div style="margin: 0; color: #1a202c; font-size: 1rem; line-height: 1.7;">
                            {goal['specific']}
                        </div>
                    </div>

                    <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.06) 0%, rgba(118, 75, 162, 0.04) 100%);
                                padding: 1.25rem;
                                border-radius: 12px;
                                margin-bottom: 1rem;
                                border-left: 3px solid #667eea;
                                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);">
                        <p style="margin: 0 0 0.75rem 0; color: #667eea; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                            📊 Mensurável
                        </p>
                        <div style="margin: 0; color: #1a202c; font-size: 1rem; line-height: 1.7;">
                            {goal['measurable']}
                        </div>
                    </div>

                    <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.06) 0%, rgba(118, 75, 162, 0.04) 100%);
                                padding: 1.25rem;
                                border-radius: 12px;
                                margin-bottom: 1rem;
                                border-left: 3px solid #667eea;
                                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);">
                        <p style="margin: 0 0 0.75rem 0; color: #667eea; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                            ✅ Alcançável
                        </p>
                        <div style="margin: 0; color: #1a202c; font-size: 1rem; line-height: 1.7;">
                            {goal['achievable']}
                        </div>
                    </div>

                    <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.06) 0%, rgba(118, 75, 162, 0.04) 100%);
                                padding: 1.25rem;
                                border-radius: 12px;
                                margin-bottom: 1rem;
                                border-left: 3px solid #667eea;
                                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);">
                        <p style="margin: 0 0 0.75rem 0; color: #667eea; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                            💫 Relevante
                        </p>
                        <div style="margin: 0; color: #1a202c; font-size: 1rem; line-height: 1.7;">
                            {goal['relevant']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if 'created_date' in goal:
                        created = datetime.fromisoformat(goal['created_date'])
                        st.markdown(f"""
                        <div style="margin-top: 1rem; padding: 0.75rem; background: rgba(102, 126, 234, 0.05); border-radius: 8px; border-left: 3px solid #667eea;">
                            <p style="margin: 0; color: #64748b; font-size: 0.85rem;">
                                📅 <strong>Criada em:</strong> {created.strftime('%d/%m/%Y às %H:%M')}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

                with col2:
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.03) 100%);
                                padding: 1.25rem;
                                border-radius: 12px;
                                border: 2px solid rgba(102, 126, 234, 0.1);
                                height: 100%;">
                        <h4 style="color: #667eea; margin: 0 0 1rem 0; font-size: 1rem; font-weight: 700;">
                            Ações
                        </h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    completed = st.checkbox(
                        "✅ Marcar como Completada",
                        value=goal.get('completed', False),
                        key=f"goal_complete_{original_idx}"
                    )
                    st.session_state.smart_goals[original_idx]['completed'] = completed

                    if completed != goal.get('completed', False):
                        save_data()

                    st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)

                    # Edit and Delete buttons in two columns
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("✏️ Editar", key=f"edit_{original_idx}", use_container_width=True):
                            st.session_state.editing_goal_idx = original_idx
                            st.rerun()
                    with btn_col2:
                        if st.button("🗑️ Excluir", key=f"delete_{original_idx}", use_container_width=True):
                            st.session_state.smart_goals.pop(original_idx)
                            save_data()
                            st.rerun()
    else:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 3rem 2rem; background: linear-gradient(135deg, rgba(102, 126, 234, 0.03) 0%, rgba(118, 75, 162, 0.03) 100%); border: 2px dashed rgba(102, 126, 234, 0.2);">
            <div style="font-size: 4rem; margin-bottom: 1rem; opacity: 0.6;">🎯</div>
            <h3 style="color: #1a202c; margin: 0 0 0.75rem 0; font-size: 1.5rem; font-weight: 700;">
                Comece sua Jornada 2026
            </h3>
            <p style="color: #64748b; margin: 0 0 1.5rem 0; font-size: 1rem; line-height: 1.6; max-width: 500px; margin-left: auto; margin-right: auto;">
                Você ainda não criou nenhuma meta SMART. Use o formulário acima para definir seus objetivos e começar a transformar seus sonhos em realidade! ✨
            </p>
            <p style="color: #667eea; font-weight: 600; font-size: 0.95rem;">
                👆 Role para cima e clique em "➕ Criar Nova Meta SMART"
            </p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# TAB 4: DASHBOARD
# ============================================================================

with tab4:
    st.markdown("""
    <div class="section-header">
        <h2 style="color: white; margin: 0; font-size: 2rem; font-weight: 800; letter-spacing: -0.5px;">
            📊 Dashboard
        </h2>
        <p style="color: rgba(255,255,255,0.95); margin: 0.5rem 0 0 0; font-size: 1rem;">
            Visão geral do seu progresso e áreas de foco
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Hero Stats Cards
    total_goals = len(st.session_state.smart_goals)
    completed_goals = sum(1 for g in st.session_state.smart_goals if g.get('completed', False))
    completion_rate = (completed_goals / total_goals * 100) if total_goals > 0 else 0
    avg_roda = sum(st.session_state.roda_scores.values()) / len(st.session_state.roda_scores)
    
    # Count areas with goals
    areas_with_goals = len(set(g['area'] for g in st.session_state.smart_goals)) if st.session_state.smart_goals else 0
    total_life_areas = len(st.session_state.roda_scores)
    
    # Quick insights
    pending_goals = total_goals - completed_goals
    areas_without_goals = total_life_areas - areas_with_goals
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Determine score-based styling
        if avg_roda >= 8:
            score_color = "#10b981"
            heart_emoji = "💚"
        elif avg_roda >= 7:
            score_color = "#3b82f6"
            heart_emoji = "💙"
        elif avg_roda >= 5:
            score_color = "#f59e0b"
            heart_emoji = "🧡"
        else:
            score_color = "#ef4444"
            heart_emoji = "❤️"
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 1.5rem;
                    border-radius: 16px;
                    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
                    text-align: center;">
            <div style="color: rgba(255,255,255,0.9); font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.5rem;">
                Roda da Vida
            </div>
            <div style="color: {score_color}; font-size: 2.5rem; font-weight: 800; line-height: 1;">
                {avg_roda:.1f} {heart_emoji}
            </div>
            <div style="color: rgba(255,255,255,0.8); font-size: 0.8rem; margin-top: 0.5rem;">
                de 10
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: white;
                    padding: 1.5rem;
                    border-radius: 16px;
                    border-left: 5px solid #10b981;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                    text-align: center;">
            <div style="color: #64748b; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.5rem;">
                Metas Ativas
            </div>
            <div style="color: #1a202c; font-size: 2.5rem; font-weight: 800; line-height: 1;">
                {total_goals}
            </div>
            <div style="color: #10b981; font-size: 0.8rem; margin-top: 0.5rem; font-weight: 600;">
                {areas_with_goals}/{total_life_areas} áreas
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: white;
                    padding: 1.5rem;
                    border-radius: 16px;
                    border-left: 5px solid #3b82f6;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                    text-align: center;">
            <div style="color: #64748b; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.5rem;">
                Concluídas
            </div>
            <div style="color: #1a202c; font-size: 2.5rem; font-weight: 800; line-height: 1;">
                {completed_goals}
            </div>
            <div style="color: #3b82f6; font-size: 0.8rem; margin-top: 0.5rem; font-weight: 600;">
                {pending_goals} pendentes
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        rate_color = "#10b981" if completion_rate >= 50 else "#f59e0b" if completion_rate >= 25 else "#ef4444"
        st.markdown(f"""
        <div style="background: white;
                    padding: 1.5rem;
                    border-radius: 16px;
                    border-left: 5px solid {rate_color};
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                    text-align: center;">
            <div style="color: #64748b; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.5rem;">
                Taxa de Conclusão
            </div>
            <div style="color: #1a202c; font-size: 2.5rem; font-weight: 800; line-height: 1;">
                {completion_rate:.0f}%
            </div>
            <div style="color: {rate_color}; font-size: 0.8rem; margin-top: 0.5rem; font-weight: 600;">
                {completed_goals}/{total_goals} metas
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick Action Insights
    if areas_without_goals > 0 or pending_goals > 5:
        st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
        insights = []
        
        if areas_without_goals > 0:
            insights.append(f"💡 **{areas_without_goals} área(s)** ainda sem metas definidas")
        
        if pending_goals > 5:
            insights.append(f"⚡ **{pending_goals} metas pendentes** - considere priorizar as mais importantes")
        
        if completion_rate < 20 and total_goals > 3:
            insights.append(f"🎯 Foco! Tente concluir pelo menos 1-2 metas esta semana")
        
        if insights:
            st.markdown(f"""
            <div style="background: rgba(102, 126, 234, 0.1);
                        padding: 1rem 1.5rem;
                        border-radius: 12px;
                        border-left: 4px solid #667eea;">
                <div style="color: #667eea; font-weight: 700; margin-bottom: 0.5rem;">⚡ Insights Rápidos</div>
                <div style="color: #1a202c; font-size: 0.9rem;">
                    {' • '.join(insights)}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin: 2.5rem 0 1.5rem 0;">
        <h3 style="color: #667eea; margin: 0; font-size: 1.2rem; font-weight: 700;">
            🎯 Áreas que Precisam de Atenção
        </h3>
        <p style="color: #64748b; margin: 0.3rem 0 0 0; font-size: 0.9rem;">
            Pontuações mais baixas - áreas para focar
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Get bottom 3 and top 3 areas
    sorted_areas = sorted(st.session_state.roda_scores.items(), key=lambda x: x[1])
    bottom_3 = sorted_areas[:3]
    top_3 = sorted_areas[-3:][::-1]  # Reverse to show highest first

    # Create gauge charts - Bottom 3
    gauge_col1, gauge_col2, gauge_col3 = st.columns(3)

    # Define colors for different score ranges
    def get_gauge_color(score):
        if score <= 3:
            return "#ef4444"  # Red
        elif score <= 5:
            return "#f59e0b"  # Orange
        elif score <= 7:
            return "#3b82f6"  # Blue
        else:
            return "#10b981"  # Green

    # Emoji mapping for each area
    area_emojis = {
        "Saúde": "😊",
        "Carreira": "👩🏻‍💻",
        "Finanças": "💸",
        "Relacionamentos": "❤️",
        "Família": "🤗",
        "Espiritualidade": "🧘🏼‍♀️",
        "Diversão": "🎉",
        "Crescimento Pessoal": "🌱",
        "Ambiente Físico": "🏡",
        "Criatividade": "🎨"
    }

    for idx, (area, score) in enumerate(bottom_3):
        col = [gauge_col1, gauge_col2, gauge_col3][idx]
        area_name = area.split('/')[0]  # Get Portuguese name
        emoji = area_emojis.get(area_name, "")
        display_name = f"{emoji} {area_name}" if emoji else area_name

        with col:
            # Create gauge chart
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=float(score),
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': display_name, 'font': {'size': 16, 'color': '#1a202c', 'family': 'Inter'}},
                number={'font': {'size': 36, 'color': '#1a202c', 'family': 'Inter', 'weight': 'bold'}, 'valueformat': '.1f'},
                gauge={
                    'axis': {'range': [0, 10], 'tickwidth': 1, 'tickcolor': "#cbd5e1"},
                    'bar': {'color': get_gauge_color(score), 'thickness': 0.7},
                    'bgcolor': "white",
                    'borderwidth': 0,
                    'bordercolor': "white",
                    'steps': [
                        {'range': [0, 10], 'color': '#f1f5f9'}
                    ],
                    'threshold': {
                        'line': {'color': "white", 'width': 0},
                        'thickness': 0,
                        'value': 10
                    }
                }
            ))

            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': "#1a202c", 'family': 'Inter'},
                height=270,
                margin=dict(l=10, r=10, t=90, b=10),
                uirevision='constant'
            )

            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    st.markdown("""
    <div style="margin: 2.5rem 0 1.5rem 0;">
        <h3 style="color: #10b981; margin: 0; font-size: 1.2rem; font-weight: 700;">
            ⭐ Áreas de Destaque
        </h3>
        <p style="color: #64748b; margin: 0.3rem 0 0 0; font-size: 0.9rem;">
            Pontuações mais altas - continue assim!
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Create gauge charts - Top 3
    gauge_col1, gauge_col2, gauge_col3 = st.columns(3)

    for idx, (area, score) in enumerate(top_3):
        col = [gauge_col1, gauge_col2, gauge_col3][idx]
        area_name = area.split('/')[0]
        emoji = area_emojis.get(area_name, "")
        display_name = f"{emoji} {area_name}" if emoji else area_name

        with col:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=float(score),
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': display_name, 'font': {'size': 16, 'color': '#1a202c', 'family': 'Inter'}},
                number={'font': {'size': 36, 'color': '#1a202c', 'family': 'Inter', 'weight': 'bold'}, 'valueformat': '.1f'},
                gauge={
                    'axis': {'range': [0, 10], 'tickwidth': 1, 'tickcolor': "#cbd5e1"},
                    'bar': {'color': get_gauge_color(score), 'thickness': 0.7},
                    'bgcolor': "white",
                    'borderwidth': 0,
                    'bordercolor': "white",
                    'steps': [
                        {'range': [0, 10], 'color': '#f1f5f9'}
                    ],
                    'threshold': {
                        'line': {'color': "white", 'width': 0},
                        'thickness': 0,
                        'value': 10
                    }
                }
            ))

            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': "#1a202c", 'family': 'Inter'},
                height=270,
                margin=dict(l=10, r=10, t=90, b=10),
                uirevision='constant'
            )

            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    st.markdown("---")

    # Goals Progress by Area
    st.markdown("""
    <div style="margin: 2rem 0 1rem 0;">
        <h3 style="color: #667eea; margin: 0; font-size: 1.2rem; font-weight: 700;">
            📈 Progresso de Metas por Área
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.smart_goals:
        goals_by_area = {}
        for goal in st.session_state.smart_goals:
            area = goal['area']
            if area not in goals_by_area:
                goals_by_area[area] = {'total': 0, 'completed': 0}
            goals_by_area[area]['total'] += 1
            if goal.get('completed', False):
                goals_by_area[area]['completed'] += 1
        
        # Color psychology-based colors for each life area
        area_color_map = {
            "Saúde": "#10b981",
            "Carreira": "#1e40af",
            "Finanças": "#eab308",
            "Relacionamentos": "#ec4899",
            "Família": "#f97316",
            "Espiritualidade": "#8b5cf6",
            "Diversão": "#d946ef",
            "Crescimento Pessoal": "#14b8a6",
            "Ambiente Físico": "#c2410c",
            "Criatividade": "#fb7185"
        }
        
        # Create progress cards
        cols = st.columns(min(len(goals_by_area), 5))
        
        for idx, (area, data) in enumerate(goals_by_area.items()):
            if idx < 5:  # Limit to 5 areas per row
                with cols[idx]:
                    area_name = area.split('/')[0]
                    total = data['total']
                    completed = data['completed']
                    progress_pct = (completed / total * 100) if total > 0 else 0
                    color = area_color_map.get(area, '#667eea')
                    
                    st.markdown(f"""
                    <div style="background: white;
                                padding: 1.2rem;
                                border-radius: 12px;
                                border-left: 4px solid {color};
                                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                                text-align: center;">
                        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">
                            {area_emojis.get(area_name, "📍")}
                        </div>
                        <div style="color: #1a202c; font-size: 0.85rem; font-weight: 700; margin-bottom: 0.8rem;">
                            {area_name}
                        </div>
                        <div style="background: #f1f5f9; height: 8px; border-radius: 4px; overflow: hidden; margin-bottom: 0.8rem;">
                            <div style="background: {color}; height: 100%; width: {progress_pct}%; transition: width 0.3s ease;"></div>
                        </div>
                        <div style="color: {color}; font-size: 1.25rem; font-weight: 800;">
                            {completed}/{total}
                        </div>
                        <div style="color: #64748b; font-size: 0.75rem; text-transform: uppercase;">
                            {progress_pct:.0f}% completo
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Show remaining areas in second row if more than 5
        if len(goals_by_area) > 5:
            st.markdown('<div style="margin-top: 1rem;"></div>', unsafe_allow_html=True)
            cols2 = st.columns(min(len(goals_by_area) - 5, 5))
            
            for idx, (area, data) in enumerate(list(goals_by_area.items())[5:10]):
                with cols2[idx]:
                    area_name = area.split('/')[0]
                    total = data['total']
                    completed = data['completed']
                    progress_pct = (completed / total * 100) if total > 0 else 0
                    color = area_color_map.get(area, '#667eea')
                    
                    st.markdown(f"""
                    <div style="background: white;
                                padding: 1.2rem;
                                border-radius: 12px;
                                border-left: 4px solid {color};
                                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                                text-align: center;">
                        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">
                            {area_emojis.get(area_name, "📍")}
                        </div>
                        <div style="color: #1a202c; font-size: 0.85rem; font-weight: 700; margin-bottom: 0.8rem;">
                            {area_name}
                        </div>
                        <div style="background: #f1f5f9; height: 8px; border-radius: 4px; overflow: hidden; margin-bottom: 0.8rem;">
                            <div style="background: {color}; height: 100%; width: {progress_pct}%; transition: width 0.3s ease;"></div>
                        </div>
                        <div style="color: {color}; font-size: 1.25rem; font-weight: 800;">
                            {completed}/{total}
                        </div>
                        <div style="color: #64748b; font-size: 0.75rem; text-transform: uppercase;">
                            {progress_pct:.0f}% completo
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("📝 Adicione metas na aba SMART Goals para ver o progresso por área")

    st.markdown("---")
    
    # Export section
    st.markdown("""
    <div style="margin: 2rem 0 1rem 0;">
        <h3 style="color: #667eea; margin: 0; font-size: 1.2rem; font-weight: 700;">
            💾 Exportar Seus Dados
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    export_data = {
        "roda_da_vida_2025": st.session_state.roda_scores,
        "smart_goals_2026": st.session_state.smart_goals,
        "reflections": {
            "conquistas_2025": st.session_state.get("conquistas_2025", ""),
            "desafios_2025": st.session_state.get("desafios_2025", ""),
            "aprendizados_2025": st.session_state.get("aprendizados_2025", ""),
            "gratidao_2025": st.session_state.get("gratidao_2025", "")
        },
        "data_criacao": datetime.now().isoformat()
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="📥 Download JSON",
            data=json.dumps(export_data, indent=2, ensure_ascii=False),
            file_name=f"plano_de_2026_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        df_export = pd.DataFrame({
            'Área': list(st.session_state.roda_scores.keys()),
            'Pontuação 2025': list(st.session_state.roda_scores.values())
        })
        
        csv = df_export.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"plano_de_2026_roda_vida_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# ============================================================================
# TAB 5: PROGRESS TRACKING
# ============================================================================

with tab5:
    st.markdown("""
    <div class="section-header">
        <h2 style="color: white; margin: 0; font-size: 2rem; font-weight: 800; letter-spacing: -0.5px;">
            📈 Progresso
        </h2>
        <p style="color: rgba(255,255,255,0.95); margin: 0.5rem 0 0 0; font-size: 1rem;">
            Acompanhe sua evolução ao longo do tempo
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("📝 Registrar Check-in Mensal", use_container_width=True, type="primary"):
            add_to_history()
            save_data()
            st.success("✅ Check-in registrado com sucesso!")
    
    with col2:
        num_checkins = len(st.session_state.history)
        st.markdown(f"""
        <div style="background: rgba(102, 126, 234, 0.1);
                    padding: 0.5rem 1rem;
                    border-radius: 4px;
                    text-align: center;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    height: 40px;
                    box-sizing: border-box;">
            <span style="color: #667eea; font-weight: 700; font-size: 0.95rem; line-height: 1;">
                📊 {num_checkins} check-in(s)
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    if st.session_state.history:
        # Calculate insights
        current_avg = st.session_state.history[-1]['avg_score']
        previous_avg = st.session_state.history[-2]['avg_score'] if len(st.session_state.history) > 1 else current_avg
        avg_change = current_avg - previous_avg
        
        # Calculate days since last check-in
        last_checkin = datetime.fromisoformat(st.session_state.history[-1]['date'])
        days_since = (datetime.now() - last_checkin).days
        
        # Find most improved and most declined areas
        if len(st.session_state.history) > 1:
            current_scores = st.session_state.history[-1]['roda_scores']
            previous_scores = st.session_state.history[-2]['roda_scores']
            
            changes = {}
            for area in current_scores.keys():
                if area in previous_scores:
                    changes[area] = current_scores[area] - previous_scores[area]
            
            most_improved = max(changes.items(), key=lambda x: x[1]) if changes else None
            most_declined = min(changes.items(), key=lambda x: x[1]) if changes else None
        else:
            most_improved = None
            most_declined = None
        
        # Progress Summary Cards
        st.markdown("""
        <div style="margin: 2rem 0 1rem 0;">
            <h3 style="color: #667eea; margin: 0; font-size: 1.2rem; font-weight: 700;">
                💡 Resumo de Progresso
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            trend = "↗️" if avg_change > 0 else "↘️" if avg_change < 0 else "➡️"
            trend_color = "#10b981" if avg_change > 0 else "#ef4444" if avg_change < 0 else "#64748b"
            
            # Determine score-based styling and message
            if current_avg >= 8:
                score_color = "#10b981"
                score_message = "Excelente! ✨"
                heart_emoji = "💚"
            elif current_avg >= 7:
                score_color = "#3b82f6"
                score_message = "Muito bom! 💙"
                heart_emoji = "💙"
            elif current_avg >= 5:
                score_color = "#f59e0b"
                score_message = "Em progresso"
                heart_emoji = "🧡"
            else:
                score_color = "#ef4444"
                score_message = "Precisa atenção"
                heart_emoji = "❤️"
            
            st.markdown(f"""
            <div style="background: white;
                        padding: 1.5rem;
                        border-radius: 12px;
                        border-left: 5px solid {score_color};
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                        text-align: center;
                        min-height: 140px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;">
                <div style="color: #64748b; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; margin-bottom: 0.5rem;">
                    Última Média
                </div>
                <div style="color: {score_color}; font-size: 2rem; font-weight: 800; line-height: 1;">
                    {current_avg:.1f}
                </div>
                <div style="color: {score_color}; font-size: 0.85rem; margin-top: 0.5rem; font-weight: 600;">
                    {heart_emoji} {score_message}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            days_color = "#10b981" if days_since <= 30 else "#f59e0b" if days_since <= 60 else "#ef4444"
            st.markdown(f"""
            <div style="background: white;
                        padding: 1.5rem;
                        border-radius: 12px;
                        border-left: 5px solid {days_color};
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                        text-align: center;
                        min-height: 140px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;">
                <div style="color: #64748b; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; margin-bottom: 0.5rem;">
                    Último Check-in
                </div>
                <div style="color: #1a202c; font-size: 2rem; font-weight: 800; line-height: 1;">
                    {days_since}
                </div>
                <div style="color: #64748b; font-size: 0.85rem; margin-top: 0.5rem; font-weight: 600;">
                    dias atrás
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            if most_improved and most_improved[1] > 0:
                area_name = most_improved[0].split('/')[0]
                st.markdown(f"""
                <div style="background: white;
                            padding: 1.5rem;
                            border-radius: 12px;
                            border-left: 5px solid #10b981;
                            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                            text-align: center;
                            min-height: 140px;
                            display: flex;
                            flex-direction: column;
                            justify-content: center;">
                    <div style="color: #64748b; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; margin-bottom: 0.5rem;">
                        Mais Melhorou
                    </div>
                    <div style="color: #1a202c; font-size: 1.1rem; font-weight: 700; line-height: 1.2; margin-bottom: 0.3rem;">
                        {area_name}
                    </div>
                    <div style="color: #10b981; font-size: 1.5rem; font-weight: 800;">
                        +{most_improved[1]:.1f}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background: white;
                            padding: 1.5rem;
                            border-radius: 12px;
                            border-left: 5px solid #64748b;
                            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                            text-align: center;
                            min-height: 140px;
                            display: flex;
                            flex-direction: column;
                            justify-content: center;">
                    <div style="color: #64748b; font-size: 0.85rem; line-height: 1.4;">
                        Primeiro check-in<br>ou sem mudanças
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col4:
            if most_declined and most_declined[1] < 0:
                area_name = most_declined[0].split('/')[0]
                st.markdown(f"""
                <div style="background: white;
                            padding: 1.5rem;
                            border-radius: 12px;
                            border-left: 5px solid #ef4444;
                            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                            text-align: center;
                            min-height: 140px;
                            display: flex;
                            flex-direction: column;
                            justify-content: center;">
                    <div style="color: #64748b; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; margin-bottom: 0.5rem;">
                        Precisa Atenção
                    </div>
                    <div style="color: #1a202c; font-size: 1.1rem; font-weight: 700; line-height: 1.2; margin-bottom: 0.3rem;">
                        {area_name}
                    </div>
                    <div style="color: #ef4444; font-size: 1.5rem; font-weight: 800;">
                        {most_declined[1]:.1f}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background: white;
                            padding: 1.5rem;
                            border-radius: 12px;
                            border-left: 5px solid #64748b;
                            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                            text-align: center;
                            min-height: 140px;
                            display: flex;
                            flex-direction: column;
                            justify-content: center;">
                    <div style="color: #64748b; font-size: 0.85rem; line-height: 1.4;">
                        Tudo mantendo<br>ou melhorando!
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Evolution chart
        st.markdown("""
        <div style="margin: 2rem 0 1rem 0;">
            <h3 style="color: #667eea; margin: 0; font-size: 1.2rem; font-weight: 700;">
                📊 Evolução ao Longo do Tempo
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Create timeline chart
        history_dates = [datetime.fromisoformat(h['date']) for h in st.session_state.history]
        history_avgs = [h['avg_score'] for h in st.session_state.history]
        
        df_history = pd.DataFrame({
            'Data': history_dates,
            'Média': history_avgs
        })
        
        # Convert to lists to avoid pyarrow issues
        dates_list = df_history['Data'].tolist()
        medias_list = [float(v) for v in df_history['Média'].tolist()]
        
        fig_timeline = go.Figure()
        fig_timeline.add_trace(go.Scatter(
            x=dates_list,
            y=medias_list,
            mode='lines+markers',
            name='Pontuação Média',
            line=dict(
                color='#667eea',
                width=4,
                smoothing=1.3
            ),
            marker=dict(
                size=12,
                color='#764ba2',
                line=dict(width=2, color='white')
            ),
            fill='tonexty',
            fillcolor='rgba(102, 126, 234, 0.1)',
            hovertemplate='<b>%{x}</b><br>Pontuação Média: %{y:.1f}/10<extra></extra>'
        ))
        
        fig_timeline.update_layout(
            title=dict(
                text='Evolução da Pontuação Média',
                font=dict(size=18, family='Inter', color='#1a202c')
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(
                color='#1a202c',
                family='Inter',
                size=14
            ),
            height=400,
            xaxis=dict(
                title='Data do Check-in',
                showgrid=True,
                gridcolor='rgba(102, 126, 234, 0.15)',
                linecolor='rgba(102, 126, 234, 0.3)'
            ),
            yaxis=dict(
                title='Pontuação Média',
                showgrid=True,
                gridcolor='rgba(102, 126, 234, 0.15)',
                linecolor='rgba(102, 126, 234, 0.3)',
                range=[0, 10]
            ),
            margin=dict(l=60, r=50, t=60, b=50),
            hovermode='x unified'
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        st.markdown("---")
        
        # Compact history with delete
        col_header, col_clear = st.columns([3, 1])
        
        with col_header:
            st.markdown("""
            <div style="margin: 2rem 0 1rem 0;">
                <h3 style="color: #667eea; margin: 0; font-size: 1.3rem; font-weight: 700;">
                    📋 Histórico de Check-ins
                </h3>
            </div>
            """, unsafe_allow_html=True)
        
        with col_clear:
            st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
            with st.popover("🗑️ Gerenciar Check-ins", use_container_width=True):
                st.markdown("**Selecione os check-ins para deletar:**")
                
                # Create list of check-in options
                check_in_options = []
                for idx, entry in enumerate(reversed(st.session_state.history)):
                    entry_date = datetime.fromisoformat(entry['date'])
                    avg_score = entry['avg_score']
                    check_in_options.append(f"{entry_date.strftime('%d/%m/%Y')} - Média: {avg_score:.1f}")
                
                # Option to select all
                select_all = st.checkbox("Selecionar todos", key="select_all_checkins")
                
                st.markdown("---")
                
                # Multiselect for specific check-ins
                if select_all:
                    selected = st.multiselect(
                        "Check-ins selecionados:",
                        options=check_in_options,
                        default=check_in_options,
                        label_visibility="collapsed"
                    )
                else:
                    selected = st.multiselect(
                        "Escolha os check-ins:",
                        options=check_in_options,
                        label_visibility="collapsed"
                    )
                
                st.markdown("---")
                
                # Delete button
                if selected:
                    st.warning(f"⚠️ {len(selected)} check-in(s) será(ão) deletado(s)")
                    if st.button("Confirmar Exclusão", type="primary", use_container_width=True):
                        # Find indices to delete
                        indices_to_delete = []
                        for sel in selected:
                            for idx, entry in enumerate(reversed(st.session_state.history)):
                                actual_idx = len(st.session_state.history) - 1 - idx
                                entry_date = datetime.fromisoformat(entry['date'])
                                avg_score = entry['avg_score']
                                option_str = f"{entry_date.strftime('%d/%m/%Y')} - Média: {avg_score:.1f}"
                                if option_str == sel:
                                    indices_to_delete.append(actual_idx)
                                    break
                        
                        # Delete in reverse order to maintain indices
                        for idx in sorted(indices_to_delete, reverse=True):
                            st.session_state.history.pop(idx)
                        
                        save_data()
                        st.rerun()
                else:
                    st.info("Selecione ao menos um check-in para deletar")
        
        st.markdown('<div style="margin-bottom: 1.5rem;"></div>', unsafe_allow_html=True)
        
        # Display most recent first
        for idx, entry in enumerate(reversed(st.session_state.history)):
            actual_idx = len(st.session_state.history) - 1 - idx
            entry_date = datetime.fromisoformat(entry['date'])
            avg_score = entry['avg_score']
            
            # Determine card styling based on score
            if avg_score >= 8:
                border_color = "#10b981"
                heart_emoji = "💚"
            elif avg_score >= 7:
                border_color = "#3b82f6"
                heart_emoji = "💙"
            elif avg_score >= 5:
                border_color = "#f59e0b"
                heart_emoji = "🧡"
            else:
                border_color = "#ef4444"
                heart_emoji = "❤️"
            
            # Unified card with integrated expander
            st.markdown(f"""
            <div style="background: white;
                        padding: 1.25rem 1.5rem;
                        border-radius: 12px;
                        border-left: 5px solid {border_color};
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                        margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="color: #667eea; font-weight: 600; font-size: 0.95rem;">
                        📅 {entry_date.strftime('%d/%m/%Y')}
                    </div>
                    <div style="color: {border_color}; font-weight: 800; font-size: 1.5rem;">
                        {heart_emoji} {avg_score:.1f}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Expander for details
            with st.expander("📊 Ver detalhes das áreas", expanded=False):
                # Show all areas with scores
                areas_list = list(entry['roda_scores'].keys())
                scores_list = [float(v) for v in entry['roda_scores'].values()]
                
                cols_areas = st.columns(2)
                for i, (area, score) in enumerate(zip(areas_list, scores_list)):
                    area_name = area.split('/')[0]
                    
                    # Color based on score
                    if score <= 3:
                        color = "#ef4444"
                    elif score <= 5:
                        color = "#f59e0b"
                    elif score <= 7:
                        color = "#3b82f6"
                    else:
                        color = "#10b981"
                    
                    with cols_areas[i % 2]:
                        st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; padding: 0.5rem 1rem; margin-bottom: 0.5rem; background: white; border-radius: 8px; border-left: 3px solid {color}; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);">
                            <span style="font-size: 0.9rem; color: #1a202c; font-weight: 500;">{area_name}</span>
                            <span style="font-weight: 700; color: {color}; font-size: 0.95rem;">{score:.1f}</span>
                        </div>
                        """, unsafe_allow_html=True)
    else:
        st.info("""
        📝 Nenhum check-in registrado ainda.

        Clique no botão "Registrar Check-in Mensal" para salvar sua avaliação atual da Roda da Vida.
        Isso permitirá que você acompanhe seu progresso ao longo do tempo!
        """)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #667eea; padding: 20px;'>
    <h3>Meu Plano de 2026 📔</h3>
    <p>Transformando chumbo em ouro | Turning lead into gold</p>
    <p style='margin-top: 15px; font-style: italic;'>A magia está em você 💜</p>
</div>
""", unsafe_allow_html=True)
