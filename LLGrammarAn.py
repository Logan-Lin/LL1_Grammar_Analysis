import pandas as pd
import os


an_map = pd.read_csv(os.path.join("data", "an_map.csv"), "r", delimiter='`', index_col=0)
coding_df = pd.read_csv(os.path.join("data", "coding.csv"), "r", delimiter=' ', index_col=0)


def process_binary(bin_str):
    """
    Turn binary string such as (20, -) into coding integer.

    :param bin_str: string, binary string output by lexical analysis, like '(20, -)'.
    :return: Extracted coding integer, like 20.
    """
    return int(bin_str[1:].split(",")[0])


def get_current_description(column="secondary"):
    """
    Return current description based on current coding.

    :param column: string, Set the column to search for. Set to 'description' to search from original column.
    :raise: ValueError if can't find description based on current coding
    :return: string, Description (identifier) current coding represented
    """
    coding = coding_array[scan_index]
    desc = coding_df.loc[coding][column]
    if not type(desc).__name__ == "str":
        raise ValueError("No valid identifier matching coding {}".format(coding))
    return desc


def load_coding(file_name):
    """
    Load lexical analysis's output into coding array.

    :param file_name: string, output file's directory
    """
    global coding_array
    coding_array = []
    with open(file_name, "r") as file:
        for row in file.readlines():
            if len(row) > 2:
                # If the row is not empty
                row_coding = list(map(process_binary, row.split(")")[:-1]))
                coding_array += row_coding
    # Append the end symbol to the end of coding series.
    coding_array.append(52)


def control(start_function):
    """
    The main control function of LL(1) analysis.

    :param start_function: str, the start function of LL(1) grammar.
    """
    stack = ['#', start_function]
    global scan_index
    scan_index = 0

    while True:
        # Pop out top of the stack and get current scanning symbol from input series.
        stack_top = stack[-1]
        current = get_current_description()
        print('[{0:20}]<-{1:}'.format(" ".join(stack), current))
        del stack[-1]

        if not stack_top.isupper():
            # The top of the stack is not an upper character, which means it is a terminal symbol.
            if stack_top == current:
                if current == '#':
                    # If the scanned symbol is end symbol, the process can end and the result is true.
                    return
                scan_index += 1
            else:
                # If the scanned input symbol not matching with stack top, there is an error in input series.
                raise ValueError("Terminal symbol not matching, input '{}', stack top '{}'".format(current, stack_top))
        else:
            formula = an_map.loc[stack_top, current]
            if not type(formula).__name__ == "str":
                # If there is no matching formula in the analysis map, there is an error in input series.
                raise ValueError("No matching formula with non-terminal "
                                 "symbol '{}' and terminal symbol '{}'".format(stack_top, current))
            if not formula == 'e':
                # Using reversed list to simulate the push of stack.
                formula_array = list(reversed(formula.split(" ")))
                stack += formula_array


def scan_file(file_name):
    """
    Scan the input binary series from file and check if it is valid.

    :param file_name: string, the file storing binary series outputted from lexical analysis
    """
    load_coding(file_name)
    print("====Validating file {}====".format(file_name))
    try:
        control("S")
        print("Input file {} valid".format(file_name))
    except (ValueError, KeyError) as e:
        print("Input file {} not valid, error at {}. \nDetail: {}".format(file_name, scan_index, e))


if __name__ == "__main__":
    for root, directories, filenames in os.walk("test"):
        for filename in sorted(filenames):
            name, ext = os.path.splitext(filename)
            if ext == ".txt":
                scan_file(os.path.join(root, filename))
            print()
