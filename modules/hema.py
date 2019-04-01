from .base import Module
import random


class Hema(Module):
    DESCRIPTION = "Ribbit"

    def response(self, query, message):
        try:
            repetitions = int(query)
        except ValueError:
            repetitions = random.randint(5, 30)
        return " ".join(["ribbit"] * repetitions)
