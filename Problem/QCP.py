from OptimizationProblem import OptimizationProblem
import sys
import io
import gurobipy as gp
from gurobipy import Model, GRB, quicksum

#This class is used to create Quadratic Constrained Programming (QCP) models and also can be extended for Mixed Integer Quadratic Constrained Programming (MIQCP) models.
class QCP(OptimizationProblem):
    def __init__(self, name: str, problem: dict):
        super().__init__(name, problem)  # class create model

    #Here we deal with quadratic constraints and objective functions.
    #Only at leat one constraint has to be quadratic and the rest can be linear.
    #The objective can be linear or quadratic.
    #So I need to account for either case
    def _create_model(self):
        # Direct all output to string buffer to suppress Gurobi console output
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        try:
            self._model = Model(self._name)
            self._model.setParam('OutputFlag', 0)
            self._model.setParam('LogToConsole', 0)

            self._addVariables()  # Add variables to the model
            self._addLinearConstraints()  # Add linear constraints to the model
            self._addQuadraticConstraints()  # Add quadratic constraints to the model
            
            self._addLinearObjective()  
        except Exception as e:
            self._model = None
            print(f"Error creating model: {e}")
        # Change output back to console
        sys.stdout = old_stdout
        sys.stderr = old_stderr