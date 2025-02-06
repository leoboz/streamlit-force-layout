import streamlit as st
import streamlit.components.v1 as components
import json, os
from streamlit_autorefresh import st_autorefresh

# Define o caminho do arquivo de dados
DATA_FILE = "game_data.json"
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"discovered": []}, f, ensure_ascii=False)

def read_game_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Lista completa de nós (palavras)
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

# Atualiza os nós com base nas palavras descobertas
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

st.set_page_config(page_title="Jogo - Projeção", layout="wide")
st.title("Projeção do Jogo")
st.write("Esta é a tela de projeção. Ela se atualiza em tempo real.")

# Auto-refresca a tela a cada 2 segundos
st_autorefresh(interval=2000, key="display_autorefresh")

# Código HTML/JS com D3.js para a simulação interativa
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
      // Fixa o nó central ("SÍNTESIS") no centro
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
      node.append("circle")
          .attr("r", d => d.central ? 60 : (d.discovered ? d.id.length * 5 : 0))
          .attr("fill", d => d.central ? "#ff6961" : (d.discovered ? "#77dd77" : "none"))
          .attr("stroke", "#555")
          .attr("stroke-width", 2);
      node.append("text")
          .attr("dy", 4)
          .attr("text-anchor", "middle")
          .text(d => (d.central || d.discovered) ? d.id : "");
      function ticked() {{
        node.attr("transform", function(d) {{
            let r = d.central ? 60 : (d.discovered ? d.id.length * 5 : 0);
            if(r === 0) r = 5;
            // Garantir que os nós permaneçam dentro do canvas
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

components.html(html_code, width=1200, height=900)
st.markdown('<br><a href="https://seu-app-mobile.streamlit.app" target="_self">Ver Mobile</a>', unsafe_allow_html=True)
