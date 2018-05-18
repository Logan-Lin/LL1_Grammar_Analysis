import AnMapConstruct
import LLGrammarAn
import os


if __name__ == "__main__":
    AnMapConstruct.print_grammar()
    AnMapConstruct.construct_first()
    AnMapConstruct.construct_follow()
    AnMapConstruct.construct_map()

    for root, directories, filenames in os.walk("test"):
        for filename in sorted(filenames):
            name, ext = os.path.splitext(filename)
            if ext == ".txt":
                LLGrammarAn.scan_file(os.path.join(root, filename))
            print()
