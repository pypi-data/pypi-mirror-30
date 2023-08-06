from z3 import *
from mythril.analysis import solver
from mythril.analysis.ops import *
from mythril.analysis.report import Issue
from mythril.exceptions import UnsatError
import re
import copy
import logging


'''
MODULE DESCRIPTION:

Check for integer underflows.
For every SUB instruction, check if there's a possible state where op1 > op0.
'''


def execute(statespace):

    logging.debug("Executing module: INTEGER")

    issues = []

    for k in statespace.nodes:
        node = statespace.nodes[k]

        for state in node.states:

            instruction = state.get_current_instruction()

            if(instruction['opcode'] == "SUB"):

                stack = state.mstate.stack

                op0 = stack[-1]
                op1 = stack[-2]

                constraints = copy.deepcopy(node.constraints)

                if type(op0) == int and type(op1) == int:
                    continue

                if (re.search(r'calldatasize_', str(op0))) \
                    or (re.search(r'256\*.*If\(1', str(op0), re.DOTALL) or re.search(r'256\*.*If\(1', str(op1), re.DOTALL)) \
                    or (re.search(r'32 \+.*calldata', str(op0), re.DOTALL) or re.search(r'32 \+.*calldata', str(op1), re.DOTALL)):

                    # Filter for patterns that contain bening nteger underflows.

                    # Pattern 1: (96 + calldatasize_MAIN) - (96), where (96 + calldatasize_MAIN) would underflow if calldatasize is very large.
                    # Pattern 2: (256*If(1 & storage_0 == 0, 1, 0)) - 1, this would underlow if storage_0 = 0

                    continue

                logging.debug("[INTEGER_UNDERFLOW] Checking SUB " + str(op0) + ", " + str(op1) + " at address " + str(instruction['address']))

                allowed_types = [int, BitVecRef, BitVecNumRef]

                if type(op0) in allowed_types and type(op1) in allowed_types:
                    constraints.append(UGT(op1,op0))

                    try:

                        model = solver.get_model(constraints)

                        issue = Issue(node.contract_name, node.function_name, instruction['address'], "Integer Underflow", "Warning")

                        issue.description = "A possible integer underflow exists in the function " + node.function_name + ".\n" \
                            "The subtraction may result in a value < 0."

                        issue.debug = solver.pretty_print_model(model)
                        issues.append(issue)

                    except UnsatError:
                        logging.debug("[INTEGER_UNDERFLOW] no model found") 

    return issues
