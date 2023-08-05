from typing import Optional

from .utils import between_parentheses, to_bin


class Parser(object):
    """Hack Assembly Parser

    Encapsulates access to the hack assembly source code, providing convenient access to the commands' components.
    In addition, removes all whitespaces and comments, and executes a first pass to build the symbol table.

    Reference: http://nand2tetris.org/chapters/chapter%2006.pdf

    Attributes:
        _commands: the commands found in the source code file.
        _current_command_index: the index of the command that will be the object of non-static methods such as `comp`,
                                `dest`, or `jump`.
        A_COMMAND: a string constant to compare with to know if a command type is "A".
        L_COMMAND: a string constant to compare with to know if a command type is "L"  (i.e a pseudocommand).
        C_COMMAND: a string constant to compare with to know if a command type is "C".
        _symbol_table: a dict that maps symbols to memory addresses. Used to substitute predefined, label, and variable
                      symbols in the source code to generate hack machine code.
        VALID_COMP: a list of the valid `comp` mnemonics of "C" commands.
        VALID_DEST: a list of the valid `dest` mnemonics of "C" commands.
        VALID_JUMP: a list of the valid `jump` mnemonics of "C" commands.

    """

    def __init__(self, source_code_file):
        """Initializes the Hack Assembly Parser

        Args:
            source_code_file: a hack assembly file path.
        """
        self._commands = []
        with open(source_code_file) as f:
            for line in f:
                comment_occurrence = line.find("//")
                line = ''.join(line[:comment_occurrence].replace(" ", ""))
                if line:
                    self._commands.append(line)
        if not self._commands:
            raise ValueError(
                "Source code file doesn't have assembly commands.")
        self._current_command_index = 0
        self.A_COMMAND = "A_COMMAND"
        self.L_COMMAND = "L_COMMAND"
        self.C_COMMAND = "C_COMMAND"
        self._symbol_table = {
            "SP": to_bin(0),
            "LCL": to_bin(1),
            "ARG": to_bin(2),
            "THIS": to_bin(3),
            "THAT": to_bin(4),
            "R0": to_bin(0),
            "R1": to_bin(1),
            "R2": to_bin(2),
            "R3": to_bin(3),
            "R4": to_bin(4),
            "R5": to_bin(5),
            "R6": to_bin(6),
            "R7": to_bin(7),
            "R8": to_bin(8),
            "R9": to_bin(9),
            "R10": to_bin(10),
            "R11": to_bin(11),
            "R12": to_bin(12),
            "R13": to_bin(13),
            "R14": to_bin(14),
            "R15": to_bin(15),
            "SCREEN": to_bin(16384),
            "KBD": to_bin(24576)
        }
        self.VALID_COMP = [
            "0",
            "1",
            "-1",
            "D",
            "A",
            "!D",
            "!A",
            "-D",
            "-A",
            "D+1",
            "A+1",
            "D-1",
            "A-1",
            "D+A",
            "D-A",
            "A-D",
            "D&A",
            "D|A",
            "M",
            "!M",
            "-M",
            "M+1",
            "M-1",
            "D+M",
            "D-M",
            "M-D",
            "D&M",
            "D|M"]
        if len(self.VALID_COMP) != 28:
            raise AttributeError(
                "invalid list of valid comp mnemonics: {}".format(
                    self.VALID_COMP))
        self.VALID_DEST = [None, "M", "D", "MD", "A", "AM", "AD", "AMD"]
        if len(self.VALID_DEST) != 8:
            raise AttributeError(
                "invalid list of valid dest mnemonics: {}".format(
                    self.VALID_DEST))
        self.VALID_JUMP = [
            None,
            "JGT",
            "JEQ",
            "JGE",
            "JLT",
            "JNE",
            "JLE",
            "JMP"]
        if len(self.VALID_JUMP) != 8:
            raise AttributeError(
                "invalid list of valid jump mnemonics: {}".format(
                    self.VALID_JUMP))
        self._first_pass()

    @property
    def commands(self) -> list:
        """Returns the commands found in the source code file.

        Returns:
            A list of commands. Example: ["@2", "D=A", "@3", "D=D+A", "@0", "M=D"]
        """
        return self._commands

    def number_of_commands(self) -> int:
        """ Returns the number of commands found in the source code file.

        Returns:
            An int. Example: 6.
        """
        return len(self.commands)

    @property
    def current_command_index(self) -> int:
        """Returns the value the index of the command that will be the object of non-static methods such as `comp`,
           `dest`, or `jump`.

        Returns:
            An int. Example: 0.
        """
        return self._current_command_index

    @current_command_index.setter
    def current_command_index(self, value: int):
        self._current_command_index = value

    def current_command(self) -> str:
        """Returns the command that will be the object of non-static methods such as `comp`, `dest`, or `jump`.

        Returns:
            A string. Examples: ""@2", ""D=A".
        """
        return self.commands[self.current_command_index]

    def has_more_commands(self) -> bool:
        """Returns False if the current command is the last command in the source code file. Else, return True.

        Returns:
            A bool. True, or False.
        """
        return self.current_command_index < self.number_of_commands() - 1

    def _increment_command_index(self):
        """Adds 1 to the _current_command_index"""
        self._current_command_index += 1

    def advance(self):
        """Makes the next command the current command.

        Raises:
            IndexError: called this method when the current command is already the last one.
        """
        if self.has_more_commands():
            self._increment_command_index()
        else:
            raise IndexError(
                "Already in the last command: {}.".format(
                    self.current_command()))

    @staticmethod
    def is_a_command(command: str) -> bool:
        """Checks if a string is an "A" command.

        Args:
            command: a string. Examples: ""@2", ""D=A".

        Returns:
            A boolean. True, or False
        """
        first_char = command[0]

        if first_char == "@":
            return True

        return False

    @staticmethod
    def is_l_command(command: str) -> bool:
        """Checks if a string is a "L" command, i.e a pseudocommand.

        Args:
            command: a string. Examples: ""@2", ""D=A", (LOOP).

        Returns:
            A boolean. True, or False
        """
        first_char = command[0]

        if first_char == "(":
            return True

        return False

    def is_c_command(self, command: str) -> bool:
        """Checks if a string is a "C" command.

        Args:
            command: a string. Examples: ""@2", ""D=A".

        Returns:
            A boolean. True, or False
        """
        if self.is_a_command(command) or self.is_l_command(command):
            return False

        assign_char_index = command.find("=")

        if assign_char_index == -1:
            assign_char_index = command.find(";")

        if assign_char_index == -1:
            return False

        return True

    def current_command_type(self) -> str:
        """ Returns the current command type.
        Returns:
            A string. Check the A_COMMAND, L_COMMAND, and the C_COMMAND Parser attributes for the specific values of
            the returned string.
        """
        current_command = self.current_command()

        if self.is_a_command(current_command):
            return self.A_COMMAND
        elif self.is_l_command(current_command):
            return self.L_COMMAND
        elif self.is_c_command(current_command):
            return self.C_COMMAND
        else:
            raise ValueError(
                f"Invalid command {current_command} at command index {self.current_command_index}")

    @property
    def symbol_table(self) -> dict:
        """
        Returns:
            The value of the Parser's _symbol_table attribute.
        """
        return self._symbol_table

    @symbol_table.setter
    def symbol_table(self, value: tuple):
        """ Updates the value of the Parser's symbol_table attribute
        Args:
            value: a tuple with the format (key, value). The resulting dict will be merged into the symbol_table.
        """
        self._symbol_table = {**self.symbol_table, **{value[0]: value[1]}}

    def l_command_symbol(self) -> str:
        """
        Returns:
            A string with the value of the symbol between the parentheses of a "L" command (pseudocommand). Example:
            (LOOP) -> "LOOP", (HERE) -> "HERE".

        Raises:
            ValueError: the current command is not a "L" command.
        """
        current_command = self.current_command()

        if not self.is_l_command(current_command):
            raise ValueError(
                f"Command {current_command} is not a {self.L_COMMAND}")

        return between_parentheses(current_command)

    def restart_current_command_index(self):
        """Sets the current command index to 0.

        """
        self.current_command_index = 0

    def _first_pass(self):
        """
        “Go through the entire assembly program, line by line, and build the symbol table without generating any code.
        As you march through the program lines, keep a running number recording the ROM address into which the current
        command will be eventually loaded. This number starts at 0 and is incremented by 1 whenever a C-instruction or
        an A-instruction is encountered, but does not change when a label pseudocommand or a comment is encountered.
        Each time a pseudocommand (Xxx) is encountered, add a new entry to the symbol table, associating Xxx with the
        ROM address that will eventually store the next command in the program. This pass results in entering all the
        program’s labels along with their ROM addresses into the symbol table. The program’s variables are handled in
        the second pass.”

        Excerpt From: Nisan, Noam. “The Elements of Computing Systems: Building a Modern Computer from First Principles.”
        """
        i = 0
        while self.has_more_commands():
            if self.current_command_type() == self.L_COMMAND:
                l_symbol = self.l_command_symbol()
                if l_symbol not in self.symbol_table:
                    self._symbol_table[l_symbol] = to_bin(i)
            else:
                i += 1
            self.advance()
        if self.current_command_type() == self.L_COMMAND:
            l_symbol = self.l_command_symbol()
            if l_symbol not in self.symbol_table:
                self._symbol_table[l_symbol] = to_bin(
                    self.current_command_index)
        self.restart_current_command_index()

    def a_command_address(self) -> str:
        """ Returns the `address` mnemonic of the current command.

        Returns:
            A string. Examples: "@R0" -> "R0", "@1" -> "1", "@i" -> "i".

        Raises:
            ValueError: current command is not an "A" command.
        """
        current_command = self.current_command()

        if not self.is_a_command(current_command):
            raise ValueError(
                f"Command {current_command} at command index {self.current_command_index} "
                f"is not an {self.A_COMMAND}")

        return current_command[1:]

    def comp(self) -> str:
        """ Returns the `comp` mnemonic of the current command.

        Returns:
            A string. Examples: "D=D+A" -> "D+A", "D=M" -> "M", "0:JMP" -> "0", "D;JGT" -> "D".

        Raises:
            ValueError: current command is not a "C" command, or found an invalid comp mnemonic at the "C" command.
        """
        current_command = self.current_command()

        if not self.is_c_command(current_command):
            raise ValueError(
                f"Command {current_command} at command index {self.current_command_index} "
                f"is not a {self.C_COMMAND}.")

        assign_char_index = current_command.find("=")

        if assign_char_index == -1:
            assign_char_index = current_command.find(";")

            if assign_char_index == -1:
                raise ValueError(
                    f"Command {current_command} at command index {self.current_command_index} "
                    f"doesn't have a comp mnemonic.")

            comp = current_command[:assign_char_index]
        else:
            comp = current_command[assign_char_index + 1:]

        if comp in self.VALID_COMP:
            return comp

        raise ValueError(
            f"Invalid comp mnemonic at command {current_command}, at command index "
            f"{self.current_command_index}")

    def dest(self) -> Optional[str]:
        """ Returns the `dest` mnemonic of the current command.

        Returns:
            A string. Examples: "D=D+A" -> "D", "D=M" -> "D", "M=D" -> "M".

        Raises:
            ValueError: current command is not a "C" command, or found an invalid dest mnemonic at the "C" command.
        """
        current_command = self.current_command()

        if not self.is_c_command(current_command):
            raise ValueError(
                f"Command {current_command} at command index {self.current_command_index} "
                f"is not a {self.C_COMMAND}.")

        assign_char_index = current_command.find("=")

        if assign_char_index == -1:
            return

        dest = current_command[:assign_char_index]

        if dest in self.VALID_DEST:
            return dest

        raise ValueError(
            f"Invalid dest mnemonic at command {current_command}, command index "
            f"{self.current_command_index}")

    def jump(self) -> Optional[str]:
        """ Returns the `jump` mnemonic of the current command.

        Returns:
            A string. Examples: "0:JMP" -> "JMP", "D;JGT" -> "JGT".

        Raises:
            ValueError: current command is not a "C" command, or found an invalid `jump` mnemonic at the "C" command.
        """
        current_command = self.current_command()

        if not self.is_c_command(current_command):
            raise ValueError(
                f"Command {current_command} at command index {self.current_command_index} "
                f"is not a {self.C_COMMAND}.")

        assign_char_index = current_command.find(";")

        if assign_char_index == -1:
            return

        jump = current_command[assign_char_index + 1:]

        if jump in self.VALID_JUMP:
            return jump

        raise ValueError(
            f"Invalid jump mnemonic at command {current_command}, command index "
            f"{self.current_command_index}")
