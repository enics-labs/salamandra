# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

import re


class Lexer(object):
    def __init__(self, tokens, flags=re.MULTILINE):
        self.tokens = {}
        # preprocess the state definitions to pattern, action and new_state
        for state, patterns in tokens.items():
            self.tokens[state] = []
            for p in patterns:
                pat = re.compile(p[0], flags)
                action = p[1]
                new_state = p[2] if len(p) > 2 else None
                # convert pop to an integer
                if new_state and new_state.startswith('#pop'):
                    if len(new_state.split(':')) > 1:
                        new_state = -int(new_state.split(':')[1])
                    else:
                        new_state = -1

                self.tokens[state].append((pat, action, new_state))

    def run(self, text, start='root'):
        # run lexer on text with the tokens, and yield the matches
        stack = [start]
        patterns = self.tokens[stack[-1]]
        pos = 0

        while True:
            for pat, action, new_state in patterns:
                m = pat.match(text, pos)
                if m:
                    if action:
                        yield (pos, m.end() - 1), action, m.groups()
                    pos = m.end()  # new position
                    if new_state:  # change to new state
                        if isinstance(new_state, int):  # pop states
                            del stack[new_state:]
                        else:
                            stack.append(new_state)
                        patterns = self.tokens[stack[-1]]  # update to new state

                    break  # found a match so break and do again

            else:  # can't match anything in patterns so advance position by 1 or by word
                end = False
                if len(text) > pos:
                    if text[pos].isspace():
                        pos += 1
                    else:  # if inside word, skip the all word
                        while not text[pos].isspace():
                            pos += 1
                            if len(text) == pos:
                                end = True
                                break
                else:  # reached end of text
                    break
                if end:
                    break
