import argparse
import colorama
import re
import itertools

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
    if eliminated:
        noped_regex = "[^"+eliminated+"]"
    else:
        noped_regex = "."
    indices = [i for i,c in enumerate(base) if c == "."]    
    base = list(base)
    res = []
    for choice in itertools.combinations(indices, len(somewhere)):
        this = base[:]
        for i, c in enumerate(choice):
            this[c] = somewhere[i]
        res.append("".join(this))
    return "^("+"|".join(res).replace(".",noped_regex)+")$"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="/usr/share/dict/words")

    parsers = parser.add_subparsers(dest='cmd')
    perms = parsers.add_parser("using")
    perms.add_argument("charset")
    perms.add_argument("--min", type=int, default=0)
    perms.add_argument("--must")
    srch = parsers.add_parser("search")
    srch.add_argument("regex")
    srch.add_argument("--contains", "-c", action="store_true")
    srch = parsers.add_parser("wordle")
    srch.add_argument("base")
    srch.add_argument("--eliminated", "-e", default="")
    srch.add_argument("--somewhere", "-s", default="")
    options = parser.parse_args()

    with open(options.source) as srcfile:
        words = srcfile.read().split()

    if options.cmd == "using":
        for r in construct_from_perms(words,
                    options.charset,
                    minimum=options.min,
                    must=options.must):
            print(r)
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
        for word in words:
            if re.match(regex, word):
                print(word)
        

if __name__ == "__main__":
    main()
