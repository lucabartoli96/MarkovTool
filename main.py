# coding=utf-8

from markov_command import run as markov

MARKOV, GENERATOR = 'markov', 'gen'

def main(argv):

    if len(argv) == 1:
        raise ValueError('No Action specified')
    else:
        command = argv[1]
        if command not in (MARKOV, GENERATOR):
            raise ValueError('Unknown command \'%s\'' % command)
        else:
            if command == MARKOV:
                markov(argv)
            elif command == GENERATOR:
                gen(argv)
