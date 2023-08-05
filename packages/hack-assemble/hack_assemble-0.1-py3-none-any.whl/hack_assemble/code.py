from .utils import to_bin


def a_command(address: str) -> str:
    """ Returns an "A" command binary code.

    Args:
        address: a string with an integer content, representing a memory address.

    Returns:
        A 16-bit string representing an "A" command in binary code. Examples:
            "0" -> "0000000000000000"
            "1" -> "0000000000000000"
            "24576" -> "0110000000000000"

    Raises:
        ValueError: the address argument integer content was parsed as a negative integer, or the argument was higher
                    than the largest memory address.
    """
    _address = int(address)

    if _address < 0:
        raise ValueError(
            "address can't be negative (there are no negative memory addresses)")

    last_memory_address = 2 ** 15 - 1

    if _address > last_memory_address:
        raise ValueError("symbol can't be higher than {} because that's the last memory address".format(
            last_memory_address))

    return to_bin(_address).zfill(16)


def c_command(comp: str, dest: str, jump: str) -> str:
    """ Returns a "C" command binary code.

    Args:
        comp: a valid `comp` mnemonic. Examples: "0", "1", "-1", "A", "D+A", "M+A", "A-D".
        dest: a valid `dest` mnemonic. Examples: None, "M", "D", "A".
        jump: a valid `jump` mnemonic. Examples: None, "JMP", "JGE".

    Returns:
        A 16-bit string representing an "C" command in binary code. Examples:
            "0", None, "JMP" -> "1110101010000111"
            "1", "M", None -> "1111111111001000"

    Raises:
        ValueError: `comp`, or `dest`, or `jump` are invalid; both `dest` and `jump` are None; or both `dest` and `jump`
                    are not None.
    """
    def _fill(s):
        return s.zfill(7)

    def _fill1(s):
        return "1{}".format(s)

    comp_table = {
        "0": _fill("101010"),
        "1": _fill("111111"),
        "-1": _fill("111010"),
        "D": _fill("001100"),
        "A": _fill("110000"),
        "!D": _fill("001101"),
        "!A": _fill("110001"),
        "-D": _fill("001111"),
        "-A": _fill("110011"),
        "D+1": _fill("011111"),
        "A+1": _fill("110111"),
        "D-1": _fill("001110"),
        "A-1": _fill("110010"),
        "D+A": _fill("000010"),
        "D-A": _fill("010011"),
        "A-D": _fill("000111"),
        "D&A": _fill("000000"),
        "D|A": _fill("010101"),
        "M": _fill1("110000"),
        "!M": _fill1("110001"),
        "-M": _fill1("110011"),
        "M+1": _fill1("110111"),
        "M-1": _fill1("110010"),
        "D+M": _fill1("000010"),
        "D-M": _fill1("010011"),
        "M-D": _fill1("000111"),
        "D&M": _fill1("000000"),
        "D|M": _fill1("010101")
    }

    dest_table = {
        None: "000",
        "M": "001",
        "D": "010",
        "MD": "011",
        "A": "100",
        "AM": "101",
        "AD": "110",
        "AMD": "111"
    }

    jump_table = {
        None: "000",
        "JGT": "001",
        "JEQ": "010",
        "JGE": "011",
        "JLT": "100",
        "JNE": "101",
        "JLE": "110",
        "JMP": "111"
    }

    if comp not in comp_table:
        raise ValueError("Unexpected comp mnemonic: {}".format(comp))

    if dest not in dest_table:
        raise ValueError("Unexpected dest mnemonic: {}".format(dest))

    if jump not in jump_table:
        raise ValueError("Unexpected jump mnemonic: {}".format(jump))

    if not dest and not jump:
        raise ValueError(
            "Either the `dest` or the `jump` arguments must be not None.")

    if dest and jump is not None:
        raise ValueError("`dest` and `jump` arguments can't both be not None.")

    if jump and dest is not None:
        raise ValueError("`dest` and `jump` arguments can't both be not None.")

    return "111{}{}{}".format(
        comp_table[comp],
        dest_table[dest],
        jump_table[jump])
