import argparse
import colorama
import re
import itertools

import z3
from z3ext import contained_in
from z3ext.strings import String

# using
def construct_from_perms(words, charset, minimum=0, must=None):
    s = set(charset)
    res = []
    for word in words:
        if set(word).issubset(s) and len(word) >= minimum:
            if not must:
                res.append(word)
            elif must in word:
                res.append(word.replace(must,colorama.Fore.YELLOW + must + colorama.Fore.RESET))
    return res

def wordle_regex(base : str, somewhere : str, eliminated : str):
    noped_regex = "[^'"+eliminated+"]"
    indices = [i for i,c in enumerate(base) if c == "."]    
    base = list(base)
    res = []
    for choice in itertools.combinations(indices, len(somewhere)):
        for p in (itertools.permutations(choice)):
            this = base[:]
            for i, c in enumerate(p):
                this[c] = somewhere[i]
            res.append("".join(this))
    return "^("+"|".join(res).replace(".",noped_regex)+")$"

def pretty_print_keyword(words, sln):
    longest = 0
    indices = [] 
    for word in words:
        index = word.index(".")
        if index > longest:
            longest = index
        indices.append(index)
    # buffer + index = constant
    # => buffer + index = longest
    # buffer = longest - index
    for i, (word, index) in enumerate(zip(words, indices)):
        prefix, suffix = word.split(".")
        buffer = " "*(longest - index)
        fmt_string = buffer + (colorama.Style.BRIGHT +
                        prefix + 
                      colorama.Fore.BLUE +
                        sln[i] + 
                      colorama.Fore.WHITE + 
                        suffix +
                      colorama.Style.NORMAL)
        print(fmt_string)


def solve_keyword(words, dictionary):
    # Get list of possible words.
    matches = []
    for w in words:
        index = w.index(".")
        this_matches = set()
        for d in dictionary:
            if re.match("^"+w+"$", d):
                if "'" not in d:
                    this_matches.add((d,d[index]))
        matches.append(this_matches)
    print(matches)
    char_opts = [[c for w,c in matches_group]
        for matches_group in matches]
    regex = "".join(["("+"|".join(chars)+")" for chars in char_opts])

    for d in dictionary:
        if re.match(regex, d):
            word = d
            break   
    print(colorama.Fore.GREEN + word + colorama.Fore.WHITE)
    pretty_print_keyword(words,  word)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="/usr/share/dict/words")

    parsers = parser.add_subparsers(dest='cmd')
    perms = parsers.add_parser("using", help="words using a specified charset")
    perms.add_argument("charset", help="words must use this charset")
    perms.add_argument("--min", type=int, default=0, help="minimum length of word")
    perms.add_argument("--must", help="these letters *must* be used")

    srch = parsers.add_parser("search", help="search dictionary using regex")
    srch.add_argument("regex", help="regex to match on")
    srch.add_argument("--contains", "-c", action="store_true", help="allow match to be subset of word")

    keyword = parsers.add_parser("keyword", help="solve keyword problem")
    keyword.add_argument("cluewords", nargs="+", help="keywords of form 'KEYWOR.'")

    wordle = parsers.add_parser("wordle", help="Find words that match wordle clues")
    wordle.add_argument("base", help="base string. Use '.' to indicate unfilled positions. Example: 'a..te'")
    wordle.add_argument("--eliminated", "-e", default="", help="specify letters that appear nowhere")
    wordle.add_argument("--somewhere", "-s", default="", help="specify letters that must appear somewhere")
    wordle.add_argument("--debug", "-d", action="store_true", help="Print regex as well")
    wordle.add_argument("--regex", "-r", action="store_true", help="Print regex and exit")
    wordle.add_argument("--nocolor", "-c", action="store_true", help="no color")

    options = parser.parse_args()

    with open(options.source) as srcfile:
        words = srcfile.read().split()

    if options.cmd == "using":
        for r in construct_from_perms(words,
                    options.charset,
                    minimum=options.min,
                    must=options.must):
            print(r)
    if options.cmd == "keyword":
        solve_keyword(options.cluewords, words)
    if options.cmd == "search":
        if not options.contains:
            options.regex = "^"+options.regex+"$"
        for word in words:
            if re.match(options.regex, word):
                print(word)
    if options.cmd == "wordle":
        regex = wordle_regex(options.base,
            options.somewhere,
            options.eliminated)
        if options.debug or options.regex:
            print(regex)
        if options.regex:
            return
        for word in words:
            if re.match(regex, word):
                pretty = ""
                for i,c in enumerate(word):
                    if options.nocolor:
                        pretty += c
                    elif c == options.base[i]:
                        pretty += colorama.Fore.GREEN + c + colorama.Fore.RESET
                    elif c in options.somewhere:
                        pretty += colorama.Fore.YELLOW + c + colorama.Fore.RESET
                    else:
                        pretty += c
                print(pretty)

if __name__ == "__main__":
    main()
