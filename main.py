import gurobipy as grb
from gurobipy import GRB
from mcp.server.fastmcp import FastMCP
import sys
import io
from mcp import types
from Problem import LP,QP,QCP
# Create an MCP server
mcp = FastMCP("GurobiLLM")

@mcp.tool()
async def GurobiSolver(problem: dict) -> int:
    """
     Solve a linear programming problem using Gurobi.
            Terminology:
            - "Decision Variables": The variables to be optimized.
            - "Objective Function": The function to be maximized or minimized.
            - "Constraints": The conditions that the solution must satisfy.
            Supported problem types:
            - Linear Programming (LP)
            - Mixed Integer Linear Programming (MILP)
            - Quadratic Programming (QP)
            - Mixed Integer Quadratic Programming (MIQP)
            - Quadratic Constrained Programming (QCP)
            - Mixed Integer Quadratic Constrained Programming (MIQCP)
            Any other problem types will fail with an error.
            Anything not specified as required is not required.
    inputSchema={
                {    
                    "problem": {
                        "name": {"type":"string"},
                        "type": {"type": "string", "enum": ["LP", "MILP", "QP", "MIQP", "QCP", "MIQCP"]},
                        "required":["type"]
                    },
                    "objective": {
                        "type": "minimize",
                        "function_type": "quadratic",
                        "linear_terms": {
                            "x": 3,
                            "y": 4
                        },
                        "quadratic_terms": [
                            { "var1": "x", "var2": "x", "coef": 1 },
                            { "var1": "x", "var2": "y", "coef": 2 },
                            { "var1": "y", "var2": "y", "coef": 3 }
                        ]
                    },
                    "variables": {"type":"dict","example":{
                            "x": {"type":"dict","example":{"type": "continuous", "name":"factories","lb": 0}},
                            "y": {"type": "dict","example":{"name":"water", "lb": 0, "ub": 1}}
                    }},
                    "constraints": {"type":"list","example":
                    {
                       "linear_constraints": [
                        
                        {
                            "lhs": {
                                "x": 2,
                                "y": 1
                            },
                            "rhs": 10,
                            "sign": "<=",
                            "name": "c1"
                        },
                        {
                            "lhs": {
                                "x": 1,
                                "y": -1
                            },
                            "rhs": 2,
                            "sign": ">=",
                            "name": "c2"
                        }
                        ],
                        "quadratic_constraints": [
                        {
                            "quadratic_terms": [
                            { "var1": "x", "var2": "x", "coef": 2 },
                            { "var1": "x", "var2": "y", "coef": 1 },
                            { "var1": "y", "var2": "y", "coef": 3 }
                            ],
                            "linear_terms": {
                            "x": 1,
                            "y": -2
                            },
                            "constant": -5,
                            "sign": "<=",
                            "name": "q1"
                        }
                            
                        ]
                    }
                    },
                    "required": ["problem", "objective", "variables", "constraints"]
                }
            }
    """
    try:
        problem = createProblem(problem)
        problem._create_model()
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