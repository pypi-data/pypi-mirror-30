# -*- coding: utf-8 -*-

"""Main module."""

def wordstartfunc(stc, letter):
    """Prints the words in the given sentence that start with the given letter"""
    for word in stc.split():
        if word[0].lower() == letter.lower():
            print(word)

