import inspect

###############################################################################

def memoize(function):
    """Decorator that stores the return value of a function for given sets of
    parameters. This decorator is useful if a function is fairly expensive
    and is called frequently with the same parameters.
    
    Any function with this decorator can clear its memoized values using an
    attached function called clear_memoized_values.
    """
    
    # Use a dictionary to store all of the return values. The set of arguments
    # are used as keys.
    return_value_store = {}

    def clear_memoized_values():
        """Clears all of the memoized values in the function."""
        return_value_store.clear()
    
    def wrapper(*args, **kwargs):
        """Function returned by the memoize decorator. Checks if the set of
        arguments is already saved in the dictionary of return values before
        evaulating the function.
        """
        
        # Append the keyword args to the end of the regular args to represent
        # the unique key for the result.
        key = args + tuple((key, kwargs[key]) for key in sorted(kwargs.keys()))
        
        # Check the store for a return value.
        if (key in return_value_store):
            return return_value_store[key]
            
        # Evaluate the function and store the result.
        return_value = function(*args, **kwargs)
        return_value_store[key] = return_value
        
        return return_value
        
    # Give the wrapper function the clear function as a method.
    wrapper.clear_memoized_values = clear_memoized_values
        
    return wrapper
    
###############################################################################

def clear_memoized_values(obj):
    """Clears all memoized values for all methods that the specified object
    contains.
    """
    
    # Use the clear_memoized_values attached to each memoized function.
    for _, function in inspect.getmembers(obj):
        if (hasattr(function, 'clear_memoized_values')):
            function.clear_memoized_values()
        