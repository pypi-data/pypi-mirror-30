def between_parentheses(s: str) -> str:
    """ Returns the text between the parentheses found in a string argument
    Args:
        s: a string

    Returns:
        a string. Examples: "(LOOP)" -> "LOOP", "(123 456)" -> "123 456"

    """
    return s[s.find("(") + 1:s.rfind(")")]


def to_bin(n: int) -> str:
    """ Returns a 15-bit binary string representing the value of the integer argument.
    Args:
        n: a positive integer.

    Returns:
        a string. Examples: 0 -> "000000000000000", 1 -> "000000000000001", 2 -> "000000000000010",
                            24576 -> "110000000000000"
    """
    if n < 0:
        raise ValueError(
            "This function doesn't accept negative number arguments")

    return bin(n)[2:].zfill(15)
