# ToDo:
# (2) Add branch to label functionality
# (3) Add label to immediate functionality so that labels can be stored into registers. For
# example, if label 'main' points to operation-line #34, then the operation 'movi r, main'
# would be assembled as the operation 'movi r, 34'
# (4) Add address modification, so that we can do 'str [r1 + 2], r3'


import sys
from enum import Enum
import struct
import colorama
import itertools
import json
from math import log2, log10, ceil, floor

class ERROR(Enum):
    invalid_argument_count = 0
    invalid_label_name = 1
    invalid_macro_name = 2
    label_in_macro_definition = 3
    invalid_macro_argc_declaration = 4
    macro_definition_in_macro_definition = 5
    end_of_macro_outside_macro_definition = 6
    invalid_macro_variable_name = 7
    macro_variable_name_gte_argc = 8
    repeated_word_on_line = 9
    more_than_label_on_line = 10
    args_do_no_match_operation_layout = 11
    invalid_operation_name = 12

class Error:
    def __init__(self, errno, sli):
        self.errno = errno
        self.sli = sli

    def print(self):
        print(colorama.Style.NORMAL + colorama.Fore.RED + "Error " + colorama.Style.BRIGHT + colorama.Fore.BLUE + str(self.errno).replace("ERROR.", '') + colorama.Style.NORMAL + colorama.Fore.RED + " on line " + colorama.Style.BRIGHT + colorama.Fore.YELLOW + str(self.sli + 1))

def line_has_label(line):
    if ':' in line:
        return True
    return False

def get_label(line):
    if not ':' in line:
        return False
    # If the label is not at the start, then this will find only the first label
    return strip_line(line).split(':')[0].split()[-1]

def strip_line(line):
    return line.split(';')[0].strip().lower()

def get_args_from_line(line):
    return ''.join(strip_line(line).split()[1:]).split(',')

def get_first_word_in_line(line):
    return strip_line(line).split()[0]

def is_macro_definition_line(line):
    if get_first_word_in_line(line) == '.macro':
        return True
    return False

def is_macro_end_line(line):
    if '.orcam' in line:
        return True
    return False

def remove_label_from_line(line):
    return strip_line(line).replace(get_label(line), '').strip()

def get_opname_from_line(line):
    if not line_has_label(line):
        return get_first_word_in_line(line)
    return get_first_word_in_line(line.split(':')[1])

def get_macroName_from_line(line):
    splits = strip_line(line).split()
    return splits[splits.index(".macro") + 1]

def get_macro_layout_from_definition(line):
    if line.isdigit():
        return 'v' * int(line)
    return strip_line(line).split()[2]

def get_line_syntax_errors_generic(line, sli):
    errors = []
    if line.count(".macro") > 1 or line.count(".orcam") > 1 or line.count(':') > 1:
        errors.append(Error(ERROR.repeated_word_on_line, sli))
    if is_macro_end_line(line) and line_has_label(line):
        errors.append(Error(ERROR.label_in_macro_definition, sli))
    if line_has_label(line) and strip_line(line).split(':')[1] != '':
        errors.append(Error(ERROR.more_than_label_on_line, sli))
    return errors

def get_line_syntax_errors_in_macro_definition(line, sli):
    errors = []
    if line_has_label(line):
        errors.append(Error(ERROR.label_in_macro_definition, sli))
    if is_macro_definition_line(line):
        errors.append(Error(ERROR.macro_definition_in_macro_definition, sli))
    return errors

def get_line_syntax_errors_out_of_macro_definition(line, sli):
    errors = []
    if is_macro_end_line(line):
        errors.append(Error(ERROR.end_of_macro_outside_macro_definition, sli))
    return errors

class OperationLine:
    def __init__(self, text, sourceLineIndex, opname=None, args=None, symbolTable=None):
        if opname is None: opname = get_opname_from_line(text)
        if args is None: args = get_args_from_line(text)
        self.text = text
        self.sli = sourceLineIndex
        self.opname = opname
        self.args = args
        self.layout = None
        if symbolTable is not None:
            self.fix(symbolTable)

    def fix(self, symbolTable):
        operation = symbolTable.operations.get(self.opname)
        if operation is None:
            return
        self.layout = operation.layout
        if len(self.layout) == len(self.args) + 1:
            if self.layout[0] == 'r':
                # Set the store location of the operation to the first operand
                self.args.insert(0, self.args[0])
            if self.layout[0] == 'c':
                if '.' in self.opname:
                    # The condition is in the opname
                    self.opname, condition = self.opname.split('.')
                    self.args.insert(0, condition)
                else:
                    # Say that the conditional statement always runs unless directed otherwise
                    self.args.insert(0, "true")

    def find_errors(self, symbolTable):
        errors = []
        operation = symbolTable.operations.get(self.opname)
        if operation is None:
            # Assume this is a macro
            macro = symbolTable.macros.get(self.opname)
            if macro is None:
                # The operation/macro doesn't exist
                return [Error(ERROR.invalid_operation_name, self.sli)]
            layout_pairs = [(f'${i}', arg_layout) for i, arg_layout in enumerate(macro.layout)]
        else:
            # use layout_pairs so that both macro-bound operations
            # normal operations can use the below for loop
            self.layout = operation.layout
            layout_pairs = [(self.args[i], arg_layout) for i, arg_layout in enumerate(self.layout)]
        for arg, arg_layout in layout_pairs:
            if arg not in symbolTable.layout_table[arg_layout].keys():
                errors.append(Error(ERROR.args_do_no_match_operation_layout, self.sli))
                break
        return errors

