from .parser import Parser
from .code import *
from .utils import to_bin


def assemble(source_code_file: str) -> list:
    """ Generates a list of Hack machine language commands.

    Args:
        source_code_file: a path to a Hack assembly file.

    Returns:
        a list of strings representing hack machine language commands. Examples:
            ["0000000000000010", "1110110000010000", "0000000000000011", "1110000010010000", "0000000000000000", "1110001100001000"]
    """
    parser = Parser(source_code_file)

    result = {
        "commands": [],
        "assembled": []
    }

    i = 16

    while parser.has_more_commands():
        current_command_type = parser.current_command_type()

        if current_command_type == parser.A_COMMAND:
            address = parser.a_command_address()
            if address.isdigit():
                result["commands"].append(parser.current_command())
                result["assembled"].append(a_command(address))
            else:
                symbol_table = parser.symbol_table

                if address in symbol_table:
                    result["commands"].append(parser.current_command())
                    result["assembled"].append(symbol_table[address].zfill(16))
                else:
                    parser.symbol_table = address, to_bin(i)
                    result["commands"].append(parser.current_command())
                    result["assembled"].append(to_bin(i).zfill(16))
                    i += 1

        elif current_command_type == parser.C_COMMAND:
            result["commands"].append(parser.current_command())
            result["assembled"].append(
                c_command(
                    parser.comp(),
                    parser.dest(),
                    parser.jump()))

        parser.advance()

    current_command_type = parser.current_command_type()

    if current_command_type == parser.A_COMMAND:
        address = parser.a_command_address()
        symbol_table = parser.symbol_table
        if address in symbol_table:
            result["commands"].append(parser.current_command())
            result["assembled"].append(a_command(symbol_table[address]))
        else:
            to_bin_i = to_bin(i)
            while to_bin_i not in symbol_table.values():
                i += 1
            parser.symbol_table = address, to_bin_i
            result["commands"].append(parser.current_command())
            result["assembled"].append(a_command(to_bin_i))

    elif current_command_type == parser.C_COMMAND:
        result["commands"].append(parser.current_command())
        result["assembled"].append(
            c_command(
                parser.comp(),
                parser.dest(),
                parser.jump()))

    return result
