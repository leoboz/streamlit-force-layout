import streamlit as st
import streamlit.components.v1 as components
import json

# --- Lógica do Jogo e Dados dos Nós ---
# Para este exemplo, vamos manter uma lista estática.
# Em seu jogo, você poderá atualizar essa lista conforme as palavras são descobertas.
nodes = [
    {"id": "SYNTHESIS", "fixed": True},
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

# Aqui, você pode modificar os nós para marcar quais palavras foram descobertas,
# por exemplo, adicionando uma propriedade "discovered": True ou alterando a cor.

nodes_data = json.dumps(nodes)

# --- Código HTML/JS com D3.js ---
html_code = f"""
<html>
  <head>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
      body {{ margin: 0; overflow: hidden; }}
      svg {{ width: 100%; height: 100%; }}
      text {{ font-family: sans-serif; pointer-events: none; }}
    </style>
  </head>
  <body>
    <svg></svg>
    <script>
      const width = 1200;
      const height = 900;

      // Dados dos nós
      let nodes = {nodes_data};

      // Para o nó central (SYNTHESIS), fixa sua posição no centro
      nodes = nodes.map(d => {{
        if(d.id === "SYNTHESIS") {{
          d.fx = width / 2;
          d.fy = height / 2;
          d.central = true;
        }} else {{
          d.central = false;
        }}
        return d;
      }});

      // Seleciona o SVG e configura o viewBox
      const svg = d3.select("svg")
        .attr("viewBox", [0, 0, width, height]);

      // Cria a simulação de forças
      const simulation = d3.forceSimulation(nodes)
          .force("charge", d3.forceManyBody().strength(-200))
          .force("center", d3.forceCenter(width / 2, height / 2))
          .force("collision", d3.forceCollide().radius(d => (d.id.length * 10) + 10))
          .on("tick", ticked);

      // Cria grupos para cada nó
      const node = svg.selectAll("g")
        .data(nodes)
        .join("g")
        .call(d3.drag()
          .on("start", dragstarted)
          .on("drag", dragged)
          .on("end", dragended));

      // Adiciona um círculo para cada nó
      node.append("circle")
          .attr("r", d => d.central ? 60 : d.id.length * 5)
          .attr("fill", d => d.central ? "red" : "lightgray")
          .attr("stroke", "black");

      // Adiciona o texto centralizado
      node.append("text")
          .attr("dy", 4)
          .attr("text-anchor", "middle")
          .text(d => d.id);

      // Função de atualização da simulação
      function ticked() {{
        node.attr("transform", d => "translate(" + d.x + "," + d.y + ")");
      }}

      // Funções para drag (arrastar os nós)
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

# --- Exibir o Componente no Streamlit ---
st.title("Simulação Force-Directed com D3.js")
st.write("A palavra central (SYNTHESIS) está fixa e os outros nós se organizam ao redor.")

components.html(html_code, width=1200, height=900)
