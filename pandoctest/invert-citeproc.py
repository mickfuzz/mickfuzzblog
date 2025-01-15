#!/bin/env python
# -*- coding: utf-8 -*-
'''

Due to changes made towards pandoc2, at the moment mostly only the inversion of (some) citations and re-wrapping of lines into somewhat semantic units.
I previously had some pandoc filters that also converted track changes to CriticMarkup, could accept or reject them, and merged comments to footnotes or html comments;
due to the change in pandoc filters they don't work at the moment, so that functionality is not used for now (but it is implemented in the script).

Usage:

`pandoc -s test.md --bibliography library.bib -M link-citations -t docx -o test.docx`

`pandoc -s test.docx --wrap=none --track-changes=all --atx-headers --reference-location=section -t markdown | ./invert-citeproc.py > test.rev.md`

**Note:** With earlier versions of pandoc, the script was able to read diacritics from the references section.
As empty anchors seem to be stripped by now, this is not possible anymore, and references are currently ignored.
It added a pipe in between which pulled lines starting with `[]{#ref-}` to the front, that then would be read in the following postprocessor pipe.
The usage to revert back to markdown used to be as follows:

`pandoc -s test.docx --wrap=none --track-changes=all --atx-headers --reference-location=section -t markdown  | python -c 'import sys; sys.stdout.writelines(sorted(sys.stdin.readlines(), key=lambda x: not x.startswith("[]{#ref-")))' | ./invert-citeproc.py > test.rev.md`

**Caveats:**

* diacritics don't work as of now, as the name is guessed from the citekey
* some citation styles may not work
* there are contractions when using page references, which vary by CSL used

'''


import sys
import re
import os

mode = "accept"
# mode = "reject"
# mode = "all"

commentMode = 'after-line'
# commentMode = 'remove'
# commentMode = 'after-line'
# removeHighlightThreshold = 0.9 # TODO not yet implemented
commentPrefix = '@CMT:' if not 'COMMENTATOR' in os.environ else '@{}:'.format(os.environ['COMMENTATOR'])

global commentid
commentid = 0

global citationMap
citationMap = {}

global failedCitations
failedCitations = []


def splitSemantics(matchobj):
    return re.sub(
        r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<! [A-Z]\.)(?!\n)(?<=[.?!;:])\s",
        "\n",
        matchobj.group(0)
        )


def moveComment(matchobj, line):
    global commentMode
    global commentPrefix
    if commentMode == 'footnote':
        global commentid
        cmt = '[^cmt-' + str(commentid) + ']'
        commentid += 1
        comments.append(cmt + ': ' + re.sub(' (¶ )+', '\n', matchobj.group(3)))
        return matchobj.group(1) + cmt + matchobj.group(5)

    elif commentMode == 'after-line':
        highlight = re.search(r'({==|^)((?:(?!(?:==}|{==)).)*?)==}{>>' + matchobj.group(3)[:5], line, re.M)

        rtrn = matchobj.group(1) + matchobj.group(5)

        this_line = ''

        if not highlight:
            cmt = '<!-- {} [ERROR] {}-->'.format(commentPrefix, matchobj.group(3))
        else:
            is_inline = highlight.group(1) == '{=='

            len_highlight = len(highlight.group(2)) + 6
            len_paragraph = len(line) - len(matchobj.group(3))
            this_line = [l for l in line.split('\n') if highlight.group(0) in l][0]
            len_this_line = len(this_line) - len(matchobj.group(3))

            if (not highlight) or len_highlight > 1.0 * len_this_line:
                highlight = '[PARAGRAPH] '
                # WON'T WORK
            elif len_highlight > len_this_line * 0.70:
                highlight = '[LINE] '
            else:
                highlight = highlight.group(2)
            highlight = '>>' + highlight + '<< ' if len(highlight.strip()) > 0 and highlight[0] != '[' else highlight
            cmt = '<!-- ' + commentPrefix + ' ' + highlight + re.sub(' (¶ )+', '\n', matchobj.group(3)) + ' -->'

        if this_line and this_line.startswith('==}'):
            rtrn = cmt + '\n' + rtrn
        else:
            rtrn = rtrn + '\n' + cmt
#                comments.append(cmt)
        return rtrn


def recreateCitation(matchobj):
    # 1: preface [if 2 = (]
    # 2: ( or ;
    # 3: in bracket preface [if any]
    # 4: year
    # 5: citation key
    # 6: page number, etc [if any]
    # 7: closing bracket [if any]

    citekey = matchobj.group(5)
    if citekey in citationMap:
        author = citationMap[citekey]
    else:
        author = re.sub('[0-9]+.*', '', citekey).capitalize()
        # TODO note that guessing

    def removeAuthor(author, string):
        if author in string:
            return(string.split(author, 1)[0])
        else:
            return(string)

    citation = ''
    nobracket = True
    if matchobj.group(2) in [';', ',']:
        if matchobj.group(1) != '':
            raise ValueError('Regex Mistake in `' + matchobj.group(0) + '`')
        citation = '; '
        nobracket = False
    else:
        citation = removeAuthor(author, matchobj.group(1))
        if author not in matchobj.group(1):
            citation += '['
            nobracket = False

    citation += removeAuthor(author, matchobj.group(3))
    citation += '@' + citekey
    citation += matchobj.group(6)
    if matchobj.group(7) == ')' and not nobracket:
        citation += ']'

    return citation


