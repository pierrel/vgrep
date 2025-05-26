from vgrep.templater import Templater
from langchain_core.runnables import Runnable
from typing import Generator


def contextualize(input_gen: Generator[str],
                  contextualizing_llm: Runnable) -> str:
    templater = Templater("contextualize.txt.j2")
    context = ""

    for chunk in input_gen:
        request = templater.render_template(context=context,
                                            chunk=chunk)
        res = contextualizing_llm.invoke(request)
        context = res.content
        
    return context
