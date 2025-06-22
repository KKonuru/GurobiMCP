from OptimizationProblem import OptimizationProblem
import sys
import io
import gurobipy as gp
from gurobipy import Model, GRB, quicksum
#This class is used to create Qudratic Programming (QP) models and can also be extended for Mixed Integer Quadratic Programming (MIQP) models.
class QP(OptimizationProblem):
    def __init__(self, name: str, problem: dict):
        super().__init__(name, problem) #class create model

    def _create_model(self):

        #Direct all output to string buffer to suppress Gurobi console output
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
            if "quadratic_constraints" in self._constraints:
                raise ValueError("Quadratic constraints are not supported in QP problems. Use QCP for quadratic constraints.")
            self._addQuadraticObjective()  # Add quadratic objective function to the model
            
        except Exception as e:
            print(f"An error occurred while creating the model: {e}")
            self._model = None
            raise e
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
        


        #Change output back to console
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        

