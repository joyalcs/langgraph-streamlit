from langgraph.graph import StateGraph, START, END
from app.backend.core.state import PdfState
from app.backend.agents.pdf_agents.pdf_validation_agent import pdf_validation_agent

pdf_graph =  StateGraph(PdfState)

pdf_graph.add_node("pdf_validation_agent", pdf_validation_agent)

pdf_graph.add_edge(START, pdf_validation_agent)
pdf_graph.add_edge(pdf_validation_agent, END)

