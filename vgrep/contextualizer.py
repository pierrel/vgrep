from vgrep.templater import Templater
from typing import Literal
from langchain_core.runnables import Runnable
from langgraph.graph import END, StateGraph, START
from pydantic import BaseModel
from typing import Generator
from functools import partial


def contextualize(input_gen: Generator[str],
                  contextualizing_llm: Runnable) -> str:
    graph = contextualize_graph(contextualizing_llm)
    res = graph.invoke({"context": "",
                        "to_contextualize": input_gen,
                        "done_contextualizing": False})
    return res['context']


class ContextState(BaseModel):
    context: str
    to_contextualize: Generator[str]
    done_contextualizing: bool


def contextualize_chunk(llm: Runnable,
                        state: ContextState) -> ContextState:
    """Contextualizing the next chunk of the `state`'s `to_contextualize`
    string and puts it into `state.context`

    """
    try:
        chunk = next(state.to_contextualize)
        templater = Templater()
        request = templater.render_template("contextualize.txt.j2",
                                            state=state,
                                            chunk=chunk)
        res = llm.invoke(request)
        state.context = res.content
    except StopIteration:
        state.done_contextualizing = True
    return state


def done_contextualizing(state: ContextState) -> Literal[END, "contextualize"]:
    """Decides whether contextualization should continue or if the
    graph should terminate

    """
    if state.done_contextualizing:
        return END
    else:
        return "contextualize"


def contextualize_graph(contextualizer: Runnable) -> StateGraph:
    """Returns a graph that can be invoked to contextualize a string"""
    contextualize_node = partial(contextualize_chunk, contextualizer)
    workflow = StateGraph(ContextState)
    workflow.add_node("contextualize", contextualize_node)
    workflow.add_edge(START, "contextualize")
    workflow.add_conditional_edges("contextualize",
                                   done_contextualizing)
    return workflow.compile()
