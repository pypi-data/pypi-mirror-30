from functools import wraps
try:
    from pycallgraph import PyCallGraph
    from pycallgraph.output import GraphvizOutput
except:
    pass
import os


class CallGraphDecorator(object):

    def __init__(self,
                 always_on=False,
                 output_folder=None,
                 output_type=None,
                 state_setup_env="CREATE_CALL_GRAPH"
                 ):
        if not output_folder:
            output_folder = os.environ.get("CALL_GRAPH_OUTPUT_PATH", "./call_graph/")
        if not output_type:
            output_type = os.environ.get("CALL_GRAPH_OUTPUT_TYPE", "png")

        try:
            if always_on:
                self.condition = True
            else:
                self.condition = os.environ.get(state_setup_env, 'false').lower() in ['true', 1]
            self.output_type = output_type
            self.output_folder = output_folder
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            self.graph_count = 0

            print("Initializing CallGraphDecorator SUCCESS with state: {state} and params - "
                  "output_folder: {fold}, "
                  "state_setup_env: {env} "
                  "output_type: {type}".format(
                    state=self.condition, 
                    fold=output_folder, 
                    env=state_setup_env, 
                    type=output_type)
                  )
        except:
            print("Initializing CallGraphDecorator FAILED")
            self.condition = False

    def __call__(self, func):
        if not self.condition:
            return func
        return self.log_graph(func)

    def log_graph(self, func):
        @wraps(func)
        def inner(*args, **kwds):
            try:
                graphviz = GraphvizOutput()
                graphviz.output_file = "{fold}_{count}.{type}".format(
                    fold=os.path.join(self.output_folder, func.__name__),
                    count=self.graph_count,
                    type=self.output_type)
                graphviz.output_type = self.output_type
                self.graph_count += 1
                with PyCallGraph(output=graphviz):
                    return func(*args, **kwds)
            except:
                return func(*args, **kwds)
        return inner
