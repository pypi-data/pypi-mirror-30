Decorator for PyCallGraph
#################

TODO

    # pip install pycallgraph
    # pip install pycallgraphdecorator
    # export CREATE_CALL_GRAPH=True
    # export CALL_GRAPH_OUTPUT_PATH=./call_graph/
    # export CALL_GRAPH_OUTPUT_TYPE=png

Python Call Graph Decorator
#################

Welcome! Python Call Graph Decorator is a `Python <http://www.python.org>`_ module with decorator for easy and effective use pyCallGraph that creates `call graph <http://en.wikipedia.org/wiki/Call_graph>`_ visualizations for Python applications.

.. image:: https://img.shields.io/pypi/v/pycallgraph.svg
    :target: https://crate.io/packages/pycallgraph/

Quick Start
===========

Installation is easy as::

    pip install pycallgraphdecorator

Or manually::

    python setup.py install

Decorator is possible turn on permanently or switching ON/OFF via set system environment before start tracking application.

Decorator is write very effective! Condition if graph's are creating is evaluated only ones and if condition is off ten decorator only call method.

Decorator is possible set globally via system environment or locally via decorator parameters.

Output::

    Each call decorated function create new graph in specific folder. Graphs are named as `function-name_graph-count.graph-type`

Possible system environment::

    CREATE_CALL_GRAPH - set create graph On/Off - value True/False, true/false, 0/1 (can by set unique environment name for each decorator - state_setup_env params)
    CALL_GRAPH_OUTPUT_PATH - set output path
    CALL_GRAPH_OUTPUT_TYPE - set output type - for example "png" (NOT ".png"!!!)

Possible decorator parameters::

     always_on=False - graph is crating always (environment CREATE_CALL_GRAPH isn't acceptable) - default False
     output_folder - output folder - default "./call_graph/"
     output_type - output graph type - default "png"
     state_setup_env - enable set specific system environment for turning on/off creating graphs - default "CREATE_CALL_GRAPH"

Simple use of the decorator::

   from callgraphdecorator import CallGraphDecorator

    @CallGraphDecorator(True)
    def test1():
        print("Hello Word.")

    if __name__ == '__main__':
        test1() // output - ./call_graph/test1_0.png
        test1() // output - ./call_graph/test1_1.png
