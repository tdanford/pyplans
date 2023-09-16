
from plans.parsing import split_into_sentences

txt = """This is some text.  Some of it
crosses line boundaries.  How well "does it do
to figure out," where things are, "Mr. Python?"
I truly don't know! But we'll figure it out.
"""

def test_split_paragraph(): 
    assert len(split_into_sentences(txt)) == 5 