def rememberCitation(matchobj):
    global citationMap
    citationMap[matchobj.group(1)] = matchobj.group(2)
    if re.search(r"(\{[+\-=>]{2}|[<+\-=]{2}\})", matchobj.group(0)) is not None:
        failedCitations.append(matchobj.group(0))
    return ''


def processLine(line):
    global comments
    comments = []

    line = re.sub(
                r"\\--",
                "--",
                line
    )

    # remove references
    line = re.sub(
                r"\[\]{#ref-([^ ]+) .anchor}\W*([A-Za-z]+)?(?:(?!(?:\n\n.|\[\^.)).)*",
                rememberCitation,
                line
    )

    # line = re.sub(
    #            r"^(#.*){#.*}$",
    #            "\1",
    #            line
    # )
    line = re.sub(
                r"{>>author:[^<]+<<}",
                "",
                line
    )
    if mode == "accept":
        line = re.sub(
                    r"({--(?:(?!--}).)*--}|{\+\+|\+\+})",
                    "",
                    line
        )
        # replace paragraph breaks
        line = re.sub(
                r"\[\]{.paragraph-insertion [^}]*}",
                "\n\n",
                line
        )
    elif mode == "reject":
        line = re.sub(
                    r"({\+\+(?:(?!\+\+}).)*\+\+}|{--|--})",
                    "",
                    line
        )

        # replace paragraph breaks
        line = re.sub(
                r"\[\]{.paragraph-insertion [^}]*}",
                "",
                line
        )
    if commentMode == "remove":
        line = re.sub(
                    r"({>>(?:(?!<<}).)*<<}|{==|==})",
                    "",
                    line
        )

    line = re.sub(
                # r"\(.*?, \[[0-9]{4}[a-z]?\]\(#ref-([^)]+?(?:[0-9]{4})?[^)]*?)\)(, [^)]+)?\)",
                r"(?:((?:[\w,-_;.&]+ ){,6})([\(;,]))([^\(]*?(?:{==)?)\[([([0-9]{4}[a-z]?)\](?:\(\\l\)\[a\])?\(#ref-([\w_-]+)\)(.*?)((?:{==.*==})?\)|(?=;)|(?=, \[))",
                recreateCitation,
                line
    )

    line = re.sub(
                r"((?:^|[+\-<]{2}}|\]|\))(.*?)(?:\[|\(|{[+\->]{2}|$))",
                splitSemantics,
                line
    )
    while True:
        oldline = line[:]
        line = re.sub(
            r"(==})({>>)(.*?)(<<})(.*)(?=\n)",
            lambda x: moveComment(x, line),
            line
        )
        if oldline == line:
            break

    # line = re.sub(
    #            r"[A-Z][a-z]+(?:(?:,| &| and|) \w+)+ \(\[[0-9]{4}[a-z]?\]\(#ref-((?:[^)0-9]+?)(?:[0-9]{4})?[^)0-9]*?)\)(?:, ([^)]+))?\)",
    #            "@\1\2",
    #            line
    # )

    # fix italics
    line = re.sub(r"(?<=\W)\*(\S+(?:\s+[^*\s]+)*?)\*(?=\W)", r"_\1_", line)
    ## TODO doesn't work with BOLD!! i.e. bold needs to be protected
    # fix empty additions
    line = re.sub(r" +{\+\+ +\+\+}", " ", line)
    # remove highlights
    if commentMode == 'after-line':
        line = re.sub(r"({==|==})", "", line)
    # fix empty space before punctuation
    line = re.sub(r" (?=[.;:,])", "", line)
    # fix extra whitespace
    line = re.sub(r" +", " ", line)
    # fix em-dashes
    line = re.sub(r"---", "—", line)
    # fix empty lines
    line = re.sub(r"\n{2,}", "\n\n", line)
    # add line break before 2nd level heading
    line = re.sub(r"##", "\n##", line)
    # fix escaped brackets
    line = re.sub(r"\\\[", "[", line)
    line = re.sub(r"\\\]", "]", line)
    # fix protected spaces
    line = re.sub(r"[\u202F\u00A0]", " ", line)
    # fix page numbers
    line = re.sub(r"(?<=p\.)\s(?=\d)", "", line)
    line = re.sub(r"\((p\.\d+)\)", r"[\1]", line)
    # remove header ids
    line = re.sub(r"(?<=^)(#.*) {#.*$", r"\1", line)
    # fix footnotes
    line = re.sub(r"^(\[\^\w+\]:)\n", r"\1 ", line)
    # failed comments
    line = re.sub(r"{>>", "<!-- {} [START] -->".format(commentPrefix), line)
    line = re.sub(r"<<}", "<!-- {} [END] -->".format(commentPrefix), line)
    line = re.sub(r"(\S)\s*(<!--)", r"\1\n\2", line)
    line = re.sub(r"(-->)\s*(\S)", r"\1\n\2", line)
    if len(comments) > 0:
        emptylines = '\n' if commentMode == 'footnote' else ''
        line = line + emptylines + '\n'.join(comments) + emptylines + '\n'
    return line


if __name__ == "__main__":
    empty = False
    for line in sys.stdin:
        line = processLine(line)
        if len(line.strip()) == 0:
            if empty:
                continue
            else:
                empty = True
        else:
            empty = False
        # sys.stderr.write("DEBUG: got line: " + line)
        sys.stdout.write(line)
    if len(failedCitations) > 0:
        sys.stdout.writelines(['\n', '<!--NOTES IN THE CITATIONS-->\n<!--\n'])
        sys.stdout.writelines('\n'.join(failedCitations))
        sys.stdout.writelines(['\n-->\n'])
