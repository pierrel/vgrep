# This is the beginning of a summarization class or module that takes
# a string and summarizes it. It loops through the input string in
# chunks of max tokens (of the given llm)
from vgrep.templater import Templater
from typing import Literal
from langchain_core.runnables import Runnable
from langgraph.graph import END, StateGraph, START
from pydantic import BaseModel
from typing import Generator
from functools import partial


def summarize(input_gen: Generator[str],
              summarizing_llm: Runnable) -> str:
    graph = summarize_graph(summarizing_llm)
    res = graph.invoke({"summary": "",
                        "to_summarize": input_gen,
                        "done_summarizing": False})
    return res['summary']


class SummaryState(BaseModel):
    summary: str
    to_summarize: Generator[str]
    done_summarizing: bool


def summarize_chunk(llm: Runnable,
                    state: SummaryState) -> SummaryState:
    """Summarizes the next chunk of the `state`'s `to_summarize`
    string and puts it into `state.summary`, moving
    `state.current_index` by `chunk_size` amount.

    """
    try:
        chunk = next(state.to_summarize)
        templater = Templater()
        request = templater.render_template("summarize.txt.j2",
                                            state=state,
                                            chunk=chunk)
        res = llm.invoke(request)
        state.summary = res.content
    except StopIteration:
        state.done_summarizing = True
    return state


def done_summarizing(state: SummaryState) -> Literal[END, "summarize"]:
    """Decides whether summarization should continue or if the graph
    should terminate

    """
    if state.done_summarizing:
        return END
    else:
        return "summarize"


def summarize_graph(summarizer: Runnable) -> StateGraph:
    """Returns a graph that can be invoked to summarize a string"""
    summarize_node = partial(summarize_chunk, summarizer)
    workflow = StateGraph(SummaryState)
    workflow.add_node("summarize", summarize_node)
    workflow.add_edge(START, "summarize")
    workflow.add_conditional_edges("summarize",
                                   done_summarizing)
    return workflow.compile()


# FOR TESTING
from langchain_ollama import ChatOllama
chunks = ["Designing Instagram is one of the most common system design interview questions asked not just at Meta, but across all FAANG and FAANG-adjacent companies. It has a lot of similarities with our breakdowns of FB News Feed and Dropbox, but given the popularity and demand, we decided this warranted its own breakdown.",
          "If you're someone who often struggles to come up with your non-functional requirements, take a look at this list of common non-functional requirements that should be considered. Just remember, most systems are all these things (fault tolerant, scalable, etc) but your goal is to identify the unique characteristics that make this system challenging or unique.",
          "Before defining your non-functional requirements in an interview, it's wise to inquire about the scale of the system as this will have a meaningful impact on your design. In this case, we'll be looking at a system with 500M DAU with 100M posts per day."]
state = SummaryState(summary="",
                     to_summarize=(x for x in chunks),
                     done_summarizing=False)
# END FOR TESTING
