from mcp.server.fastmcp import FastMCP
import math

custom_mcp = FastMCP("Math") # name of the mcp server

# now create tools
@custom_mcp.tool()  # converts the python function into mcp tool
def add(a: int , b: int) -> int:
    "Add two numbers"
    return a + b

@custom_mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b
    
@custom_mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b
          
@custom_mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide a by b. Raises error if b is zero."""
    if b == 0:
        raise ValueError("Division by zero is not allowed.")
    return a / b

@custom_mcp.tool()
def square_root(x: float) -> float:
    """Return the square root of x."""
    if x < 0:
        raise ValueError("Cannot take square root of a negative number.")
    return math.sqrt(x)

@custom_mcp.tool()
def factorial(n: int) -> int:
    """Return factorial of n."""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers.")
    return math.factorial(n)

if __name__ == "__main__":
    custom_mcp.run("stdio")
    # custom_mcp.run('streamable-http') # for remote server
