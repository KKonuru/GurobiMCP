import gurobipy as grb
from gurobipy import GRB
from mcp.server.fastmcp import FastMCP
import sys
import io
from mcp import types
from Problem import LP,QP,QCP
# Create an MCP server
mcp = FastMCP("GurobiLLM")

supported_problem_types = ["LP", "MILP", "QP", "MIQP", "QCP", "MIQCP"]

@mcp.tool()
async def GurobiSolver(problem: dict) -> int:
    """
     Solve a linear programming problem using Gurobi.
            Terminology:
            - "Objective Function": The function to be maximized or minimized.
            - "Constraints": The conditions that the solution must satisfy.
            Supported problem types:
            - Linear Programming (LP)
            - Mixed Integer Linear Programming (MILP)
            - Quadratic Programming (QP)
            - Mixed Integer Quadratic Programming (MIQP)
            - Quadratic Constrained Programming (QCP)
            - Mixed Integer Quadratic Constrained Programming (MIQCP)
            
            For problem types such as LP,MILP,QP,MIQP do not include key "quadratic_constraints" in the constraints section.
            For problem types such as LP,MILP do not include the key "quadratic_terms" in the objective section.
    input_schema = {
                        "problem": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "type": {
                                    "type": "string",
                                    "enum": ["LP", "MILP", "QP", "MIQP", "QCP", "MIQCP"]
                                }
                            },
                            "required": ["type"],
                            "optional": ["name"]
                        },
                        "objective": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string", "enum": ["minimize", "maximize"]},
                                "function_type": {"type": "string", "enum": ["linear", "quadratic"]},
                                "linear_terms": {"type": "object",
                                    "patternProperties": {
                                        "^.*$": {"type": "number"}
                                    }
                                },
                                "quadratic_terms": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "var1": {"type": "string"},
                                            "var2": {"type": "string"},
                                            "coef": {"type": "number"}
                                        },
                                        "required": ["var1", "var2", "coef"]
                                    }
                                }
                            },
                            "required": ["type", "function_type", "linear_terms"],
                            "optional": ["quadratic_terms"]
                        },
                        "variables": {
                            "type": "object",
                            "patternProperties": {
                                "^.*$": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string"},
                                        "name": {"type": "string"},
                                        "lb": {"type": "number"},
                                        "ub": {"type": "number"}
                                    },
                                    "required": ["type"],
                                    "optional": ["name", "lb", "ub"]
                                }
                            }
                        },
                        "constraints": {
                            "type": "object",
                            "properties": {
                                "linear_constraints": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "lhs": {"type": "object",
                                                "patternProperties": {
                                                    "^.*$": {"type": "number"}
                                                }
                                            },
                                            "rhs": {"type": "number"},
                                            "sign": {"type": "string",
                                                "enum": ["=", "<=", ">=", "<", ">"]
                                            },
                                            "name": {"type": "string"}
                                        },
                                        "required": ["lhs", "rhs", "sign"],
                                        "optional": ["name"]
                                    }
                                },
                                "quadratic_constraints": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "quadratic_terms": {"type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "var1": {"type": "string"},
                                                        "var2": {"type": "string"},
                                                        "coef": {"type": "number"}
                                                    },
                                                    "required": ["var1", "var2", "coef"]
                                                }
                                            },
                                            "linear_terms": {"type": "object",
                                                "patternProperties": {
                                                    "^.*$": {"type": "number"}
                                                }
                                            },
                                            "constant": {"type": "number"},
                                            "sign": {"type": "string",
                                                "enum": ["=", "<=", ">=", "<", ">"]
                                            },
                                            "name": {"type": "string"}
                                        },
                                        "required": ["quadratic_terms", "linear_terms", "sign"],
                                        "optional": ["constant", "name"]
                                    }
                                }
                            }
                        },
                        "required": ["problem", "objective", "variables", "constraints"]
                    }

            Example input (QP):
            {
                "problem": {
                    "name": "Example QP",
                    "type": "QP"
                },
                "objective": {
                    "type": "minimize",
                    "function_type": "quadratic",
                    "linear_terms": {"x": 3, "y": 4},
                    "quadratic_terms": [
                    {"var1": "x", "var2": "x", "coef": 1},
                    {"var1": "x", "var2": "y", "coef": 2},
                    {"var1": "y", "var2": "y", "coef": 3}
                    ]
                },
                "variables": {
                    "x": {"type": "continuous", "lb": 0},
                    "y": {"type": "continuous", "lb": 0, "ub": 1}
                },
                "constraints": {
                    "linear_constraints": [
                        {
                            "lhs": {"x": 2, "y": 1},
                            "rhs": 10,
                            "sign": "<=",
                            "name": "c1"
                        }
                    ]
                }
            }
    """
    try:
        problem = createProblem(problem)
        model = problem.getModel()
        if model is None:
            return "Error: Model creation failed. Please check the problem definition."
        model.optimize()
        if model.status == GRB.OPTIMAL or model.status == GRB.TIME_LIMIT:
            solution = {v.varName: v.x for v in model.getVars()}
            result = {
                "status": model.status,
                "objective_value": model.objVal,
                "solution": solution
            }
            return result
        else:
            return f"Error: Optimization failed with status {model.status}. Please check the problem definition."
    except Exception as e:
        return f"Error: Problem type is not specified. {str(e)}"
    
#Create prompt for formulating the problem
@mcp.prompt()
def GurobiSolverPrompt(problem: str) -> str:
    return f"""
    You are a expert in optmization whose job is to take real world problems and formulate it as optimization problem that can be solved with the gurobi tool call accessible to you.
    You must determine the best problem formulation such that the solver can get the optimal solution quickly. The user will provide you with a problem description 
    and you will need to create a mathematical optimization model that can be solved using Gurobi. You will need to define the problem type, objective function, variables, and constraints based on the provided problem description.
    The problem must be formated as a problem of type {supported_problem_types}. You will take you formulation and create a json of the formulation according to the tool docstring to make the tool call.
    The problem is as follows:
    {problem}
    """


def createProblem(problem: dict):
    type = problem["problem"]["type"]
    if type == "LP" or type == "MILP":
        return LP(problem)
    elif type == "QP" or type == "MIQP":
        return QP(problem)
    elif type == "QCP" or type == "MIQCP":
        return QCP(problem)
    else:
        raise ValueError(f"Unsupported problem type: {type}")


if __name__ == "__main__":
    mcp.run()