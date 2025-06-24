# About
### What is a MCP server?
Model Context Protocol (MCP) is a open protocol that standardizes how Large Language Model (LLM) applications, such as IDEs and AI, connect with external data sources, tools, and prompts. Any application that is MCP compatible can use any MCP server to connect to external sources. This allows AI applications to improve its context with access to external data sources or tools. MCP servers can include databases, research paper search tools, etc. that extends the context available to a LLM.
### What is the Gurobi MCP?
This is a MCP server that connects a AI application to use gurobi solver on device to solve optimization problems formulated by the LLM. The MCP server runs on device and uses gurobi software installed on device 
### What problem types can I solve?
The MCP server accounts for the following problem types:
1.	Linear Programming (LP)
2.	Mixed-Integer Linear Programming (MILP)
3.	Quadratic Programming (QP) – convex and non-convex
4.	Mixed-Integer QP (MIQP)
5.	Quadratically Constrained Programming (QCP) – convex and non-convex
6.	Mixed-Integer QCP (MIQCP)

# How to setup the server in Claude desktop?
Note: If Claude desktop is not already downloaded, download it here: https://claude.ai/download
1. Clone the repository
```
git clone https://github.com/KKonuru/GurobiMCP.git
```
or download the project as a zip and unzip in your repo directory

2. Enter the project directory, create a virtual environment, and install packages listed in requirements.txt
```

```

3. Copy the full path of your python interpreter in .venv folder and the main.py file in your package. Then open claude desktop and open settings. 

In settings click on the developer tab on the left side of the page. Then click open edit config which will open file explorer. 

Open the file named "claude_desktop_config.json". Here modify the file such as stated below but replace the command and args with the two paths copied earlier.
```
{
    "mcpServers": {
    "gp-solver": {
        "command": "/Path/to/gurobiMCP/.venv/bin/python",
        "args": [
        "/Path/to/gurobiMCP/main.py"
        ]
    }
    }
}
```
4. Restart Claude desktop and the tool should appear after clicking the second icon on the left.
The prompt also appears when clicking the + icon

