
from sentence_splitter import SentenceSplitter 

from typing import List 

# split_into_sentences is intended to be a generic splitting funciton 
# which wraps sentence_splitter or whatever other internal parsing / splitting 
# logic (from nltk in the future, maybe?) we choose to use. 
def split_into_sentences(txt: str) -> List[str]: 
    splitter = SentenceSplitter(language="en") 
    no_newlines = txt.replace('\n', ' ') 
    return splitter.split(no_newlines) 
