from langgraph.graph import StateGraph, END
from langgraph.pregel import Pregel
from typing import Literal
from graph.state import GraphState
from graph.nodes import GraphNodes

class GraphWorkflow:
    """
    This class is responsible for building and compiling the
    LangGraph "assembly line."

    It takes the "stations" (GraphNodes) and "wires" them together.
    """
    
    def __init__(self, 
                 nodes: GraphNodes
    ):
        self.nodes = nodes

    def _should_continue(self, 
                         state: GraphState
    ) -> Literal["continue", "end"]:
        """
        Private method for our conditional edge. It checks the state
        and decides the next step.
        
        """
        if state.get("error"):
            # If 'load_pdf' failed, skip 'extract_data'
            print(f"--- ! Error in 'load_pdf': {state['error']} ---")
            return "end"
        else:
            return "continue"

    def build(self) -> Pregel:
        """
        Assembles all the nodes and edges and compiles the graph.
        
        Returns:
            A compiled LangGraph app (Pregel).
        
        """
        workflow = StateGraph(GraphState)

        # Add the node functions from our 'nodes' object
        workflow.add_node("load_pdf", self.nodes.load_pdf)
        workflow.add_node("extract_data", self.nodes.extract_data)
        workflow.add_node("finalize_result", self.nodes.finalize_result)

        # Set the entry point
        workflow.set_entry_point("load_pdf")

        # Add the routing logic (the "edges")
        workflow.add_conditional_edges(
            "load_pdf",
            self._should_continue,
            {
                "continue": "extract_data",
                "end": "finalize_result"
            }
        )
        
        workflow.add_edge("extract_data", "finalize_result")
        workflow.add_edge("finalize_result", END)

        return workflow.compile()