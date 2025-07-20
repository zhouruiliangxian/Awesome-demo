"""This is a sample module demonstrating various Python elements."""

# Module-level variable
MODULE_VERSION = "1.0.0"

def greet(name: str) -> str:
    """Greet the given name.
    
    Args:
        name: The name to greet.
        
    Returns:
        A greeting message.
    """
    return f"Hello, {name}!"

class Person:
    """A class representing a person."""
    
    def __init__(self, name: str, age: int):
        """Initialize the person.
        
        Args:
            name: The person's name.
            age: The person's age.
        """
        self.name = name
        self.age = age
    
    def introduce(self) -> str:
        """Return a self-introduction."""
        return f"My name is {self.name} and I'm {self.age} years old."

def _private_function():
    """This is a private function (starts with underscore)."""
    pass

class _PrivateClass:
    """This is a private class (starts with underscore)."""
    pass