import ply.lex as lex
import ply.yacc as yacc
from biro.middleware import Scope, Error, BiroIntermediateCode


class Parser(object):
    reserved = {
        "biro": "BIRO",
        "smallbiro": "SMALLBIRO",
        "is": "IS",
        "equals": "EQUALS",
        "more": "MORE",
        "less": "LESS",
        "donate": "DONATE",
        "proceed": "PROCEED",
        "leave": "LEAVE",
        "loop": "LOOP",
        "attempt": "ATTEMPT",
        "arrest": "ARREST",
        "and": "AND",
        "or": "OR",
        "true": "TRUE",
        "false": "FALSE",
        "num": "NUM",
        "str": "STR",
        "bool": "BOOL",
    }

    tokens = (
        "ID",
        "STRING",
        "NUMBER",
        "LPAREN",
        "RPAREN",
        "LCURL",
        "RCURL",
        "DOT",
        "PLUS",
        "MINUS",
        "ASTERISK",
        "DIVIDE",
        "QUESMARK",
        "COMMA",
        "LSQUARE",
        "RSQUARE",
        "ASSIGN",
        "LITERAL_A",
        "LITERAL_Q",
        "LITERAL_S",
        "COLON",
        *reserved.values(),
    )

    precedence = (
        ("nonassoc", "LESS", "MORE", "EQUALS"),
        ("left", "PLUS", "MINUS"),
        ("left", "ASTERISK", "DIVIDE"),
        ("nonassoc", "ASSIGN"),
        ("left", "AND", "OR"),
    )

    # Regular expression rules for simple tokens
    def t_ID(self, t):
        r"[a-zA-Z_][a-zA-Z_0-9]*(?!\[)"
        t.type = self.reserved.get(t.value, "ID")
        if t.type == "TRUE":
            t.value = True
        elif t.type == "FALSE":
            t.value = False
        return t

    def t_STRING(self, t):
        r'"[^"]*"'
        return t

    def t_NUMBER(self, t):
        r"[+-]?([0-9]*[.])?[0-9]+"
        t.value = float(t.value)
        return t

    t_LITERAL_A = r"a(?=\[)"
    t_LITERAL_Q = r"q(?=\[)"
    t_LITERAL_S = r"s(?=\[)"

    t_LPAREN = r"\("
    t_RPAREN = r"\)"
    t_LCURL = r"{"
    t_RCURL = r"}"
    t_DOT = r"\."
    t_PLUS = r"\+"
    t_MINUS = r"-"
    t_ASTERISK = r"\*"
    t_DIVIDE = r"/"
    t_QUESMARK = r"\?"
    t_COMMA = r","
    t_LSQUARE = r"\["
    t_RSQUARE = r"\]"
    t_ASSIGN = r"="
    t_EQUALS = r"=="
    t_MORE = r">"
    t_LESS = r"<"
    t_COLON = r":"

    t_ignore_COMMENT = r"\/\/.*"

    def t_newline(self, t):
        r"\n+"
        t.lexer.lineno += len(t.value)

    # Ignored characters
    t_ignore = " \t"

    # Error handling rule
    def t_error(self, t):
        print(f"Illegal character '{t.value[0]}'")
        t.lexer.skip(1)

    # PLY Productions

    # Program
    def p_program(self, p):
        "program : statement_list"
        p[0] = p[1]

    # Statement List
    def p_statement_list(self, p):
        """statement_list : statement statement_list
        | statement"""
        if len(p) == 3:
            p[0] = [p[1]] + p[2]
        else:
            p[0] = [p[1]]

    # Statement
    def p_statement(self, p):
        """statement : variable_declaration
        | variable_assignment
        | conditional_statement
        | array_declaration
        | queue_declaration
        | stack_declaration
        | try_block
        | catch_block
        | loop_statement
        | function_declaration
        | function_call
        | builtin_call
        | empty"""
        p[0] = p[1]

    # Variable Declaration
    def p_variable_declaration(self, p):
        """variable_declaration : BIRO ID COLON type ASSIGN assigned_expression
        | SMALLBIRO ID COLON type ASSIGN assigned_expression"""
        if p[1] == "biro":
            scope = Scope.GLOBAL
            self.biro.setGlobal(p[2], p[4], p.lineno(2), p.lexpos(2))
        else:
            scope = Scope.LOCAL
        p[0] = ("variable_declaration", scope, p[4], p[2], p[6])

    # Variable Assignment
    def p_variable_assignment(self, p):
        """variable_assignment : ID ASSIGN assigned_expression"""
        p[0] = ("variable_assignment", p[1], p[3])

    # Assigned Expression
    def p_assigned_expression(self, p):
        """assigned_expression : expression
        | array_declaration
        | queue_declaration
        | stack_declaration"""
        p[0] = p[1]

    # Array Declaration
    def p_array_declaration(self, p):
        """array_declaration : LITERAL_A LSQUARE expression_list RSQUARE"""
        p[0] = ("array_declaration", p[3])

    # Queue Declaration
    def p_queue_declaration(self, p):
        """queue_declaration : LITERAL_Q LSQUARE expression_list RSQUARE"""
        p[0] = ("queue_declaration", p[3])

    # Stack Declaration
    def p_stack_declaration(self, p):
        """stack_declaration : LITERAL_S LSQUARE expression_list RSQUARE"""
        p[0] = ("stack_declaration", p[3])

    # Conditional Statement
    def p_conditional_statement(self, p):
        """conditional_statement : BIRO IS expression QUESMARK LCURL control_flow_statements_list RCURL"""
        p[0] = ("conditional_statement", p[3], p[6])

    # Try Block
    def p_try_block(self, p):
        """try_block : BIRO ATTEMPT LCURL statement_list RCURL"""
        p[0] = ("try_block", p[4])

    # Catch Block
    def p_catch_block(self, p):
        """catch_block : BIRO ARREST LCURL statement_list RCURL"""
        p[0] = ("catch_block", p[4])

    # Loop Block
    def p_loop_statement(self, p):
        """loop_statement : BIRO LOOP LCURL control_flow_statements_list RCURL"""
        p[0] = ("loop_statement", p[4])

    # Function Declaration
    def p_function_declaration(self, p):
        """function_declaration : BIRO ID LPAREN arg_list RPAREN COLON LPAREN type_list RPAREN LCURL donate_statement_list RCURL"""
        if len(p[4]) == len(p[8]):
            return_type = "void"
        elif len(p[4]) - len(p[8]) == -1:
            return_type = p[8].pop()
        else:
            Error().show(
                f"Not all types are defined for {p[2]}({','.join(p[4])}) function"
            )
            exit(1)
        self.biro.setFunc(
            name=p[2],
            arg_names=p[4],
            arg_type=p[8],
            return_type=return_type,
            block=p[11],
        )
        p[0] = ("function_declaration", p[2], p[4], p[8], p[11])

    # Function Call
    def p_function_call(self, p):
        """function_call : ID LPAREN expression_list RPAREN"""
        p[0] = ("function_call", p[1], p[3])

    # Builtin Call
    def p_builtin_call(self, p):
        """builtin_call : BIRO DOT function_call"""
        p[0] = ("builtin_call", p[3])

    # Donate Statement List
    def p_donate_statement_list(self, p):
        """donate_statement_list : donate_statement donate_statement_list
        | donate_statement"""
        if len(p) == 3:
            p[0] = [p[1]] + p[2]
        else:
            p[0] = [p[1]]

    # Donate Statement
    def p_donate_statement(self, p):
        """donate_statement : statement_list
        | DONATE expression"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ("donate_statement", p[2])

    # Control Flow Statements List
    def p_control_flow_statements_list(self, p):
        """control_flow_statements_list : control_flow_statements control_flow_statements_list
        | control_flow_statements"""
        if len(p) == 3:
            p[0] = [p[1]] + p[2]
        else:
            p[0] = [p[1]]

    # Control Flow Statements
    def p_control_flow_statements(self, p):
        """control_flow_statements : statement_list
        | LEAVE
        | PROCEED
        | DONATE expression"""
        if p[1] == "leave":
            p[0] = ("leave",)
        elif p[1] == "proceed":
            p[0] = ("proceed",)
        elif p[1] == "donate":
            p[0] = ("donate_statement", p[2])
        else:
            p[0] = p[1]

    # Expression
    def p_expression(self, p):
        """expression : ID
        | STRING
        | NUMBER
        | TRUE
        | FALSE
        | builtin_call
        | function_call
        | expression PLUS expression
        | expression MINUS expression
        | expression ASTERISK expression
        | expression DIVIDE expression
        | expression EQUALS expression
        | expression MORE expression
        | expression LESS expression
        | expression AND expression
        | expression OR expression"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = (p[2], p[1], p[3])

    # Expression List
    def p_expression_list(self, p):
        """expression_list : expression COMMA expression_list
        | expression
        | empty"""
        if len(p) == 4:
            p[0] = [p[1]] + p[3]
        else:
            p[0] = [p[1]]

    # Argument List
    def p_arg_list(self, p):
        """arg_list : ID COMMA arg_list
        | ID
        | empty"""
        if len(p) == 4:
            p[0] = [p[1]] + p[3]
        else:
            p[0] = [p[1]]

    # Type List
    def p_type_list(self, p):
        """type_list : type COMMA type_list
        | type
        | empty"""
        if len(p) == 4:
            p[0] = [p[1]] + p[3]
        else:
            p[0] = [p[1]]

    # Type
    def p_type(self, p):
        """type : NUM
        | STR
        | BOOL
        | LITERAL_A LSQUARE NUM RSQUARE
        | LITERAL_A LSQUARE STR RSQUARE
        | LITERAL_A LSQUARE BOOL RSQUARE
        | LITERAL_Q LSQUARE NUM RSQUARE
        | LITERAL_Q LSQUARE STR RSQUARE
        | LITERAL_Q LSQUARE BOOL RSQUARE
        | LITERAL_S LSQUARE NUM RSQUARE
        | LITERAL_S LSQUARE STR RSQUARE
        | LITERAL_S LSQUARE BOOL RSQUARE"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = (p[1], p[3])

    # Empty
    def p_empty(self, p):
        """empty :"""
        pass

    # Error
    def p_error(self, p):
        Error().parsing(p)
        exit(1)

    def __init__(self):
        self.biro = BiroIntermediateCode()
        self.lexer = lex.lex(module=self)
        self.parser = yacc.yacc(module=self)

    def parse(self, code):
        self.biro.setCode(self.parser.parse(code))
