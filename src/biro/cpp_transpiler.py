from biro.middleware import BiroIntermediateCode, BiroBuiltins, Error, Scope
from biro.lexerparser import Parser
import os


class CPP(BiroBuiltins):
    code = []
    comment_mark = "//"
    namespace = "builtins"

    implementation_path = os.path.abspath(
        os.path.join(
            os.path.abspath(__file__),
            os.path.pardir,
            os.path.pardir,
            "implementations",
            "cpp",
        )
    )

    initialization = {
        "num": "float",
        "str": "std::string",
        "bool": "bool",
        ("a", "num"): "std::vector<float>",
        ("a", "str"): "std::vector<std::string>",
        ("a", "bool"): "std::vector<bool>",
        ("q", "num"): "std::queue<float>",
        ("q", "str"): "std::queue<std::string>",
        ("q", "bool"): "std::queue<bool>",
        ("s", "num"): "std::stack<float>",
        ("s", "str"): "std::stack<std::string>",
        ("s", "bool"): "std::stack<bool>",
    }

    def __init__(self, parser: Parser) -> None:
        self.biro: BiroIntermediateCode = parser.biro
        self.parser = parser
        self.type_func_mapping = {
            "variable_declaration": (self._make_variable_declaration, ";"),
            "variable_assignment": (self._make_variable_assignment, ";"),
            "function_call": (self._make_function_call, ";"),
            "builtin_call": (self._make_builtin_call, ";"),
            "try_block": (self._make_try_block, ""),
            "catch_block": (self._make_catch_block, ""),
            "loop_statement": (self._make_loop_statement, ""),
            "conditional_statement": (self._make_conditional_statement, ""),
            "donate_statement": (self._make_donate_statement, ";"),
        }

    def make(self):
        # print(self.biro.getCode())
        self._make_header()
        self._make_includes()
        self._make_builtins()
        self._make_globals()
        self._make_funcs()
        self._make_user_code()
        return "\n".join(self.code)

    def _make_header(self) -> None:
        code = ""
        for line in self.biro._header.split("\n"):
            code += f"{self.comment_mark}{line}\n"
        self.code.append(code)

    def _make_includes(self) -> None:
        code = """
        #include <iostream>
        #include <string>
        #include <vector>
        #include <queue>
        #include <stack>
        #include <cmath>
        """
        self.code.append(code)

    def _make_globals(self) -> None:
        code = [
            f"\t{self.initialization[Type]} {name};"
            for name, Type in self.biro.getGlobals().items()
        ]
        self.code.append("\n".join(code))

    def _make_funcs(self) -> None:
        for func, body in self.biro.getFunc().items():
            code = f"""{
                    self.initialization[body[1]] if body[1] != 'void' else 'void'
                } {func[0]} ({
                ",".join(
                    [
                        f"{self.initialization[types]} {names}"
                        for names, types in zip(body[0], func[1])
                    ]
                )
            }) {{
                {self._make_statement_list(body[2])}
            }}"""
            self.code.append(code)

    def _make_builtins(self) -> None:
        builtins = "\n".join(
            [
                self._builtin_say(),
                self._builtin_ask(),
                self._builtin_index(),
                self._builtin_len(),
            ]
        )
        code = f"""
        namespace builtins{{
            {builtins}
        }}
        """
        self.code.append(code)

    def _make_user_code(self):
        user_code = self.biro.getCode()
        self.code.append("int main() {")
        code = self._make_statement_list(user_code)
        self.code.append(code)
        self.code.append("return 0; }")

    def _make_statement_list(self, statements):
        code = []
        for token in statements:
            # print("\t*\t", token)
            if token is None:
                continue
            Type = token[0]
            if isinstance(token, list):
                code.append(self._make_statement_list(token))
                continue
            elif Type not in self.type_func_mapping:
                # print("type:", Type)
                continue
            making_method = self.type_func_mapping[Type]
            code.append(making_method[0](token) + making_method[1])
        return "\n".join(code)

    def _make_variable_declaration(self, token):
        init = ""
        if token[1] == Scope().LOCAL:
            init = self.initialization[token[2]]
        code = f"{init} {self._make_assigned_expression(token[4], token[3])}"
        return code

    def _make_variable_assignment(self, token) -> None:
        code = self._make_assigned_expression(token[2], token[1])
        return code

    def _make_assigned_expression(self, expression, iden):
        if (
            hasattr(expression, "__getitem__")
            and expression[0] == "array_declaration"
        ):
            return self._make_array_declaration(expression[1], iden)
        elif (
            hasattr(expression, "__getitem__")
            and expression[0] == "queue_declaration"
        ):
            return self._make_queue_declaration(expression[1], iden)
        elif (
            hasattr(expression, "__getitem__")
            and expression[0] == "stack_declaration"
        ):
            return self._make_stack_declaration(expression[1], iden)
        else:
            return f"{iden} = {self._make_expression(expression)}"

    def _make_expression(self, expression):
        if isinstance(expression, (float, bool)):
            return str(expression).lower()
        if isinstance(expression, str):
            if expression[0] == expression[-1] == '"':
                return f"std::string({expression})"
            else:
                return expression
        if not isinstance(expression, tuple):
            print(expression)
            Error().show("Internal error while making expression")
            exit(1)
        if expression[0] == "builtin_call":
            return self._make_builtin_call(expression)
        if expression[0] == "function_call":
            return self._make_function_call(expression)
        else:
            p = {
                "equals": "==",
                "more": ">",
                "less": "<",
                "and": "&&",
                "or": "||",
            }
            symbol = expression[0]
            if symbol in p:
                symbol = p[symbol]
            return f"{self._make_expression(expression[1])} {symbol} {self._make_expression(expression[2])}"

    def _make_builtin_call(self, expression):
        return f"{self.namespace}::{self._make_function_call(expression[1])}"

    def _make_function_call(self, expression):
        # print(expression)
        return f"{expression[1]}({','.join([self._make_expression(i) for i in expression[2]])})"

    def _make_array_declaration(self, expression, iden):
        code = []
        for i in expression:
            code.append(f"{iden}.push_back({self._make_expression(i)});")
        return "\n".join(code)

    def _make_queue_declaration(self, expression, iden):
        code = []
        for i in expression:
            code.append(f"{iden}.push({self._make_expression(i)});")
        return "\n".join(code)

    def _make_stack_declaration(self, expression, iden):
        code = []
        for i in expression:
            code.append(f"{iden}.push({self._make_expression(i)});")
        return "\n".join(code)

    def _make_try_block(self, expression):
        return f"""
        try{{
            {self._make_statement_list(expression[1])}
        }}
        """

    def _make_catch_block(self, expression):
        return f"""
        catch(const std::exception& e){{
            {self._make_statement_list(expression[1])}
        }}
        """

    def _make_loop_statement(self, expression):
        return f"while(true){{ {self._make_control_flow_statements_list(expression[1])} }}"

    def _make_control_flow_statements_list(self, expression):
        code = []
        for i in expression:
            if isinstance(i, tuple):
                if i[0] == "leave":
                    code.append("break;")
                elif i[0] == "proceed":
                    code.append("continue;")
                elif i[0] == "donate_statement":
                    code.append(f"return {self._make_expression(i[1])};")
            else:
                code.append(self._make_statement_list(i))
        return "\n".join(code)

    def _make_conditional_statement(self, expression):
        return f"""
        if({self._make_expression(expression[1])}){{
            {self._make_control_flow_statements_list(expression[2])}
        }}
        """

    def _make_donate_statement(self, expression) -> str:
        return f"return {self._make_expression(expression[1])}"

    def getImplementation(self, file):
        file = os.path.abspath(os.path.join(self.implementation_path, file))
        if not os.path.exists(file) or not os.path.isfile(file):
            Error().show(f"Implementation error:\n\tFile {file} not found")
            exit(1)
        with open(file) as f:
            return f.read()

    def _builtin_say(self) -> str:
        return self.getImplementation("builtin_say.cpp")

    def _builtin_ask(self) -> str:
        return self.getImplementation("builtin_ask.cpp")

    def _builtin_index(self) -> str:
        return self.getImplementation("builtin_index.cpp")

    def _builtin_len(self) -> str:
        return self.getImplementation("builtin_len.cpp")
