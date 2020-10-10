import re

def space_after_slash(s):
    return re.sub(r"\/([^\s])", r"/ \1", s)

def space_before_slash(s):
    return re.sub(r"([^\s])\/", r"\1 /", s)

def space_after_period(s):
    return re.sub(r"\.([^\s])", r". \1", s)

def no_space_before_period(s):
    return re.sub(r"\s\.", r".", s)

def normalize(s):
    s = space_after_period(s)
    s = no_space_before_period(s)
    s = space_after_slash(s)
    s = space_before_slash(s)
    return s

def __main__():
    txt = "The. rain.in Spain done . a/b a /b a/ b"
    expected = "The. rain. in Spain done. a / b a / b a / b"

    processed = normalize(txt)
    print processed
    print processed == expected
