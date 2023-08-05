from mythril.analysis.report import Issue
from mythril.exceptions import UnsatError
from mythril.analysis import solver
from z3 import simplify
import logging


'''
MODULE DESCRIPTION:

Check for constraints on tx.origin (i.e., access to some functionality is restricted to a specific origin).
'''


def execute(statespace):

    logging.debug("Executing module: EXCEPTIONS")

    issues = []

    for k in statespace.nodes:
        node = statespace.nodes[k]

        for state in node.states:

            instruction = state.get_current_instruction()

            if(instruction['opcode'] == "ASSERT_FAIL"):

                logging.debug("Opcode 0xfe detected.")

                try:
                    model = solver.get_model(node.constraints)
                    logging.debug("[EXCEPTIONS] MODEL: " + str(model))

                    address = state.get_current_instruction()['address']

                    description = "A reachable exception (opcode 0xfe) has been detected. This can be caused by type errors, division by zero, out-of-bounds array access, or assert violations. "
                    description += "This is acceptable in most situations. Note however that assert() should only be used to check invariants. Use require() for regular input checking. "
                    description += "The exception is triggered under the following conditions:\n\n"

                    for d in model.decls():

                        try:
                            condition = hex(model[d].as_long())
                        except:
                            condition = str(simplify(model[d]))

                        description += ("%s: %s\n" % (d.name(), condition))

                    description += "\n"

                    issues.append(Issue(node.contract_name, node.function_name, address, "Exception state", "Informational", description))

                except UnsatError:
                    logging.debug("[EXCEPTIONS] no model found")

    return issues
