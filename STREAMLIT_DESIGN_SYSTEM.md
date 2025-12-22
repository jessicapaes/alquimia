# STREAMLIT DESIGN SYSTEM PROMPT - "Alquimia Style"

## Overview
Apply this modern, soft design system to create Streamlit apps with a premium white-box aesthetic inspired by the Bearable app. This design features glass-morphism effects, gradient accents, and persistent styling that survives Streamlit's dynamic updates.

---

## 1. PAGE CONFIGURATION

```python
st.set_page_config(
    page_title="Your App Name",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

---

## 2. COLOR PALETTE

- **Primary Purple**: `#667eea`
- **Secondary Violet**: `#764ba2`
- **Background Gray**: `#f8f9fa`
- **Text Dark**: `#1a202c`
- **Text Medium**: `#334155`
- **Border Light**: `#e2e8f0`
- **Border Lighter**: `#cbd5e1`

**Gradients:**
- Primary gradient: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- Hover variations with rgba and opacity adjustments

---

## 3. CORE CSS STRUCTURE

### Base Background & Container

```css
.main {
    background: #f8f9fa;
}
.stApp {
    background: #f8f9fa;
}
.block-container {
    padding-left: 3rem !important;
    padding-right: 3rem !important;
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    max-width: 1200px !important;
}
```

**CRITICAL**: Use light gray background (`#f8f9fa`) instead of white so that white boxes are visible.

---

## 4. TAB COMPONENT - WHITE BOX SYSTEM

This is the **most complex and critical** part. Streamlit dynamically updates tabs, so we need **triple-layer enforcement**:

### A. CSS Layer (Highest Priority)

```css
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
```

**KEY TECHNIQUE**: Negative margins (`margin: 2rem -3rem 3rem -3rem`) extend the white box beyond the container, combined with `calc(100% + 6rem)` width. This creates the "full bleed" effect.

### B. Multiple Selector Fallbacks

```css
.stTabs,
div[data-testid="stTabs"],
section[data-testid="stTabs"],
[data-testid="stTabs"],
div.stTabs,
section.stTabs {
    padding: 2rem 3rem 3rem 3rem !important;
    margin: 2rem -3rem 3rem -3rem !important;
    width: calc(100% + 6rem) !important;
    max-width: calc(100% + 6rem) !important;
    background: rgba(255, 255, 255, 0.98) !important;
    background-color: rgba(255, 255, 255, 0.98) !important;
    backdrop-filter: blur(10px) !important;
    -webkit-backdrop-filter: blur(10px) !important;
    border-radius: 25px !important;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07) !important,
                0 10px 15px rgba(0, 0, 0, 0.1) !important,
                0 20px 25px rgba(0, 0, 0, 0.08) !important;
    border: 1px solid rgba(0, 0, 0, 0.05) !important;
    box-sizing: border-box !important;
    position: relative !important;
}
```

### C. Pseudo-element Background Persistence

```css
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
```

### D. Child Override Prevention

```css
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
```

### E. Animation Trick for Persistence

```css
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
```

---

## 5. TAB BUTTON STYLING

### Nested White Box Around Tab Buttons

```css
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
```

### Individual Tab Buttons

```css
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

.stTabs [aria-selected="true"] * {
    color: white !important;
}

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
```

### Remove Default Tab Underlines

```css
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {
    background-color: transparent !important;
    display: none !important;
}

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
```

**CRITICAL**: Prevent tab clipping with `overflow: visible` and `z-index: 1`.

---

## 6. FORM INPUT STYLING - SOFT ROUNDED DESIGN

### Text Inputs & Textareas

```css
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
```

**KEY TECHNIQUE**: Dual `linear-gradient` backgrounds - one for `padding-box` (white fill) and one for `border-box` (gradient border). This creates the soft gradient border effect.

### Hover State

```css
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
```

### Focus State

```css
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
```

**DESIGN PHILOSOPHY**: High `border-radius` (25px), soft rgba gradients with low opacity (0.3-0.6), subtle shadows - creates organic, rounded appearance instead of harsh geometric boxes.

