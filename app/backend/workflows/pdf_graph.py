from langgraph.graph import StateGraph, START, END
from app.backend.core.state import State
from app.backend.agents.pdf_agents.pdf_validation_agent import pdf_validation_agent
from app.backend.agents.pdf_agents.pdf_chunking_agent import pdf_chunking_agent

pdf_graph = StateGraph(State)

# Add node
pdf_graph.add_node("pdf_validation_agent", pdf_validation_agent)
pdf_graph.add_node("pdf_chunking_agent", pdf_chunking_agent)

# Correct edges (use string node names)
pdf_graph.add_edge(START, "pdf_validation_agent")
pdf_graph.add_edge("pdf_validation_agent", "pdf_chunking_agent")
pdf_graph.add_edge("pdf_chunking_agent", END)

# Compile (IMPORTANT)
pdf_graph = pdf_graph.compile()
