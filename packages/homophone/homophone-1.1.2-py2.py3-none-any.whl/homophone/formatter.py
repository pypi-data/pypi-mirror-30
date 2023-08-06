"""Output formatters"""

import click


class ConsoleFormatter:
    def __init__(self, show_genres):
        self.show_genres = show_genres

    def __call__(self, artist):
        artist, genres = artist
        s = artist
        if self.show_genres:
            g = "\n".join(map(lambda s: "\t" + s, genres))
            s += "\n" + g
        return s
