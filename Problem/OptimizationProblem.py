from abc import ABC,abstractmethod
import os
from gurobipy import Model, GRB, quicksum
import tempfile
class OptimizationProblem(ABC):
    def __init__(self,problem:dict):
        self._name = problem["problem"].get("name", "OptimizationProblem")
        self._problem = problem
        self._objective = problem.get("objective", {})
        self._constraints = problem.get("constraints", [])
        self._variables = problem.get("variables",{})
        self._gurobi_variables = {}
        self._model = None
        self._solution = None
        self._status = None
        self._create_model()  # Call the method to create the model
        
    
    @abstractmethod
    def _create_model(self):
        pass

    def getModel(self):
        return self._model
    
    def getProblemAsLP(self) -> str:
        """
        Write the LP problem to a file in LP format.
        """
        if self._model is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".lp",mode='w+') as tmp:
                try:
                    self._model.write(tmp.name)
                    tmp.seek(0)  # Move to the beginning of the file
                    lp_string = tmp.read()
                finally:
                    tmp.close()
                    os.unlink(tmp.name)
            return lp_string
        else:
            return "Model is not created. Cannot write problem to file."
    
    def _addLinearConstraints(self) -> bool:
        if self._model is None:
            raise ValueError("Model is not created. Cannot add constraints.")
        
        default_constr_index = 0
        linear_constraints = self._constraints.get("linear_constraints", [])
        
        for constraint in linear_constraints:
            lhs_expr = quicksum(constraint["lhs"][var] * self._gurobi_variables[var] for var in constraint["lhs"])
            if constraint["sign"] == "<=":
                self._model.addConstr(lhs_expr <= constraint["rhs"], name=constraint.get("name", "Constraint_" + str(default_constr_index)))
            elif constraint["sign"] == "<":
                self._model.addConstr(lhs_expr < constraint["rhs"], name=constraint.get("name", "Constraint_" + str(default_constr_index)))
            elif constraint["sign"] == ">=":
                self._model.addConstr(lhs_expr >= constraint["rhs"], name=constraint.get("name", "Constraint_" + str(default_constr_index)))
            elif constraint["sign"] == ">":
                self._model.addConstr(lhs_expr >= constraint["rhs"], name=constraint.get("name", "Constraint_" + str(default_constr_index)))
            elif constraint["sign"] == "=":
                self._model.addConstr(lhs_expr == constraint["rhs"], name=constraint.get("name", "Constraint_" + str(default_constr_index)))
            else:
                raise ValueError(f"Unknown sign {constraint['sign']} in constraint: {constraint.get('name', '')}")
        
            default_constr_index += 1
        self._model.update()
        return True
    
    def _addQuadraticConstraints(self):
        if self._model is None:
            raise ValueError("Model is not created. Cannot add quadratic constraints.")
        counter=0
        quadratic_constraints = self._constraints.get("quadratic_constraints", [])
        for constraint in quadratic_constraints:
            quad_terms = constraint.get("quadratic_terms", [])
            linear_terms = constraint.get("linear_terms", {})
            constant = constraint.get("constant", 0)
            lhs_expr = quicksum(term["coef"] * self._gurobi_variables[term["var1"]] * self._gurobi_variables[term["var2"]] for term in quad_terms)
            lhs_expr += quicksum(linear_terms[var] * self._gurobi_variables[var] for var in linear_terms)
            lhs_expr += constant
            if constraint["sign"] == "<=":
                self._model.addQConstr(lhs_expr <= 0, name=constraint.get("name", "QuadraticConstraint_" + str(counter)))
            elif constraint["sign"] == "<":
                self._model.addQConstr(lhs_expr < 0, name=constraint.get("name", "QuadraticConstraint_" + str(counter)))
            elif constraint["sign"] == ">=":
                self._model.addQConstr(lhs_expr >= 0, name=constraint.get("name", "QuadraticConstraint_" + str(counter)))
            elif constraint["sign"] == ">":
                self._model.addQConstr(lhs_expr > 0, name=constraint.get("name", "QuadraticConstraint_" + str(counter)))
            elif constraint["sign"] == "=":
                self._model.addQConstr(lhs_expr == 0, name=constraint.get("name", "QuadraticConstraint_" + str(counter)))
            else:
                raise ValueError(f"Unknown sign {constraint['sign']} in quadratic constraint: {constraint.get('name', '')}")
            counter += 1
        self._model.update()
        return True
    
    def _addVariables(self):
        if self._model is None:
            raise ValueError("Model is not created. Cannot add variables.")
        for var in self._variables:
            """
            Define all the variables in the model.
            Each variable is defined with its type, name, lower bound (lb), upper bound (ub).
            Objective coefficient is not included in the variable definition.
            The type, name, lb, and ub parameters are optional.
            """
            var_info = self._variables[var]
            var_type = GRB.CONTINUOUS
            #Check if var type is in info
            if var_info.get("type")=="binary":
                var_type = GRB.BINARY
            elif var_info.get("type")=="integer":
                var_type = GRB.INTEGER
            elif var_info.get("type")=="semicontinuous":
                var_type = GRB.SEMICONTINUOUS
            elif var_info.get("type")=="semidefinite":
                var_type = GRB.SEMIDEFINITE
            add_var_parameters = {
                "name": var_info.get("name", var),
                "vtype": var_type
            }
            if "lb" in var_info:
                add_var_parameters["lb"] = var_info["lb"]
            if "ub" in var_info:
                add_var_parameters["ub"] = var_info["ub"]

            self._gurobi_variables[var] = self._model.addVar(**add_var_parameters)
        
        self._model.update() 
    
    def _addLinearObjective(self):
        if self._model is None:
            raise ValueError("Model is not created. Cannot add objective.")
        
        # Set the objective function
        objective = self._objective
        if objective["function_type"] != "linear":
            raise ValueError("Objective function type must be linear for LP problems. Use QP or QCP for quadratic objectives.")
        
        if objective["type"]=="maximize":
            obj_expr = quicksum(objective["linear_terms"][var] * self._gurobi_variables[var] for var in objective["linear_terms"])
            self._model.setObjective(obj_expr, GRB.MAXIMIZE)
        elif objective["type"]=="minimize":
            obj_expr = quicksum(objective["linear_terms"][var] * self._gurobi_variables[var] for var in objective["linear_terms"])
            self._model.setObjective(obj_expr, GRB.MINIMIZE)
        else:
            raise ValueError(f"Unknown objective function type: {objective['type']}")

        self._model.update() 
    def _addQuadraticObjective(self):
        if self._model is None:
            raise ValueError("Model is not created. Cannot add objective.")
        
        # Set the objective function
        objective = self._objective
        if objective["function_type"] != "quadratic":
            raise ValueError("Objective function type must be quadratic for QP problems. Use LP for linear objectives.")
        
        if objective["type"]=="maximize":
            obj_expr = quicksum(term["coef"] * self._gurobi_variables[term["var1"]] * self._gurobi_variables[term["var2"]] for term in objective["quadratic_terms"])
            obj_expr += quicksum(objective["linear_terms"][var] * self._gurobi_variables[var] for var in objective["linear_terms"])
            self._model.setObjective(obj_expr, GRB.MAXIMIZE)
        elif objective["type"]=="minimize":
            obj_expr = quicksum(term["coef"] * self._gurobi_variables[term["var1"]] * self._gurobi_variables[term["var2"]] for term in objective["quadratic_terms"])
            obj_expr += quicksum(objective["linear_terms"][var] * self._gurobi_variables[var] for var in objective["linear_terms"])
            self._model.setObjective(obj_expr, GRB.MINIMIZE)
        else:
            raise ValueError(f"Unknown objective function type: {objective['type']}")

        self._model.update()
    