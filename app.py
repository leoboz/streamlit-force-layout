import streamlit as st
import streamlit.components.v1 as components
import json

st.set_page_config(page_title="Juego de Adivinanza de Palabras", layout="wide")

# Lista completa de nodos (palabras) – la palabra central y las demás
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

# Inicializa el estado de sesión para guardar las palabras descubiertas
if "discovered" not in st.session_state:
    st.session_state["discovered"] = []

st.title("Juego de Adivinanza de Palabras")
st.write("Intentá adivinar las palabras que rodean la palabra central.")

# Entrada de nombre del usuario
name = st.text_input("Poné tu nombre:")

# Entrada para la palabra
guess = st.text_input("Escribí una palabra:")

if st.button("Enviar respuesta"):
    if not name:
        st.error("¡Por favor, ingresá tu nombre!")
    else:
        # Lista de palabras válidas (excluyendo la central)
        valid_words = [node["id"].lower() for node in all_possible_nodes if node["id"].lower() != "sintesis"]
        if guess.lower() in valid_words:
            if guess.lower() not in st.session_state["discovered"]:
                st.session_state["discovered"].append(guess.lower())
                st.success(f"¡Buenísimo, {name}! Adivinaste '{guess}'.")
            else:
                st.warning(f"¡La palabra '{guess}' ya fue descubierta!")
        else:
            st.error(f"'{guess}' no es una palabra válida.")

# Actualiza la lista de nodos según las palabras descubiertas
updated_nodes = []
for node in all_possible_nodes:
    node_copy = dict(node)
    if node_copy["id"].lower() == "sintesis":
        node_copy["discovered"] = True
    else:
        node_copy["discovered"] = (node_copy["id"].lower() in st.session_state["discovered"])
    updated_nodes.append(node_copy)

nodes_data = json.dumps(updated_nodes)

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

      // Datos de los nodos
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
      // - Nodo central: círculo de radio fijo y color rojo suave.
      // - Nodos descubiertos: círculo con radio proporcional al largo del texto.
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
            // Clampea la posición para que los nodos se mantengan dentro de los límites
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
