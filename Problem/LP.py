from OptimizationProblem import OptimizationProblem
import sys
import io
import gurobipy as gp
from gurobipy import Model, GRB, quicksum
import os
#This class is used to create Linear Programming (LP) models and can also be extended for Mixed Integer Linear Programming (MILP) models.
class LP(OptimizationProblem):
    def __init__(self, name: str, problem: dict):
        super().__init__(name, problem) #class create model
        self._create_model()  # Call the method to create the model
        
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
            
            self._addVariables()
            if "quadratic_constraints" in self._constraints:
                raise ValueError("Quadratic constraints are not supported in LP problems. Use QP or QCP for quadratic constraints.")
            # Set the constraints
            self._addLinearConstraints()  
            
            self._addLinearObjective()
        except Exception as e:
            print(f"An error occurred while creating the model: {e}")
            self._model = None
            raise e
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
        
        
    
        
    

        

        
        

