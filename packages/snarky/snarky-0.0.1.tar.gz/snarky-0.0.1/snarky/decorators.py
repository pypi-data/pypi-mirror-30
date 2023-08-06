"""Snarky behavioral decorators.
Decorators define behaviors that are involed when jk==True.
"""

import time # TODO: don't need to load it if not necessary... let user only load specifics

__all__ = ['snarky',
           'snarkyvoice',
           'say_time']

def snarky(fun):
    """Snarky text reaction when using the jk=True keyword argument."""
    def wrapper(*args, **kwargs):
        jk = kwargs.pop('jk', None)

        # before function call:
        if jk:
            text = "LOL! Then why are you asking me to run '" + fun.__name__ + "'? Unbelievable!"
            print(text)

        # function call:
        out = fun(*args, **kwargs)

        # after function call:
        if jk:
            pass

        return out

    return wrapper

def snarkyvoice(fun):
    """Snarky text-to-speech reaction when using the jk=True keyword argument."""
    from google_speech import Speech
    lang = "en"
    def wrapper(*args, **kwargs):
        jk = kwargs.pop('jk', None)

        # before function call:
        if jk:
            text = "LOL! Then why are you asking me to run '" + fun.__name__ + "'? Unbelievable!"
            speech = Speech(text, lang)
            speech.play(None)

         # function call:
        out = fun(*args, **kwargs)

        # after function call:
        if jk:
            pass

        return out

#             # you can also apply audio effects (using SoX)
#             # see http://sox.sourceforge.net/sox.html#EFFECTS for full effect documentation
#             sox_effects = ("speed", "1.5")
#             speech.play(sox_effects)
    return wrapper

def say_time(fun):
    """
    Outputs the time a function takes
    to execute.
    """

    from google_speech import Speech
    lang = "en"

    def wrapper(*args, **kwargs):
        t1 = time.time()
        out = fun(*args, **kwargs)
        t2 = time.time()
        text = "It took " + str((t2 - t1)) + " to run the function."
        print(text)
        speech = Speech(text, lang)
        speech.play(None)
        return out
    return wrapper