class Macro:
    def __init__(self, argc=None, body=None, layout=None):
        if argc is None: argc = 0
        if body is None: body = []
        if layout is None: layout = 'v' * argc
        self.argc = argc
        self.body = body
        self.layout = layout
    
    def insert_args(self, args):
        inserted_assembly = "\n".join(oline.text for oline in self.body)
        for i, arg in enumerate(args):
            inserted_assembly = inserted_assembly.replace(f'${i}', arg)
        return inserted_assembly.split('\n')

    def add_line(self, line, sli=None):
        if type(line) is not OperationLine:
            raise TypeError("'Macro.add_line()' only accepts an argument of type 'OperationLine'")
        self.body.append(line)

    def find_errors(self, symbolTable):
        errors = []
        for oline in self.body:
            oline.find_errors(symbolTable)
        return errors

class MacroCollection:
    def __init__(self, macros=None):
        if macros is None: macros = {}
        self.macros = macros
    
    def has_macro(self, macroName):
        if macroName in self.macros:
            return True
        return False
    
    def insert(self, macroName, macro):
        self.macros[macroName] = macro

    def get(self, macroName):
        return self.macros.get(macroName)

    def macro_append(self, macroName, line):
        self.macros[macroName].add_line(line)

class Operation:
    def __init__(self, opcode, layout):
        self.opcode = opcode
        self.layout = layout

class SymbolTable:
    def __init__(self, operations=None, registers=None, conditions=None, immediates=None, labels=None, macros=None, file=None):
        if file is not None:
            data = json.loads(open(file).read())
            operations = {}
            for operation in data['operations']:
                operations[operation['opname']] = Operation(operation['opcode'], operation['layout'])
            conditions = data['conditions']
            registers = data.get('registers')
            immediates = data.get('immediates')
        if operations is None: operations = {}
        if registers is None: registers = {}
        if conditions is None: conditions = []
        if immediates is None:
            decimals = {str(i): i for i in range(2 ** 16)}
            hexadecimals = {hex(i): i for i in range(2 ** 16)}
            octals = {oct(i): i for i in range(2 ** 16)}
            binaries = {bin(i): i for i in range(2 ** 16)}
            immediates = {**decimals, **hexadecimals, **octals, **binaries}
        if labels is None: labels = {}
        if macros is None: macros = MacroCollection()
        self.operations = operations
        self.registers = registers
        self.conditions = conditions
        self.immediates = immediates
        self.labels_to_indices = labels
        self.indices_to_labels = {}
        for key, value in self.labels_to_indices:
            if self.indices_to_labels.get(key):
                self.indices_to_labels[key].append(value)
                continue
            self.indices_to_labels[key] = [value]
        self.macros = macros
        self.layout_table = {
            'r': registers,
            'c': conditions,
            'i': immediates,
            'v': {**registers, **immediates, **conditions},
            'n': {**registers, **immediates}
        }
        self.argument_sizes = {}
        self.set_argument_sizes()

    def set_argument_sizes(self):
        for key, value in self.layout_table.items():
            if len(value) == 0:
                self.argument_sizes[key] = 0
                continue
            self.argument_sizes[key] = ceil(log2(max(value.values()) + 1))

    def add_generic_registers(self, n, begin=None):
        if begin is None: begin = 0
        for i in range(n):
            self.registers[f'r{i + begin}'] = i + begin
        self.set_argument_sizes()

    def assemble_operation(self, operation_line):
        operation = self.operations.get(operation_line.opname)
        machineCode = operation.opcode
        args = operation_line.args
        for i in range(len(operation.layout)):
            arg = args[i]
            arg_layout = operation.layout[i]
            machineCode = machineCode << self.argument_sizes[arg_layout]
            machineCode += self.layout_table[arg_layout][arg]
        machineCode = machineCode << 32 - 6 - sum(self.argument_sizes[arg_layout] for arg_layout in operation.layout)
        return machineCode

    def add_label(self, label, sli):
        self.labels_to_indices[label] = sli
        self.indices_to_labels[sli] = label

    def is_valid_layout(self, layout):
        if type(layout) is not str:
            raise TypeError("Argument 'layout' of Method 'is_valid_layout' must be of type 'str'")
        for char in layout:
            if char not in self.layout_table.keys():
                return False
        return True

