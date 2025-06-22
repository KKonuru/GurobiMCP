# About
This project 
### What is a MCP server?
A MCP server is a standardized protocol for connecting Large Language Models (LLMs) to external data sources, resources, and 
### What problem types can I solve?
The MCP server accounts for the following problem types:
1.	Linear Programming (LP)
2.	Mixed-Integer Linear Programming (MILP / MIP)
3.	Quadratic Programming (QP) – convex and non-convex
4.	Mixed-Integer QP (MIQP)
5.	Quadratically Constrained Programming (QCP) – convex and non-convex
6.	Mixed-Integer QCP (MIQCP)
7.	Non-Convex Mixed-Integer Nonlinear Programming (MINLP)

### To do
1. Improve the input schema in doc string
2. Tool call to get lp file content
3. Fix max timeout
4. Unit tests

### Example problems:
non convex non linear program:
minimize   sin(x) + cos(2*x) + 1
subject to  0.25*exp(x) - x <= 0
           -1 <= x <= 4