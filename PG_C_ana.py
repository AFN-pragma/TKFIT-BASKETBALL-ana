import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Arc, Circle, Polygon

# Configuration de la page
st.set_page_config(page_title="TKFIT Basketball Analytics", layout="wide", page_icon="")
# Appliquer les styles CSS personnalisés
st.markdown(
    """
    <style>
    /* Couleur de fond globale */
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    
    /* Couleur de la sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffc107 !important;
    }
    
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Dashboard TKFIT Performance")
st.subheader("Real-time analysis of biomechanical and physiological data")

# Génération de données simulées pour les basketteurs
def generate_player_data(position, has_breaks):
    np.random.seed(42)
    total_minutes = 48
    total_seconds = total_minutes * 60
    timestamps = [datetime(2023, 10, 15, 19, 0) + timedelta(seconds=x) for x in range(total_seconds)]
    
    # Paramètres spécifiques par position
    if position == "Pivot":
        base_heart_rate = np.random.randint(85, 95)
        base_muscle = np.random.randint(30, 40)
        intensity_factor = 0.7
    else:  # Meneur
        base_heart_rate = np.random.randint(95, 105)
        base_muscle = np.random.randint(40, 50)
        intensity_factor = 0.9
    
    # Création des données
    data = {
        "timestamp": timestamps,
        "vitesse": np.zeros(total_seconds),
        "acceleration": np.zeros(total_seconds),
        "heart_rate": np.zeros(total_seconds),
        "muscle_activity": np.zeros(total_seconds),
        "position_x": np.zeros(total_seconds),
        "position_y": np.zeros(total_seconds)
    }
    
    # Simulation des actions pendant le match
    for second in range(total_seconds):
        # Périodes de repos pour le pivot
        if position == "Pivot" and has_breaks and ((1200 < second < 1380) or (2100 < second < 2280)):
            data['vitesse'][second] = np.random.uniform(0, 1)
            data['acceleration'][second] = np.random.uniform(0, 0.5)
            data['heart_rate'][second] = np.random.randint(65, 75)
            data['muscle_activity'][second] = np.random.randint(5, 10)
        else:
            # Actions de jeu
            action = second % 120
            if action < 30:  # Sprint
                data['vitesse'][second] = np.random.uniform(15, 20) * intensity_factor
                data['acceleration'][second] = np.random.uniform(5, 8)
            elif action < 60:  # Déplacement rapide
                data['vitesse'][second] = np.random.uniform(8, 12)
                data['acceleration'][second] = np.random.uniform(2, 4)
            elif action < 90:  # Marche
                data['vitesse'][second] = np.random.uniform(3, 6)
                data['acceleration'][second] = np.random.uniform(1, 2)
            else:  # Position défensive
                data['vitesse'][second] = np.random.uniform(0.5, 2)
                data['acceleration'][second] = np.random.uniform(0.2, 1)
            
            data['heart_rate'][second] = base_heart_rate + np.random.randint(-5, 15)
            data['muscle_activity'][second] = base_muscle + np.random.randint(0, 20)
        
        # Position sur le terrain (coordonnées normalisées)
        if position == "Pivot":
            data['position_x'][second] = np.random.uniform(0.6, 0.9)
            data['position_y'][second] = np.random.uniform(0.4, 0.6)
        else:  # Meneur
            data['position_x'][second] = np.random.uniform(0.2, 0.8)
            data['position_y'][second] = np.random.uniform(0.2, 0.8)
    
    return pd.DataFrame(data)

# Génération des datasets
pivot_df = generate_player_data("Pivot", has_breaks=True)
guard_df = generate_player_data("Meneur", has_breaks=False)

# Sidebar - Sélection du joueur
st.sidebar.image("TKFIT LOGO.jpg")
st.sidebar.header("Paramètres d'analyse")
player_type = st.sidebar.radio("Sélection du Joueur", ("Pivot", "Meneur (Issokojo)"))
selected_df = pivot_df if player_type == "Pivot" else guard_df

# Calcul des périodes de repos
if player_type == "Pivot":
    rest_periods = [
        {"start": 1200, "end": 1380, "duration": "3 min"},
        {"start": 2100, "end": 2280, "duration": "3 min"}
    ]
else:
    rest_periods = []

# Métriques clés
st.header("📈 Performance metrics")
col1, col2, col3, col4 = st.columns(4)

avg_speed = selected_df['vitesse'].mean()
max_speed = selected_df['vitesse'].max()
col1.metric("Vitesse Moyenne", f"{avg_speed:.1f} km/h", f"{max_speed:.1f} km/h max")

avg_heart = selected_df['heart_rate'].mean()
max_heart = selected_df['heart_rate'].max()
col2.metric("Fréquence Cardiaque", f"{avg_heart:.0f} bpm", f"{max_heart:.0f} bpm max")

avg_muscle = selected_df['muscle_activity'].mean()
max_muscle = selected_df['muscle_activity'].max()
col3.metric("Activité Musculaire", f"{avg_muscle:.1f}%", f"{max_muscle:.1f}% max")

distance = (selected_df['vitesse'].sum() / 3600) * 1000  # km to meters
col4.metric("Distance Parcourue", f"{distance:.0f} m")

# Visualisations
st.header("📊 Analyse temporelle")
tab1, tab2, tab3 = st.tabs(["Physiologie", "Mouvement", "Musculaire"])

with tab1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=selected_df['timestamp'], 
        y=selected_df['heart_rate'], 
        name="Fréquence cardiaque",
        line=dict(color='firebrick', width=2)
    ))
    
    # Ajout des périodes de repos pour le pivot
    if player_type == "Pivot":
        for period in rest_periods:
            start_time = selected_df['timestamp'].iloc[period['start']]
            end_time = selected_df['timestamp'].iloc[period['end']]
            fig.add_vrect(
                x0=start_time, x1=end_time,
                fillcolor="lightgreen", opacity=0.5,
                layer="below", line_width=0,
                annotation_text="Repos", annotation_position="top left"
            )
    
    fig.update_layout(
        title="Fréquence cardiaque et périodes de repos",
        yaxis_title="FC (bpm)",
        xaxis_title="Temps",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=selected_df['timestamp'], 
        y=selected_df['vitesse'], 
        name="Vitesse",
        line=dict(color='royalblue', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=selected_df['timestamp'], 
        y=selected_df['acceleration'], 
        name="Accélération",
        yaxis="y2",
        line=dict(color='darkorange', width=2, dash='dot')
    ))
    
    fig.update_layout(
        title="Vitesse et Accélération",
        yaxis=dict(title="Vitesse (km/h)"),
        yaxis2=dict(title="Accélération (m/s²)", overlaying="y", side="right"),
        xaxis_title="Temps",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=selected_df['timestamp'], 
        y=selected_df['muscle_activity'], 
        name="Activité musculaire",
        fill='tozeroy',
        fillcolor='rgba(100, 200, 100, 0.2)',
        line=dict(color='green', width=2)
    ))
    
    # Ajout des pics d'activité
    peaks = selected_df[selected_df['muscle_activity'] > selected_df['muscle_activity'].quantile(0.9)]
    fig.add_trace(go.Scatter(
        x=peaks['timestamp'],
        y=peaks['muscle_activity'],
        mode='markers',
        marker=dict(color='red', size=6),
        name='Pics d\'activité'
    ))
    
    fig.update_layout(
        title="Activité musculaire des quadriceps",
        yaxis_title="Intensité (%)",
        xaxis_title="Temps",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

# Carte du terrain avec positionnement
st.header("🏀 Positionnement sur le terrain")

def draw_realistic_court(ax):
    # Dimensions du terrain NBA (en pieds convertis en unités arbitraires)
    court_length = 94
    court_width = 50
    
    # Couleur de fond orange bois
    court_color = '#FFA500'  # Orange vif
    line_color = 'white'
    
    # Dessiner le terrain principal
    ax.add_patch(Rectangle((0, 0), court_length, court_width, 
                         facecolor=court_color, edgecolor=line_color, linewidth=2))
    
    # Zone restrictive (peint)
    restricted_area = Rectangle((0, 17), 19, 16, 
                              facecolor='#8B4513',  # Marron bois
                              edgecolor=line_color, linewidth=1)
    ax.add_patch(restricted_area)
    
    # Zone restrictive opposée
    restricted_area2 = Rectangle((court_length-19, 17), 19, 16, 
                               facecolor='#8B4513', 
                               edgecolor=line_color, linewidth=1)
    ax.add_patch(restricted_area2)
    
    # Ligne médiane
    ax.add_line(plt.Line2D([court_length/2, court_length/2], [0, court_width], 
                         color=line_color, linewidth=2))
    
    # Cercle central
    center_circle = Circle((court_length/2, court_width/2), 6, 
                         fill=False, edgecolor=line_color, linewidth=2)
    ax.add_patch(center_circle)
    
    # Panier (cercle + support)
    basket_rim = Circle((5.25, court_width/2), 0.75, 
                      fill=False, edgecolor='red', linewidth=2)
    basket_support = Rectangle((4.5, court_width/2-0.5), 1.5, 1, 
                             facecolor='silver', edgecolor='gray')
    ax.add_patch(basket_support)
    ax.add_patch(basket_rim)
    
    # Panier opposé
    basket_rim2 = Circle((court_length-5.25, court_width/2), 0.75, 
                       fill=False, edgecolor='red', linewidth=2)
    basket_support2 = Rectangle((court_length-6, court_width/2-0.5), 1.5, 1, 
                              facecolor='silver', edgecolor='gray')
    ax.add_patch(basket_support2)
    ax.add_patch(basket_rim2)
    
    # Ligne des 3 points
    three_point_line = Arc((5.25, court_width/2), 47, 47, 
                         theta1=0, theta2=180, 
                         edgecolor=line_color, linewidth=2)
    ax.add_patch(three_point_line)
    
    three_point_line2 = Arc((court_length-5.25, court_width/2), 47, 47, 
                          theta1=0, theta2=-180, 
                          edgecolor=line_color, linewidth=2)
    ax.add_patch(three_point_line2)
    
    # Zone de la raquette (peint)
    key_area = Polygon([[0, 17], [19, 17], [19, 33], [0, 33]], 
                     closed=True, facecolor='#8B4513', edgecolor=line_color)
    ax.add_patch(key_area)
    
    key_area2 = Polygon([[court_length, 17], [court_length-19, 17], 
                      [court_length-19, 33], [court_length, 33]], 
                     closed=True, facecolor='#8B4513', edgecolor=line_color)
    ax.add_patch(key_area2)
    
    # Configuration finale
    ax.set_xlim(0, court_length)
    ax.set_ylim(0, court_width)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Ajouter du texte
    ax.text(court_length/2, court_width/2, "CERCLE CENTRAL", 
           ha='center', va='center', fontsize=8, color='white')
    ax.text(10, court_width/2, "RAQUETTE", 
           ha='center', va='center', fontsize=10, color='white', rotation=90)
    ax.text(court_length-10, court_width/2, "RAQUETTE", 
           ha='center', va='center', fontsize=10, color='white', rotation=-90)
    
    return ax

# Créer la visualisation
fig, ax = plt.subplots(figsize=(10, 6))
draw_realistic_court(ax)

# Convertir les coordonnées normalisées en coordonnées terrain
court_length = 94
court_width = 50
x_pos = selected_df['position_x'] * court_length
y_pos = selected_df['position_y'] * court_width

# Ajouter la trajectoire du joueur
scatter = ax.scatter(x_pos[::30], y_pos[::30], 
           c=selected_df['muscle_activity'][::30], 
           s=50, cmap='viridis', alpha=0.8,
           edgecolors='black', linewidth=0.5,
           label='Position')

# Ajouter les zones spécifiques au poste
if player_type == "Pivot":
    # Zone de pivot (raquette)
    pivot_zone = Rectangle((0, 17), 19, 16, 
                         fill=True, alpha=0.3, color='red')
    ax.add_patch(pivot_zone)
    ax.text(10, court_width/2, "ZONE PIVOT", 
            ha='center', va='center', fontsize=12, color='red', rotation=90)
else:
    # Zone de meneur (périphérie)
    guard_zone = Rectangle((court_length/2-15, 0), 30, court_width, 
                         fill=True, alpha=0.2, color='blue')
    ax.add_patch(guard_zone)
    ax.text(court_length/2, court_width/2, "ZONE MENEUR", 
            ha='center', va='center', fontsize=12, color='blue')

plt.title(f"Positionnement du {player_type} - Intensité musculaire", fontsize=14, weight='bold')
cbar = plt.colorbar(scatter, ax=ax, label='Intensité musculaire (%)')
cbar.ax.yaxis.label.set_font_properties({'weight': 'bold'})
st.pyplot(fig)

# Comparaison des deux joueurs
st.header("🆚 Comparaison Pivot vs Meneur")

# Calcul des métriques comparatives
metrics = {
    "Vitesse Moy (km/h)": [pivot_df['vitesse'].mean(), guard_df['vitesse'].mean()],
    "FC Moy (bpm)": [pivot_df['heart_rate'].mean(), guard_df['heart_rate'].mean()],
    "Activité Musc Moy (%)": [pivot_df['muscle_activity'].mean(), guard_df['muscle_activity'].mean()],
    "Distance (m)": [
        (pivot_df['vitesse'].sum() / 3600) * 1000,
        (guard_df['vitesse'].sum() / 3600) * 1000
    ]
}

comparison_df = pd.DataFrame(metrics, index=["Pivot", "Meneur"]).T

fig = px.bar(comparison_df, barmode='group', 
             labels={'value': 'Valeur', 'variable': 'Joueur'},
             title="Comparaison des performances",
             color_discrete_sequence=['#FF8C00', '#4169E1'])
st.plotly_chart(fig, use_container_width=True)

# Analyse des différences
st.subheader("Analyse des différences de performance")
st.markdown("""
- **Pivot**: 
  - Plus forte activité musculaire dans la raquette
  - Périodes de récupération nécessaires
  - Distance parcourue moindre mais intensité locale élevée
  
- **Meneur**:
  - Vitesse moyenne plus élevée
  - Endurance cardiovasculaire supérieure
  - Couverture de terrain plus importante
""")

# Recommandations spécifiques
st.header("💡 Recommandations d'entraînement")

if player_type == "Pivot":
    col1, col2 = st.columns(2)
    with col1:
        st.info("""
        **Entraînement physique:**
        - Sprints courts répétés (5x10m)
        - Travail de puissance dans la raquette
        - Renforcement des membres inférieurs
        - Exercices de saut vertical
        """)
    with col2:
        st.info("""
        **Récupération:**
        - Cryothérapie post-match
        - Protéines: 30g dans les 30min
        - Étirements ciblés quadriceps
        - Massage des tissus profonds
        """)
    st.progress(0.65, text="Intensité d'entraînement recommandée: 65%")
else:
    col1, col2 = st.columns(2)
    with col1:
        st.info("""
        **Entraînement physique:**
        - Endurance à haute intensité
        - Changements de rythme répétés
        - Dribble avec résistance
        - Exercices de coordination
        """)
    with col2:
        st.info("""
        **Développement technique:**
        - Prise de décision rapide
        - Passe précise sous fatigue
        - Tir en mouvement
        - Lecture du jeu
        """)
    st.progress(0.85, text="Intensité d'entraînement recommandée: 85%")

# Téléchargement des données
st.sidebar.header("Export des données")
if st.sidebar.button("Télécharger données CSV"):
    csv = selected_df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="Exporter CSV",
        data=csv,
        file_name=f"tekfit_{player_type}_data.csv",
        mime='text/csv'
    )


# Pied de page
st.caption("Données collectées par le boitier TKFIT | 2025 Basketball Analytics")
