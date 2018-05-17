import pandas as pd
import os

# grammar is a pandas data frame used to store non-terminal symbols and their formulas.
grammar = pd.read_csv(os.path.join("data", "grammar.csv"), "r", delimiter='`', index_col=0)
# first_dict is a python dict used to store FIRST(a) array corresponding to one non-terminal symbol and formula.
# The dict's form is (non-terminal, formula) -> FIRST(a) list.
first_dict = dict()

# follow_dict is a python dict used to store FOLLOW(A) array.
# The dict's form is non-terminal -> FOLLOW(a) set.
follow_dict = dict()


def get_all_formulas(non_t):
    """
    Returns all formulas corresponding to the specified non-terminal symbol.

    :param non_t: string, the non-terminal symbol.
    :return: list or pandas Series, all formulas corresponding to the specified non-terminal symbol
    """
    formulas = grammar.loc[non_t]
    formulas = formulas["formula"]
    if type(formulas).__name__ == "str":
        # If there is only one formula corresponding to the non-terminal symbol,
        # the returned 'formulas' could be string object.
        # Considering we have to traverse 'formulas', we turn it to a list here.
        formulas = [formulas]
    return formulas


def construct_first():
    """
    Construct all non-terminal symbols and formulas' FIRST(a) array.
    """
    print("Constructing FIRST(a) array.")
    for non_t in grammar[~grammar.index.duplicated(keep='first')].index:
        get_first(non_t)


def construct_follow(start_symbol='S'):
    """
    Construct all non-terminal symbols' FOLLOW(A) array.

    :param start_symbol: string, the start symbol of the grammar.
    """
    print("Constructing FOLLOW(A) array.")
    for non_t in grammar[~grammar.index.duplicated(keep='first')].index:
        get_follow(non_t, start_symbol)


def get_first(non_t):
    """
    Get a non-terminal symbols' all FIRST(a) array.
    Insert every formula's FIRST(a) into first_dict in the same time.

    :param non_t: str, non-terminal symbol.
    :return: set, the non-terminal symbol's all FIRST(a) array.
    """
    # List 'first' is used to store the non-terminal symbol's all FIRST(a) array.
    first = set()
    for formula in get_all_formulas(non_t):
        # List 'formula_first' is used to store formula's FIRST(a) array.
        formula_first = set()
        first_sym = formula.split(" ")[0]
        if first_sym.isupper():
            # The first symbol of formula is an upper character, which means it is an non-terminal symbol.
            # In this case, we recursively search for corresponding FIRST(a) array.
            first |= get_first(first_sym)
            formula_first |= get_first(first_sym)
        else:
            # The first symbol is not an upper character, which means it is an terminal symbol.
            # In this case, we directory store the symbol into array.
            first.add(first_sym)
            formula_first.add(first_sym)
        # Insert formula's FIRST(a) into the dict.
        first_dict[(non_t, formula)] = formula_first
    return first


def get_follow(non_t, start_symbol='S'):
    """
    Get a non-terminal symbols' all FOLLOW(A) array.
    Insert every non-terminals' FOLLOW(A) array into follow_dict in the same time.

    :param non_t: str, non-terminal symbol.
    :param start_symbol: str, the start symbol of the grammar.
    :return: The non-terminal symbol's all FOLLOW(a) array.
    """
    follow = set()
    for non_terminal in grammar[~grammar.index.duplicated(keep='first')].index:
        for formula in get_all_formulas(non_terminal):
            formula_list = formula.split(" ")
            if non_t in formula_list:
                # The specified non-terminal symbol is in formula, then get the index of the symbol.
                index = formula_list.index(non_t)
                if not non_t == non_terminal:
                    if index == len(formula_list) - 1:
                        # If the symbol is in the end of the formula,
                        # then add all FOLLOW(A) to the symbol's FOLLOW set.
                        follow |= get_follow(non_terminal)
                    else:
                        if formula_list[index + 1].isupper():
                            # If the follow of the symbol is an non-terminal-symbol,
                            # add the follow symbol's FIRST(A) to its follow set.
                            follow |= get_first(formula_list[index + 1])
                            if 'e' in list(get_all_formulas(formula_list[index + 1])) \
                                    and index == len(formula_list) - 2:
                                # If the follow of the symbol is the end of the formula and can be inferred to empty,
                                # add the formula's corresponding non-terminal symbol's FOLLOW()
                                # to the symbol's FOLLOW set.
                                follow |= get_follow(non_terminal)
                        else:
                            # If the follow of the symbol is an terminal-symbol,
                            # directory add that symbol to its FOLLOW set.
                            follow.add(formula_list[index + 1])
    follow -= {'e'}
    if non_t == start_symbol:
        follow.add('#')
    follow_dict[non_t] = follow
    return follow


def construct_map():
    """
    Construct LL(1) analysis sheet and write into a csv file.
    """
    print("Constructing analysis map.")
    # Gather all terminal symbol that would appear in a valid sentence.
    all_terminal = set()
    for first in first_dict.values():
        all_terminal |= first
    for follow in follow_dict.values():
        all_terminal |= follow
    all_terminal -= {'e'}
    all_terminal = list(sorted(all_terminal))

    # Set the first row of analysis sheet (in python list form)
    an_matrix = [["non-t"] + all_terminal]
    for non_t in grammar[~grammar.index.duplicated(keep='first')].index:
        # Initialize every non-terminal symbol's sheet row with all items filled with None.
        row = [None] * len(all_terminal)
        for formula in get_all_formulas(non_t):
            if formula == 'e':
                # If the formula leads to empty, add this formula to all terminal-symbols in FOLLOW(A).
                for single_follow in follow_dict[non_t]:
                    row[all_terminal.index(single_follow)] = formula
            else:
                # Add this formula to all terminal-symbols in FIRST(formula).
                for single_first in first_dict[(non_t, formula)]:
                    row[all_terminal.index(single_first)] = formula
        an_matrix.append([non_t] + row)

    # Write analysis sheet into csv file, using pandas.
    an_df = pd.DataFrame(an_matrix[1:], columns=an_matrix[0])
    an_df = an_df.set_index(["non-t"])
    an_df.to_csv(os.path.join("data", "an_map.csv"), sep='`')


if __name__ == "__main__":
    construct_first()
    construct_follow()
    construct_map()
