from main import GurobiSolver,createProblem
from Problem import LP, QP, QCP
import os
import json
import pytest

def getJson(filename):
    """Read a JSON file and return its content."""
    with open(filename, 'r') as file:
        return json.load(file)
    
#Get the json for each example problem from folder TestProblems
milp = getJson(os.path.join("TestProblems", "MILP1.json"))
qp = getJson(os.path.join("TestProblems", "QP1.json"))
qcp = getJson(os.path.join("TestProblems", "QCP1.json"))

def testCreateProblemMILP():
    """Test the creation of a MILP problem."""
    problem = createProblem(milp)
    assert problem is not None, "Problem creation failed"
    assert isinstance(problem, LP), "Problem should be a LP"

def testCreateProblemQP():
    """Test the creation of a QP problem."""
    problem = createProblem(qp)
    assert problem is not None, "Problem creation failed"
    assert isinstance(problem, QP), "Problem should be a QP"

def testCreateProblemQCP():
    """Test the creation of a QCP problem."""
    problem = createProblem(qcp)
    assert problem is not None, "Problem creation failed"
    assert isinstance(problem, QCP), "Problem should be a QCP"

@pytest.mark.asyncio
async def testGurobiSolverMILP():
    """Test the GurobiSolver with a MILP problem."""
    result = await GurobiSolver(milp)
    assert isinstance(result, dict), "Result should be a dictionary"
    assert result.get("status")==2, "Expected status to be OPTIMAL(2)"
    assert result["solution"]["x_Resource1_Job1"] == 1, "Expected result from gurobi tutorial"
    assert result["solution"]["x_Resource2_Job3"] == 1, "Expected result from gurobi tutorial"
    assert result["solution"]["x_Resource3_Job2"] == 1, "Expected result from gurobi tutorial"

@pytest.mark.asyncio
async def testGurobiSolverQP():
    """Test the GurobiSolver with a QP problem."""
    result = await GurobiSolver(qp)
    assert isinstance(result, dict), "Result should be a dictionary"
    assert result.get("status")==2, "Expected status to be OPTIMAL(2)"
    assert isinstance(result["solution"],dict), "Solution should be a dictionary"

@pytest.mark.asyncio
async def testGurobiSolverQCP():
    """Test the GurobiSolver with a QCP problem."""
    result = await GurobiSolver(qcp)
    assert isinstance(result, dict), "Result should be a dictionary"
    assert result.get("status")==2, "Expected status to be OPTIMAL(2)"
    assert isinstance(result["solution"],dict), "Solution should be a dictionary"