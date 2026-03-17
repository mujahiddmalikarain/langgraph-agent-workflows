from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class State(TypedDict):    # shared memory for all agents
    message: str


def mock_llm(state: State) -> State:   # agent function
        # Print current memory
    print("Current state:", state) 
    return {"message": "Hello, world!"}

graph = StateGraph(State) # graph object

graph.add_node("mock_llm",mock_llm) # add agent node to graph
graph.add_edge(START, "mock_llm") # add edge from start to agent
graph.add_edge("mock_llm", END) # add edge from agent to end

compiled = graph.compile() # compile graph

result = compiled.invoke({"message": "Hello, world!"}) # invoke graph

print(result) # print result




