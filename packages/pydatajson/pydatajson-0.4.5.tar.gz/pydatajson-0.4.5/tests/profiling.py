#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Decorador auxiliar

Debe instalarse 'graphviz' en el sistema para que funcione.

    Ubuntu: sudo apt-get install graphviz
    Mac: brew install graphviz
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import with_statement
import os
import sys

from functools import wraps
from pycallgraph import PyCallGraph
from pycallgraph import Config
from pycallgraph import GlobbingFilter
from pycallgraph.output import GraphvizOutput

# módulo de ejemplo que se quiere analizar
import pydatajson

SAMPLES_DIR = os.path.join("tests", "samples")
TEMP_DIR = os.path.join("tests", "temp")


def profile(profiling_result_path):
    """Decorador de una función para que se corra haciendo profiling."""

    def fn_decorator(fn):
        """Decora una función con el análisis de profiling."""

        @wraps(fn)
        def fn_decorated(*args, **kwargs):
            """Crea la función decorada."""

            graphviz = GraphvizOutput()
            graphviz.output_file = profiling_result_path

            with PyCallGraph(output=graphviz, config=None):
                fn(*args, **kwargs)

        return fn_decorated
    return fn_decorator


@profile("tests/profiling/profiling_test.png")
def main():
    # hace un profiling de la función para guarda un catálogo en Excel
    original_catalog = pydatajson.DataJson(
        os.path.join(SAMPLES_DIR, "catalogo_justicia.json"))
    tmp_xlsx = os.path.join(TEMP_DIR, "xlsx_catalog.xlsx")
    original_catalog.to_xlsx(tmp_xlsx)


if __name__ == '__main__':
    main()
