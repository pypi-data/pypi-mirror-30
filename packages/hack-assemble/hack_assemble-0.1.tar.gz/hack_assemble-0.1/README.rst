Hack Assemble
==============

An Assembler program that translates programs written in the symbolic
Hack assembly language into binary code that can execute on the Hack
hardware platform built in the previous projects.

Usage
-----

The assembler can be invoked via command line with the command:

``hack-assemble fileName.asm``

, where the string fileName.asm is the assembler’s input, i.e. the name
of a text file containing Hack assembly commands. The assembler creates
an output text file named fileName.hack. Each line in the output file
consists of sixteen 0 and 1 characters. The output file is stored in the
same directory of the input file. The name of the input file may contain
a file path.

Reference
---------

http://nand2tetris.org/06.php
