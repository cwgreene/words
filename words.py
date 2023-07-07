import argparse

# using
def construct_from_perms(words, charset, minimum=0, must=None):
    s = set(charset)
    res = []
    for word in words:
        if set(word).issubset(s) and len(word) >= minimum:
            if not must or must in word:
                res.append(word)
    return res

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="/usr/share/dict/words")

    parsers = parser.add_subparsers(dest='cmd')
    perms = parsers.add_parser("using")
    perms.add_argument("charset")
    perms.add_argument("--min", type=int, default=0)
    perms.add_argument("--must")
    options = parser.parse_args()

    with open(options.source) as srcfile:
        words = srcfile.read().split()

    if options.cmd == "using":
        for r in construct_from_perms(words,
                    options.charset,
                    minimum=options.min,
                    must=options.must):
            print(r)

if __name__ == "__main__":
    main()
