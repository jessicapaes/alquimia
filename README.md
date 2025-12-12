# 🔮 ALQUIMIA - Year 7 Vision App

Interactive app for year-end reflection (2025) and vision planning (2026) with Roda da Vida, SMART Goals, Archetypes, and Numerology.

**Alquimia** = The art of transformation. Turning your life experiences into wisdom, your pain into power, your vision into reality.

## 🚀 Quick Start with Cursor

1. **Open this folder in Cursor**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the app:**
   ```bash
   streamlit run alquimia.py
   ```

## 📱 Features

### 🎯 Roda da Vida 2025
- Interactive sliders to rate 10 life areas (0-10)
- Beautiful radar chart visualization
- Reflection questions for each area
- Calculate average life satisfaction score

### 🔮 Arquétipos Femininos
- Focus on Sorceress/Feiticeira as primary archetype
- Rate 9 feminine archetypes presence in your life
- Reflection prompts about archetypal work
- Connection to Eva app as magical creation

### 🌟 Vision Board 2026
- 8 key life areas with keywords and affirmations
- Text areas to write intentions for each area
- Aligned with Personal Year 7 energy (Nov 2025-Nov 2026)
- Transition to Year 8 in November 2026

### 📋 SMART Goals 2026
- Create Specific, Measurable, Achievable, Relevant, Time-bound goals
- Link each goal to a life area
- Connect goals to archetypal energy
- Track completion status
- Delete goals as needed

### 📊 Dashboard
- Overview metrics (average score, total goals, completion rate)
- Visual charts comparing life areas
- Goals distribution by area
- Export data as JSON or CSV

## 🎨 Customization in Cursor

### Colors & Styling
The app uses a mystical purple gradient theme. To customize:

1. **Change gradient colors** (line 15-20):
   ```python
   background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
   ```

2. **Modify accent colors**:
   - Primary: `#a8edea` (cyan)
   - Secondary: `#fed6e3` (pink)
   - White overlays: `rgba(255, 255, 255, 0.1)`

### Adding New Features

**Add a new life area to Roda da Vida:**
```python
st.session_state.roda_scores = {
    # ... existing areas ...
    'Nova Área/New Area': 5,
}
```

**Add new archetype:**
```python
archetypes = {
    # ... existing archetypes ...
    "🆕 New Archetype": "Description and keywords",
}
```

**Add new vision area:**
```python
vision_areas = {
    # ... existing areas ...
    "🆕 Nova Área": {
        "keywords": ["keyword1", "keyword2"],
        "affirmation": "Your affirmation here."
    }
}
```

## 💾 Data Persistence

Currently, data is stored in Streamlit session state (temporary). To add persistence:

### Option 1: Local JSON file
```python
import json

# Save
with open('my_vision_data.json', 'w') as f:
    json.dump(export_data, f)

# Load
with open('my_vision_data.json', 'r') as f:
    data = json.load(f)
```

### Option 2: Browser localStorage (using streamlit-javascript)
```bash
pip install streamlit-javascript
```

### Option 3: Database (SQLite, PostgreSQL)
For more permanent storage across sessions

## 🔮 Personal Year Numerology

**Current Period (Nov 5, 2025 - Nov 4, 2026): Year 7**
- Spirituality, introspection, inner wisdom
- Perfect for Eva development and personal transformation

**Next Period (Nov 5, 2026 - Nov 4, 2027): Year 8**
- Power, abundance, manifestation, business success
- Perfect for Eva launch and scaling

## 📝 Notes

- All text is bilingual (Portuguese/English)
- Designed for personal use by Jessica
- Birth info: November 5, 1989, 4:40 PM, Brasília
- Sun: Scorpio ♏ | Moon: Cancer ♋ | Rising: Aries ♈

## 🎯 To-Do in Cursor

1. [ ] Test all interactive elements
2. [ ] Customize colors to your preference
3. [ ] Add more reflection prompts
4. [ ] Implement data persistence
5. [ ] Add image upload for vision board
6. [ ] Create monthly check-in feature
7. [ ] Add PDF export with charts
8. [ ] Integrate with Eva app goals

## 🐛 Troubleshooting

**App won't start:**
```bash
# Make sure streamlit is installed
pip install streamlit

# Check Python version (needs 3.8+)
python --version
```

**Charts not showing:**
```bash
# Reinstall plotly
pip install --upgrade plotly
```

**Styling issues:**
```bash
# Clear Streamlit cache
streamlit cache clear
```

## ✨ Have fun creating your 2026 vision!

Remember: You're the Sorceress creating your reality 🔮
