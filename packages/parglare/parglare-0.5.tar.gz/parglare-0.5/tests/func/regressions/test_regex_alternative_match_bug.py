from parglare import Grammar, GLRParser


def test_regex_alternative_match_bug():
    """
    """

    grammar = """
    A: "Begin" /=|EQ/ "End";
    """
    g = Grammar.from_string(grammar)
    parser = GLRParser(g)
    parser.parse('Begin EQ End')
