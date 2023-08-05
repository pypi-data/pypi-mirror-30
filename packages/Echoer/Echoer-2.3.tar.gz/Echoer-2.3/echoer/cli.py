
import sys
import pyttsx3
import argparse
import click


@click.command()
@click.argument("words", nargs=-1, type=str)
def say(words):
    """
    Helps you turn strings on the command line into audio
    """
    word_string = " ".join(words)
    engine = pyttsx3.init()
    engine.say(word_string)
    engine.runAndWait()
