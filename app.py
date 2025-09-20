from flask import Flask, render_template, jsonify, request
import json
import os

# --- Configuración Inicial ---
app = Flask(__name__)

# --- Rutas de la Aplicación ---

@app.route('/')
def index():
    """
    Página principal que muestra una lista de partidos (simulada).
    En una aplicación real, aquí se cargarían los partidos del día.
    """
    # Simulación de datos de partidos para la demo
    partidos_demo = [
        {'id': '2826192', 'time': '15:00', 'home': 'Equipo Local A', 'away': 'Equipo Visitante A', 'handicap': '-0.5', 'goals': '2.75'},
        {'id': '1234567', 'time': '17:30', 'home': 'Equipo Local B', 'away': 'Equipo Visitante B', 'handicap': '+0.25', 'goals': '2.5'},
        {'id': '7654321', 'time': '20:00', 'home': 'Equipo Local C', 'away': 'Equipo Visitante C', 'handicap': '0.0', 'goals': '3.0'},
    ]
    return render_template('index.html', partidos=partidos_demo)

@app.route('/analizar', methods=['GET', 'POST'])
def analizar_partido_page():
    """
    Página para solicitar el análisis de un partido por su ID.
    """
    if request.method == 'POST':
        match_id = request.form.get('match_id')
        # Aquí iría la lógica para llamar a los scrapers con el match_id
        # Por ahora, simplemente redirigimos a una página de estudio de ejemplo
        return render_template('estudio.html', match_id=match_id, datos_analisis="Análisis para el partido " + match_id)
    
    return render_template('analizar_partido.html')

@app.route('/test_preview')
def test_preview_page():
    """
    Sirve la página de test para la vista previa que hemos modificado.
    """
    return render_template('test_preview.html')

# --- API Endpoints ---

@app.route('/api/preview/<string:match_id>')
def get_preview_data(match_id):
    """
    API endpoint para la vista previa rápida.
    Devuelve datos simulados en formato JSON.
    Aquí es donde la lógica de "Ordenes_jefe.txt" tiene su efecto.
    """
    # Simulación de datos de la API
    data = {
        "home_team": f"Local-{match_id[:3]}",
        "away_team": f"Visitante-{match_id[3:]}",
        "handicap": {
            "ah_line": "-0.25",
            "favorite": f"Local-{match_id[:3]}",
            "cover_on_last_h2h": "CUBIERTO" # Este dato ya no se usa en el frontend
        },
        "recent_form": {
            "home": {"wins": 3, "total": 5},
            "away": {"wins": 2, "total": 5}
        },
        "h2h_stats": { # Esta sección entera ya no se muestra en la vista previa
            "home_wins": 4,
            "away_wins": 2,
            "draws": 2
        }
    }
    return jsonify(data)

# --- Punto de Entrada ---

if __name__ == '__main__':
    # El puerto 5001 se usa para evitar conflictos con otros servicios
    app.run(debug=True, port=5001)