import streamlit as st
import streamlit.components.v1 as components
import json

# Configura o Streamlit
st.set_page_config(page_title="Word Guessing Game", layout="wide")

# Lista completa de nós (palavras) – a palavra central e as demais
all_possible_nodes = [
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

# Inicializa o estado da sessão para guardar as palavras descobertas
if "discovered" not in st.session_state:
    st.session_state["discovered"] = []

# --- Interface de Interação com o Usuário ---
st.title("Word Guessing Game")
st.write("Tente adivinhar as palavras ao redor da palavra central.")

# Input do nome do usuário
name = st.text_input("Digite seu nome:")

# Input para o palpite
guess = st.text_input("Digite uma palavra:")

if st.button("Enviar Palpite"):
    if not name:
        st.error("Por favor, informe seu nome!")
    else:
        # Cria uma lista com as palavras válidas (exceto a central)
        valid_words = [node["id"].lower() for node in all_possible_nodes if node["id"].lower() != "synthesis"]
        if guess.lower() in valid_words:
            if guess.lower() not in st.session_state["discovered"]:
                st.session_state["discovered"].append(guess.lower())
                st.success(f"Parabéns {name}! Você descobriu '{guess}'.")
            else:
                st.warning(f"A palavra '{guess}' já foi descoberta!")
        else:
            st.error(f"'{guess}' não é uma palavra válida.")

# --- Atualiza a lista de nós com base nas palavras descobertas ---
updated_nodes = []
for node in all_possible_nodes:
    node_copy = dict(node)
    # A palavra central (SYNTHESIS) sempre é considerada descoberta
    if node_copy["id"].lower() == "synthesis":
        node_copy["discovered"] = True
    else:
        node_copy["discovered"] = (node_copy["id"].lower() in st.session_state["discovered"])
    updated_nodes.append(node_copy)

nodes_data = json.dumps(updated_nodes)

# --- Código HTML/JS com D3.js para a Simulação ---
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

      // Cria a simulação de forças:
      // - forceManyBody: repulsão entre os nós.
      // - forceCenter: centraliza os nós.
      // - forceCollide: evita que os nós se toquem.
      const simulation = d3.forceSimulation(nodes)
          .force("charge", d3.forceManyBody().strength(-200))
          .force("center", d3.forceCenter(width / 2, height / 2))
          .force("collision", d3.forceCollide().radius(d => {{
              // Se o nó é descoberto ou é central, usa um raio baseado no comprimento do texto; caso contrário, retorna 0 (invisível)
              if(d.central || d.discovered) {{
                 return (d.id.length * 10) + 10;
              }} else {{
                 return 0;
              }}
          }}))
          .on("tick", ticked);

      // Cria grupos para cada nó
      const node = svg.selectAll("g")
        .data(nodes)
        .join("g")
        .call(d3.drag()
          .on("start", dragstarted)
          .on("drag", dragged)
          .on("end", dragended));

      // Adiciona um círculo para cada nó:
      // - Nó central: círculo de raio fixo e cor vermelha.
      // - Nó descoberto: círculo com raio proporcional ao tamanho do texto.
      // - Nó não descoberto: não desenha (raio 0 e fill "none").
      node.append("circle")
          .attr("r", d => d.central ? 60 : (d.discovered ? d.id.length * 5 : 0))
          .attr("fill", d => d.central ? "red" : (d.discovered ? "lightgray" : "none"))
          .attr("stroke", "black");

      // Adiciona o texto, mas só exibe se o nó for central ou descoberto.
      node.append("text")
          .attr("dy", 4)
          .attr("text-anchor", "middle")
          .text(d => (d.central || d.discovered) ? d.id : "");

      // Função chamada a cada tick da simulação.
      function ticked() {{
        node.attr("transform", d => "translate(" + d.x + "," + d.y + ")");
      }}

      // Funções para permitir arrastar os nós (exceto o central)
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

st.subheader("Simulação Force-Directed")
components.html(html_code, width=1200, height=900)
