
from plans import Steps, Action
from typing import List 

from .splitting import split_into_sentences 

def parse_paragraph_sentences_to_steps(name: str, paragraph: str) -> Steps: 
    sentences: List[str] = split_into_sentences(paragraph)
    actions: List[Action] = [Action(s) for s in sentences]
    return Steps(
        name, *actions
    )