import streamlit as st
import streamlit.components.v1 as components
import json, os
from streamlit_autorefresh import st_autorefresh

# Define o arquivo de dados compartilhado
DATA_FILE = "game_data.json"

# Se o arquivo não existir, cria-o com a estrutura inicial
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"discovered": []}, f, ensure_ascii=False)

# Funções para ler e atualizar o arquivo
def read_game_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def update_game_data(new_data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False)

# Lista completa de nodos (palabras) – la central y las demás
all_possible_nodes = [
    {"id": "SÍNTESIS", "fixed": True},
    {"id": "integración"},
    {"id": "simplificar"},
    {"id": "resumen"},
    {"id": "reducción"},
    {"id": "guión"},
    {"id": "recopilación"},
    {"id": "compendio"},
    {"id": "acortamiento"},
    {"id": "extracto"},
    {"id": "sinopsis"},
    {"id": "compilación"},
    {"id": "sumario"}
]

# Actualiza la lista de nodos según las palabras descubiertas
game_data = read_game_data()
updated_nodes = []
for node in all_possible_nodes:
    node_copy = dict(node)
    if node_copy["id"].lower() == "sintesis":
        node_copy["discovered"] = True
    else:
        node_copy["discovered"] = (node_copy["id"].lower() in game_data["discovered"])
    updated_nodes.append(node_copy)

nodes_data = json.dumps(updated_nodes)

# Detecta la vista a partir de la query string (por defecto, "mobile")
params = st.experimental_get_query_params()
view = params.get("view", ["mobile"])[0]

# ----- MODO MOBILE: Formulario para enviar respuestas -----
if view == "mobile":
    st.set_page_config(page_title="Juego - Móvil", layout="centered")
    st.title("Juego de Adivinanza de Palabras (Móvil)")
    st.write("Ingresá tu nombre y adiviná las palabras.")

    name = st.text_input("Poné tu nombre:")
    guess = st.text_input("Escribí una palabra:")

    if st.button("Enviar respuesta"):
        if not name:
            st.error("¡Por favor, ingresá tu nombre!")
        else:
            valid_words = [node["id"].lower() for node in all_possible_nodes if node["id"].lower() != "sintesis"]
            if guess.lower() in valid_words:
                data = read_game_data()
                if guess.lower() not in data["discovered"]:
                    data["discovered"].append(guess.lower())
                    update_game_data(data)
                    st.success(f"¡Buenísimo, {name}! Adivinaste '{guess}'.")
                else:
                    st.warning(f"¡La palabra '{guess}' ya fue descubierta!")
            else:
                st.error(f"'{guess}' no es una palabra válida.")
    st.write("Podés ver la proyección en otra pantalla:")
    st.markdown("[Ver Proyección](?view=display)")

# ----- MODO DISPLAY: Visualización interactiva -----
else:
    st.set_page_config(page_title="Juego - Proyección", layout="wide")
    st.title("Visualización del Juego")
    st.write("Esta es la pantalla de proyección. Se actualiza en tiempo real.")

    # Auto-refresca la pantalla cada 2 segundos para leer las actualizaciones
    st_autorefresh(interval=2000, key="display_autorefresh")

    # Código HTML/JS con D3.js para la simulación interactiva
    html_code = f"""
    <html>
      <head>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <style>
          body {{ margin: 0; overflow: hidden; background-color: #f7f7f7; }}
          svg {{ width: 100%; height: 100%; }}
          text {{
              font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
              pointer-events: none;
              fill: #333;
          }}
        </style>
      </head>
      <body>
        <svg></svg>
        <script>
          const width = 1200;
          const height = 900;

          let nodes = {nodes_data};

          // Para el nodo central ("SÍNTESIS"), fijarlo en el centro
          nodes = nodes.map(d => {{
            if(d.id === "SÍNTESIS") {{
              d.fx = width / 2;
              d.fy = height / 2;
              d.central = true;
            }} else {{
              d.central = false;
            }}
            return d;
          }});

          const svg = d3.select("svg")
            .attr("viewBox", [0, 0, width, height]);

          // Crear la simulación con fuerzas
          const simulation = d3.forceSimulation(nodes)
              .force("charge", d3.forceManyBody().strength(-200))
              .force("center", d3.forceCenter(width / 2, height / 2))
              .force("collision", d3.forceCollide().radius(d => {{
                  if(d.central || d.discovered) {{
                     return (d.id.length * 10) + 10;
                  }} else {{
                     return 0;
                  }}
              }}))
              .force("x", d3.forceX(width / 2).strength(0.05))
              .force("y", d3.forceY(height / 2).strength(0.05))
              .on("tick", ticked);

          const node = svg.selectAll("g")
            .data(nodes)
            .join("g")
            .call(d3.drag()
              .on("start", dragstarted)
              .on("drag", dragged)
              .on("end", dragended));

          // Dibujar círculos:
          // - Nodo central: radio fijo y color rojo suave.
          // - Nodos descubiertos: radio proporcional al largo del texto.
          // - Nodos no descubiertos: radio 0 (invisibles).
          node.append("circle")
              .attr("r", d => d.central ? 60 : (d.discovered ? d.id.length * 5 : 0))
              .attr("fill", d => d.central ? "#ff6961" : (d.discovered ? "#77dd77" : "none"))
              .attr("stroke", "#555")
              .attr("stroke-width", 2);

          // Agregar texto centrado solo para nodos centrales o descubiertos.
          node.append("text")
              .attr("dy", 4)
              .attr("text-anchor", "middle")
              .text(d => (d.central || d.discovered) ? d.id : "");

          function ticked() {{
            node.attr("transform", function(d) {{
                let r = d.central ? 60 : (d.discovered ? d.id.length * 5 : 0);
                if(r === 0) r = 5;
                // Limitar la posición para que no se salgan del canvas
                d.x = Math.max(r, Math.min(width - r, d.x));
                d.y = Math.max(r, Math.min(height - r, d.y));
                return "translate(" + d.x + "," + d.y + ")";
            }});
          }}

          function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            if (!d.central) {{
              d.fx = d.x;
              d.fy = d.y;
            }}
          }}

          function dragged(event, d) {{
            if (!d.central) {{
              d.fx = event.x;
              d.fy = event.y;
            }}
          }}

          function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            if (!d.central) {{
              d.fx = null;
              d.fy = null;
            }}
          }}
        </script>
      </body>
    </html>
    """
    st.subheader("Simulación Force-Directed")
    components.html(html_code, width=1200, height=900)
    st.write("Link para ingresar respuestas: [Ver Móvil](?view=mobile)")