---

## 7. JAVASCRIPT ENFORCEMENT (CRITICAL)

Streamlit dynamically rebuilds the DOM on every interaction. You **MUST** use JavaScript to enforce styles persistently:

```javascript
<script>
    function forceTabPadding() {
        const tabs = document.querySelectorAll('[data-testid="stTabs"]');
        tabs.forEach(tab => {
            const styleStr = 'padding: 2rem 3rem 3rem 3rem !important; margin: 2rem -3rem 3rem -3rem !important; width: calc(100% + 6rem) !important; max-width: calc(100% + 6rem) !important; background: rgba(255, 255, 255, 0.98) !important; background-color: rgba(255, 255, 255, 0.98) !important; backdrop-filter: blur(10px) !important; border-radius: 25px !important; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07), 0 10px 15px rgba(0, 0, 0, 0.1), 0 20px 25px rgba(0, 0, 0, 0.08) !important; border: 1px solid rgba(0, 0, 0, 0.05) !important; position: relative !important; box-sizing: border-box !important;';

            tab.style.cssText += styleStr;
            tab.setAttribute('style', tab.getAttribute('style') + '; ' + styleStr);
        });
    }

    // Run immediately
    forceTabPadding();

    // MutationObserver to watch for DOM changes
    const tabObserver = new MutationObserver(() => {
        forceTabPadding();
    });

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

    // Aggressive continuous enforcement every 50ms
    setInterval(forceTabPadding, 50);

    // On user interactions
    document.addEventListener('click', () => setTimeout(forceTabPadding, 10));
    window.addEventListener('load', forceTabPadding);
</script>
```

**WHY THIS IS NECESSARY**: Streamlit rerenders components constantly. Without JavaScript enforcement, styles revert after page load or tab switches.

---

## 8. BUTTONS

```css
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 16px !important;
    padding: 14px 32px !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    transition: all 0.3s ease !important;
}

.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    background: linear-gradient(135deg, #5568d3 0%, #6a3f91 100%) !important;
    transform: translateY(-2px) !important;
}
```

---

## 9. SLIDERS - SOLID PURPLE WITH WHITE OUTLINE

Modern slider design with solid purple color and prominent white outline on the handle (circle).

