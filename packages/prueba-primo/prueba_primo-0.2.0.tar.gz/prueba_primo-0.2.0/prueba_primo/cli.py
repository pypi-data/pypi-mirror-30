# -*- coding: utf-8 -*-

"""Console script for prueba_primo."""
import sys
import click
from prueba_primo import es_primo


@click.command()
@click.argument('number', type=int)
def main(number):
    """Console script for prueb_primo."""
    return es_primo(number)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