class Assembler:
    def __init__(self, sourceCode=None, symbolTable=None):
        if type(sourceCode) is str: sourceCode = sourceCode.splitlines()
        if symbolTable is None: symbolTable = SymbolTable()
        self.sourceCode = sourceCode
        self.table = symbolTable
        self.operationLines = []
        self.machine_lines = []
        self.machineCode = []
        self.errors = []

    def reset(self, sourceCode=None):
        if type(sourceCode) is str:
            sourceCode = sourceCode.splitlines()
            # if sourceCode is str:
            #     # The code is one line long
            #     sourceCode = [sourceCode]
        self.sourceCode = sourceCode
        self.operationLines = []
        self.machineCode = []
        self.machineCode = []
        self.errors = []

    def analyze(self):
        macroName = False
        for i, line in enumerate(self.sourceCode):
            if len(line) == 0:
                continue
            self.errors.extend(get_line_syntax_errors_generic(line, i))
            if macroName:
                self.errors.extend(get_line_syntax_errors_in_macro_definition(line, i))
                if is_macro_end_line(line):
                    macroName = False
                    continue
                new_operationLine = OperationLine(line, i, symbolTable=self.table)
                self.table.macros.macro_append(macroName, new_operationLine)
                continue
            self.errors.extend(get_line_syntax_errors_out_of_macro_definition(line, i))
            if line_has_label(line):
                self.table.add_label(get_label(line), len(self.operationLines))
                continue
            if is_macro_definition_line(line):
                macroName = get_macroName_from_line(line)
                layout = get_macro_layout_from_definition(line)
                newMacro = Macro(argc=len(layout), layout=layout)
                self.table.macros.insert(macroName, newMacro)
                continue
            new_operationLine = OperationLine(line, i, symbolTable=self.table)
            self.operationLines.append(new_operationLine)

        # We run this afterwards because now we have the macros and labels in the table,
        # so we can check for invalid operation or label names
        for oline in self.operationLines:
            self.errors.extend(oline.find_errors(self.table))

    def insert_macros(self):
        complete_operationLines = []
        for i, oline in enumerate(self.operationLines):
            macro = self.table.macros.get(oline.opname)
            if macro is not None:
                sli = oline.sli
                for mline in macro.insert_args(oline.args):
                    complete_operationLines.append(OperationLine(mline, sli, symbolTable=self.table))
                continue
            complete_operationLines.append(oline)
        self.operationLines = complete_operationLines[:]

    def print_operationLines(self):
        for oline in self.operationLines:
            print(oline.text)

    def synthesize(self):
        self.insert_macros()
        for operation in self.operationLines:
            self.machine_lines.append(self.table.assemble_operation(operation))
        self.machineCode_in_bytes = []
        self.machineCode = bytearray()
        for line in self.machine_lines:
            self.machineCode.extend(line.to_bytes(4, byteorder='big', signed=False))
            # The above is equivalent to the below:
            #
            # self.machineCode.append((line & 0xff000000) >> 24)
            # self.machineCode.append((line & 0x00ff0000) >> 16)
            # self.machineCode.append((line & 0x0000ff00) >> 8)
            # self.machineCode.append(line & 0x000000ff)
            #

    def printLines(self):
        longest_line_length = max([len(strip_line(oline.text)) for oline in self.operationLines])
        total_binary = ""
        for i, oline in enumerate(self.operationLines):
            sli = oline.sli
            if sli == self.operationLines[i - 1].sli:
                continue
            cline = self.machine_lines[i]
            binary = bin(cline).replace("0b", '').zfill(32)
            line_text = strip_line(self.sourceCode[sli])
            left = f'{oline.sli + 1})'+ ' ' * (1 + ceil(log10(len(self.sourceCode))) - ceil(log10(sli) if sli > 1 else 1)) + strip_line(line_text) + ' '
            left += '-' * (longest_line_length - len(line_text))
            # left += '-> '
            while i < len(self.operationLines) - 1 and self.operationLines[i + 1].sli == sli:
                i += 1
                cline = self.machine_lines[i]
                binary += bin(cline).replace("0b", '').zfill(32)
            print(f'{left}--> {binary}')
            total_binary += binary
        print(colorama.Fore.LIGHTBLACK_EX + '~' * 128)
        print("Binary out:", total_binary)

    def assemble(self, sourceCode=None):
        if sourceCode is not None:
            # This allows one to save a symbol table across multiple translation units
            self.reset(sourceCode)
        self.analyze()
        if not self.flush_errors():
            self.synthesize()
            self.printLines()
            # print("------------------------------------------------")
            # print("Binary:", bin(int.from_bytes(self.machineCode)).replace("0b", '').zfill(8 * len(self.machineCode)))
            return self.machineCode
        return None

    def flush_errors(self):
        for error in self.errors:
            error.print()
        if self.errors != []:
            self.errors = []
            return True
        return False

if __name__ == "__main__":
    colorama.init(autoreset=True)
    sourceCode = open("os.asm").read()  # open(sys.argv[1]).read()
    symbolTable = SymbolTable(file='symbol_table.json')
    symbolTable.add_generic_registers(31, begin=1)
    symbolTable.argument_sizes['c'] = 5
    program = Assembler(sourceCode, symbolTable=symbolTable)
    machineCode = program.assemble()
    if machineCode is None:
        exit(-1)
    with open('eout', 'wb+') as ofile:
        ofile.write(machineCode)