### Design Philosophy
- **Solid colors** instead of gradients for cleaner look
- **Thick white outline** (4px) on handle for visual prominence
- **No outline** on track for streamlined appearance
- **Consistent purple** (#8b5cf6) matching the app's spirituality/consciousness theme

### A. CSS Styling

```css
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

/* Override Streamlit's accent-color */
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
```

### B. JavaScript Enforcement

```javascript
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

    // Delayed execution for dynamic content
    [10, 50, 100, 250, 500, 1000, 2000].forEach(delay => {
        setTimeout(forcePurpleSliders, delay);
    });

    // MutationObserver for DOM changes
    const sliderObserver = new MutationObserver(() => {
        forcePurpleSliders();
    });

    sliderObserver.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['style']
    });

    // Also run on any slider interaction
    document.addEventListener('mousedown', () => setTimeout(forcePurpleSliders, 10));
    document.addEventListener('mouseup', () => setTimeout(forcePurpleSliders, 10));
    document.addEventListener('input', () => setTimeout(forcePurpleSliders, 10));
</script>
```

### C. Adding Emojis to Slider Labels

For better visual organization, add area-specific emojis to slider labels:

```python
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

# When creating sliders
for area in areas_list:
    area_name = area.split('/')[0]  # Extract Portuguese part
    emoji = area_emojis.get(area_name, "")
    display_label = f"{emoji} {area}" if emoji else area

    st.slider(
        display_label,
        min_value=0,
        max_value=10,
        value=score,
        key=f"slider_{area}"
    )
```

**KEY DETAILS:**
- **White outline thickness**: 4px (was 2px originally - increased for better visibility)
- **Handle size**: 20px diameter circle
- **Track height**: 10px
- **Color**: #8b5cf6 (solid purple, not gradient)
- **Shadow**: Subtle shadow with purple tint for depth

---

## 10. GAUGE CHARTS - PLOTLY WITH COLOR-CODED SCORES

Gauge charts for displaying scores with contextual color coding and area emojis.

### Design Philosophy
- **Color psychology**: Different colors represent different score ranges
- **Emoji integration**: Visual area identification
- **Contextual feedback**: Colors indicate urgency/status at a glance
- **Clean design**: Minimal tick marks, focus on the score

### A. Color Coding System

```python
def get_gauge_color(score):
    """Returns color based on score range for psychological impact"""
    if score <= 3:
        return "#ef4444"  # Red - Critical, needs immediate attention
    elif score <= 5:
        return "#f59e0b"  # Orange - Needs attention
    elif score <= 7:
        return "#3b82f6"  # Blue - In development
    else:
        return "#10b981"  # Green - Excellent
```

**Color Ranges:**
- 🔴 0-3: Critical (Red #ef4444)
- 🟠 4-5: Needs Attention (Orange #f59e0b)
- 🔵 6-7: In Development (Blue #3b82f6)
- 🟢 8-10: Excellent (Green #10b981)

### B. Plotly Gauge Configuration

```python
import plotly.graph_objects as go

# Area emojis for visual identification
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

# Create gauge
area_name = "Saúde"  # Example
score = 4
emoji = area_emojis.get(area_name, "")
display_name = f"{emoji} {area_name}" if emoji else area_name

fig = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=score,
    domain={'x': [0, 1], 'y': [0, 1]},
    title={
        'text': display_name,
        'font': {'size': 16, 'color': '#1a202c', 'family': 'Inter'}
    },
    delta={
        'reference': 5,
        'increasing': {'color': "#10b981"},
        'decreasing': {'color': "#ef4444"}
    },
    number={
        'font': {'size': 36, 'color': '#1a202c', 'family': 'Inter', 'weight': 'bold'},
        'valueformat': '.0f'
    },
    gauge={
        'axis': {
            'range': [None, 10],
            'tickwidth': 1,
            'tickcolor': "#cbd5e1"
        },
        'bar': {
            'color': get_gauge_color(score),
            'thickness': 0.7
        },
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

st.plotly_chart(fig, use_container_width=True)
```

### C. Color Legend

Add a legend below gauges to explain color meanings:

```python
st.markdown("""
<div style="background: rgba(248, 250, 252, 0.8);
            padding: 1rem 1.5rem;
            border-radius: 12px;
            margin: 1.5rem 0;
            border: 1px solid #e2e8f0;">
    <div style="display: flex;
                justify-content: flex-start;
                align-items: center;
                gap: 2rem;
                flex-wrap: wrap;">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <div style="width: 16px; height: 16px; background: #ef4444; border-radius: 4px;"></div>
            <span style="color: #64748b; font-size: 0.9rem; font-weight: 600;">0-3: Crítico</span>
        </div>
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <div style="width: 16px; height: 16px; background: #f59e0b; border-radius: 4px;"></div>
            <span style="color: #64748b; font-size: 0.9rem; font-weight: 600;">4-5: Precisa Atenção</span>
        </div>
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <div style="width: 16px; height: 16px; background: #3b82f6; border-radius: 4px;"></div>
            <span style="color: #64748b; font-size: 0.9rem; font-weight: 600;">6-7: Em Desenvolvimento</span>
        </div>
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <div style="width: 16px; height: 16px; background: #10b981; border-radius: 4px;"></div>
            <span style="color: #64748b; font-size: 0.9rem; font-weight: 600;">8-10: Excelente</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
```

### D. Grid Layout for Multiple Gauges

Display multiple gauges in a responsive grid:

```python
# Create columns for gauge grid
cols = st.columns(5)  # 5 gauges per row

for idx, (area, score) in enumerate(scores.items()):
    col_idx = idx % 5
    with cols[col_idx]:
        # Create gauge chart (code from section B)
        area_name = area.split('/')[0]
        emoji = area_emojis.get(area_name, "")
        display_name = f"{emoji} {area_name}" if emoji else area_name

        # ... gauge code ...
```

**KEY DESIGN CHOICES:**
- **Height**: 270px (provides space for title and gauge)
- **Top margin**: 90px (spacing between title and gauge)
- **Bar thickness**: 0.7 (visible but not overwhelming)
- **Number size**: 36px (prominent, readable)
- **Background**: Transparent to blend with white box container
- **Delta reference**: 5 (midpoint, shows improvement/decline)

**WHY COLOR-CODED GAUGES WORK:**
1. **Instant feedback**: No need to read numbers to understand status
2. **Psychological impact**: Colors trigger emotional response (red = urgent, green = good)
3. **Scannable**: Easy to identify problem areas at a glance
4. **Contextual**: Same score (5) might be good for one area, concerning for another

---

## 11. TYPOGRAPHY

---

## 10. TYPOGRAPHY

```css
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

h3 {
    color: #667eea;
}
```

---

## 11. METRICS

```css
div[data-testid="stMetricValue"] {
    font-size: 2em;
    color: #667eea;
}
```

---

## 12. IMPLEMENTATION CHECKLIST

When implementing this design system:

1. ✅ Set background to `#f8f9fa` (not white!)
2. ✅ Use CSS `@layer streamlit-override` for tabs
3. ✅ Apply negative margins: `margin: 2rem -3rem 3rem -3rem`
4. ✅ Use `calc(100% + 6rem)` for width to match negative margins
5. ✅ Add pseudo-element `::before` for persistent background
6. ✅ Include JavaScript enforcement with `MutationObserver` + `setInterval`
7. ✅ Use `overflow: visible` on tab-list to prevent clipping
8. ✅ Apply `border-radius: 25px` to inputs for soft, rounded look
9. ✅ Use rgba colors with low opacity (0.3-0.6) for subtle gradients
10. ✅ Wrap all CSS in `st.markdown("""<style>...</style>""", unsafe_allow_html=True)`
11. ✅ Wrap JavaScript in `st.markdown("""<script>...</script>""", unsafe_allow_html=True)`
12. ✅ Remove all default tab underlines and borders
13. ✅ Add `z-index: 1` to tab buttons to prevent clipping

---

## 13. COMMON PITFALLS TO AVOID

❌ **Don't** use white background - white boxes won't be visible
❌ **Don't** rely only on CSS - Streamlit will override it
❌ **Don't** forget `!important` flags - they're critical for specificity
❌ **Don't** use sharp gradients - keep them soft with rgba and opacity
❌ **Don't** skip the JavaScript enforcement - styles will revert
❌ **Don't** use small border-radius (< 20px) if you want soft appearance
❌ **Don't** forget `box-sizing: border-box` on containers
❌ **Don't** forget to remove default tab borders/underlines - they create visual noise
❌ **Don't** use `overflow: hidden` on tab containers - it will clip rounded corners

---

## 14. COMPLETE IMPLEMENTATION TEMPLATE

```python
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Your App Name",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Base Styling */
    .main {
        background: #f8f9fa;
    }
    .stApp {
        background: #f8f9fa;
    }
    .block-container {
        padding-left: 3rem !important;
        padding-right: 3rem !important;
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
    }

    /* Typography */
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
    h3 {
        color: #667eea;
    }

    /* CSS Layer with highest priority */
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

    /* Multiple selectors for tab container */
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

    /* Pseudo-element background */
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

    /* Child divs */
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

    /* Animation trick */
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

    /* Tab List Container */
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

    /* Individual Tab Buttons */
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

    .stTabs [aria-selected="true"] * {
        color: white !important;
    }

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

    /* Remove tab underlines */
    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] {
        background-color: transparent !important;
        display: none !important;
    }

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

    /* Form Inputs */
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

    /* Buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 14px 32px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
        background: linear-gradient(135deg, #5568d3 0%, #6a3f91 100%) !important;
        transform: translateY(-2px) !important;
    }

    /* Metrics */
    div[data-testid="stMetricValue"] {
        font-size: 2em;
        color: #667eea;
    }
</style>
""", unsafe_allow_html=True)

# JavaScript Enforcement
st.markdown("""
<script>
    function forceTabPadding() {
        const tabs = document.querySelectorAll('[data-testid="stTabs"]');
        tabs.forEach(tab => {
            const styleStr = 'padding: 2rem 3rem 3rem 3rem !important; margin: 2rem -3rem 3rem -3rem !important; width: calc(100% + 6rem) !important; max-width: calc(100% + 6rem) !important; background: rgba(255, 255, 255, 0.98) !important; background-color: rgba(255, 255, 255, 0.98) !important; backdrop-filter: blur(10px) !important; border-radius: 25px !important; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07), 0 10px 15px rgba(0, 0, 0, 0.1), 0 20px 25px rgba(0, 0, 0, 0.08) !important; border: 1px solid rgba(0, 0, 0, 0.05) !important; position: relative !important; box-sizing: border-box !important;';

            tab.style.cssText += styleStr;
            tab.setAttribute('style', tab.getAttribute('style') + '; ' + styleStr);
        });
    }

    // Run immediately
    forceTabPadding();

    // MutationObserver
    const tabObserver = new MutationObserver(() => {
        forceTabPadding();
    });

    function observeTabs() {
        document.querySelectorAll('[data-testid="stTabs"]').forEach(tab => {
            tabObserver.observe(tab, {
                attributes: true,
                attributeFilter: ['style', 'class']
            });
        });
    }

    observeTabs();

    const mainObserver = new MutationObserver(() => {
        forceTabPadding();
        observeTabs();
    });

    mainObserver.observe(document.body, {
        childList: true,
        subtree: true
    });

    // Continuous enforcement
    setInterval(forceTabPadding, 50);

    // Event listeners
    document.addEventListener('click', () => setTimeout(forceTabPadding, 10));
    window.addEventListener('load', forceTabPadding);
</script>
""", unsafe_allow_html=True)

# Your App Content
st.title("🔮 Your App Title")

tab1, tab2, tab3 = st.tabs(["📊 Tab 1", "📈 Tab 2", "⚙️ Tab 3"])

with tab1:
    st.header("Tab 1 Content")
    st.text_input("Your Name", placeholder="Enter your name...")
    st.text_area("Description", placeholder="Enter description...")

with tab2:
    st.header("Tab 2 Content")

with tab3:
    st.header("Tab 3 Content")
```

---

## 15. SUMMARY

This design system achieves:
- ✨ Premium white-box aesthetic (Bearable-style)
- 🎨 Soft, rounded components (not harsh/squared)
- 💜 Gradient purple/violet accents
- 🔒 Persistent styling that survives Streamlit updates
- 📱 Glass-morphism effects with backdrop-blur
- 🎯 Triple-layer enforcement (CSS Layer + Multiple Selectors + JavaScript)

**The hardest part was making the white box container persist** - this requires the combination of CSS `@layer`, negative margins, pseudo-elements, animation keyframes, AND aggressive JavaScript enforcement with `MutationObserver` + `setInterval`. Don't skip any of these layers!

---

## 16. TROUBLESHOOTING

**Problem: White box not visible**
- Solution: Ensure background is `#f8f9fa`, not white

**Problem: Styles revert after page load**
- Solution: Verify JavaScript enforcement is running (check `setInterval` at 50ms)

**Problem: Tab buttons getting clipped**
- Solution: Add `overflow: visible` and `z-index: 1` to tab buttons

**Problem: Text inputs look too harsh/squared**
- Solution: Increase `border-radius` to 25px+ and use rgba gradients with low opacity

**Problem: Negative margins not working**
- Solution: Ensure parent has proper `box-sizing: border-box` and width is `calc(100% + 6rem)`

---

**Created from the Alquimia app design system - hard-won through extensive iteration and testing.**
