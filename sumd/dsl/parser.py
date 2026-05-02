"""DSL Parser for SUMD Domain Specific Language."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from enum import Enum


class DSLTokenType(Enum):
    """Token types for DSL parsing."""
    COMMAND = "COMMAND"
    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"
    OPERATOR = "OPERATOR"
    COMPARATOR = "COMPARATOR"
    LOGICAL = "LOGICAL"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    COMMA = "COMMA"
    DOT = "DOT"
    COLON = "COLON"
    PIPE = "PIPE"
    SEMICOLON = "SEMICOLON"
    NEWLINE = "NEWLINE"
    EOF = "EOF"
    WHITESPACE = "WHITESPACE"
    COMMENT = "COMMENT"


@dataclass
class DSLToken:
    """Token in DSL."""
    type: DSLTokenType
    value: str
    position: int = 0
    line: int = 1
    column: int = 1


class DSLLexer:
    """Lexer for tokenizing DSL expressions."""
    
    # Token patterns
    TOKEN_PATTERNS = [
        (DSLTokenType.COMMENT, r'#.*'),
        (DSLTokenType.STRING, r'"[^"]*"|\'[^\']*\''),
        (DSLTokenType.NUMBER, r'\d+\.?\d*'),
        (DSLTokenType.BOOLEAN, r'true|false'),
        (DSLTokenType.COMPARATOR, r'==|!=|<=|>=|<|>|contains|matches|startswith|endswith'),
        (DSLTokenType.LOGICAL, r'and|or|not'),
        (DSLTokenType.OPERATOR, r'\+|\-|\*|\/|\%|\*\*|\='),
        (DSLTokenType.LPAREN, r'\('),
        (DSLTokenType.RPAREN, r'\)'),
        (DSLTokenType.LBRACE, r'\{'),
        (DSLTokenType.RBRACE, r'\}'),
        (DSLTokenType.LBRACKET, r'\['),
        (DSLTokenType.RBRACKET, r'\]'),
        (DSLTokenType.COMMA, r','),
        (DSLTokenType.DOT, r'\.'),
        (DSLTokenType.COLON, r':'),
        (DSLTokenType.PIPE, r'\|'),
        (DSLTokenType.SEMICOLON, r';'),
        (DSLTokenType.NEWLINE, r'\n'),
        (DSLTokenType.WHITESPACE, r'[ \t\r]+'),
        (DSLTokenType.IDENTIFIER, r'[a-zA-Z_][a-zA-Z0-9_\-]*'),
    ]
    
    def __init__(self, text: str):
        self.text = text
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[DSLToken] = []
    
    def tokenize(self) -> List[DSLToken]:
        """Tokenize the input text."""
        while self.position < len(self.text):
            matched = False
            
            for token_type, pattern in self.TOKEN_PATTERNS:
                regex = re.compile(pattern)
                match = regex.match(self.text, self.position)
                
                if match:
                    value = match.group(0)
                    
                    # Skip whitespace and comments
                    if token_type not in [DSLTokenType.WHITESPACE, DSLTokenType.COMMENT]:
                        token = DSLToken(
                            type=token_type,
                            value=value,
                            position=self.position,
                            line=self.line,
                            column=self.column,
                        )
                        self.tokens.append(token)
                    
                    # Update position
                    self.position = match.end()
                    self.column += len(value)
                    
                    if token_type == DSLTokenType.NEWLINE:
                        self.line += 1
                        self.column = 1
                    
                    matched = True
                    break
            
            if not matched:
                raise ValueError(f"Unexpected character at line {self.line}, column {self.column}: {self.text[self.position]}")
        
        # Add EOF token
        self.tokens.append(DSLToken(
            type=DSLTokenType.EOF,
            value="",
            position=self.position,
            line=self.line,
            column=self.column,
        ))
        
        return self.tokens


class DSLExpressionType(Enum):
    """Types of DSL expressions."""
    COMMAND = "COMMAND"
    ASSIGNMENT = "ASSIGNMENT"
    COMPARISON = "COMPARISON"
    LOGICAL = "LOGICAL"
    ARITHMETIC = "ARITHMETIC"
    FUNCTION_CALL = "FUNCTION_CALL"
    PROPERTY_ACCESS = "PROPERTY_ACCESS"
    LITERAL = "LITERAL"
    IDENTIFIER = "IDENTIFIER"
    PIPELINE = "PIPELINE"
    BLOCK = "BLOCK"
    LIST = "LIST"
    DICT = "DICT"


@dataclass
class DSLExpression:
    """Expression in DSL."""
    type: DSLExpressionType
    value: Any
    children: List[DSLExpression] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """String representation of the expression."""
        if self.type == DSLExpressionType.COMMAND:
            args = " ".join(str(child) for child in self.children)
            return f"{self.value} {args}"
        elif self.type == DSLExpressionType.FUNCTION_CALL:
            args = ", ".join(str(child) for child in self.children)
            return f"{self.value}({args})"
        elif self.type == DSLExpressionType.PROPERTY_ACCESS:
            if self.children:
                return f"{self.value}.{str(self.children[0])}"
            return str(self.value)
        elif self.type == DSLExpressionType.LITERAL:
            return str(self.value)
        elif self.type == DSLExpressionType.IDENTIFIER:
            return str(self.value)
        elif self.type == DSLExpressionType.PIPELINE:
            return " | ".join(str(child) for child in self.children)
        else:
            return str(self.value)


class DSLParser:
    """Parser for DSL expressions."""
    
    def __init__(self, tokens: List[DSLToken]):
        self.tokens = tokens
        self.current = 0
    
    def parse(self) -> DSLExpression:
        """Parse tokens into DSL expression."""
        if not self.tokens:
            raise ValueError("No tokens to parse")
        
        expressions = []
        
        while not self._is_at_end():
            expr = self._parse_statement()
            if expr:
                expressions.append(expr)
            
            # Skip semicolons
            if self._match(DSLTokenType.SEMICOLON):
                continue
        
        # If single expression, return it directly
        if len(expressions) == 1:
            return expressions[0]
        
        # Otherwise return a block
        return DSLExpression(
            type=DSLExpressionType.BLOCK,
            value="block",
            children=expressions,
        )
    
    def _parse_statement(self) -> Optional[DSLExpression]:
        """Parse a statement."""
        # Skip empty lines
        if self._match(DSLTokenType.NEWLINE):
            return None
        
        # Parse pipeline or command
        expr = self._parse_pipeline()
        
        # Skip trailing newline
        self._match(DSLTokenType.NEWLINE)
        
        return expr
    
    def _parse_pipeline(self) -> DSLExpression:
        """Parse a pipeline expression."""
        left = self._parse_assignment()
        
        if self._match(DSLTokenType.PIPE):
            right = self._parse_pipeline()
            return DSLExpression(
                type=DSLExpressionType.PIPELINE,
                value="|",
                children=[left, right],
            )
        
        return left
    
    def _parse_assignment(self) -> DSLExpression:
        """Parse assignment expression."""
        if self._check(DSLTokenType.IDENTIFIER) and self._check_next(DSLTokenType.OPERATOR, "="):
            identifier = self._advance()
            self._advance()  # Skip '='
            value = self._parse_logical_or()
            
            return DSLExpression(
                type=DSLExpressionType.ASSIGNMENT,
                value="=",
                children=[
                    DSLExpression(type=DSLExpressionType.IDENTIFIER, value=identifier.value),
                    value,
                ],
            )
        
        return self._parse_logical_or()
    
    def _parse_logical_or(self) -> DSLExpression:
        """Parse logical OR expression."""
        left = self._parse_logical_and()
        
        while self._match(DSLTokenType.LOGICAL, "or"):
            operator = self._previous()
            right = self._parse_logical_and()
            
            left = DSLExpression(
                type=DSLExpressionType.LOGICAL,
                value=operator.value,
                children=[left, right],
            )
        
        return left
    
    def _parse_logical_and(self) -> DSLExpression:
        """Parse logical AND expression."""
        left = self._parse_comparison()
        
        while self._match(DSLTokenType.LOGICAL, "and"):
            operator = self._previous()
            right = self._parse_comparison()
            
            left = DSLExpression(
                type=DSLExpressionType.LOGICAL,
                value=operator.value,
                children=[left, right],
            )
        
        return left
    
    def _parse_comparison(self) -> DSLExpression:
        """Parse comparison expression."""
        left = self._parse_arithmetic()
        
        if self._match(DSLTokenType.COMPARATOR):
            operator = self._previous()
            right = self._parse_arithmetic()
            
            return DSLExpression(
                type=DSLExpressionType.COMPARISON,
                value=operator.value,
                children=[left, right],
            )
        
        return left
    
    def _parse_arithmetic(self) -> DSLExpression:
        """Parse arithmetic expression."""
        left = self._parse_term()
        
        while self._match(DSLTokenType.OPERATOR, "+") or self._match(DSLTokenType.OPERATOR, "-"):
            operator = self._previous()
            right = self._parse_term()
            
            left = DSLExpression(
                type=DSLExpressionType.ARITHMETIC,
                value=operator.value,
                children=[left, right],
            )
        
        return left
    
    def _parse_term(self) -> DSLExpression:
        """Parse term expression."""
        left = self._parse_factor()
        
        while self._match(DSLTokenType.OPERATOR, "*") or self._match(DSLTokenType.OPERATOR, "/") or self._match(DSLTokenType.OPERATOR, "%"):
            operator = self._previous()
            right = self._parse_factor()
            
            left = DSLExpression(
                type=DSLExpressionType.ARITHMETIC,
                value=operator.value,
                children=[left, right],
            )
        
        return left
    
    def _parse_factor(self) -> DSLExpression:
        """Parse factor expression."""
        if self._match(DSLTokenType.OPERATOR, "-"):
            operator = self._previous()
            right = self._parse_factor()
            
            return DSLExpression(
                type=DSLExpressionType.ARITHMETIC,
                value=operator.value,
                children=[right],
            )
        
        if self._match(DSLTokenType.LOGICAL, "not"):
            operator = self._previous()
            right = self._parse_factor()
            
            return DSLExpression(
                type=DSLExpressionType.LOGICAL,
                value=operator.value,
                children=[right],
            )
        
        return self._parse_primary()
    
    def _parse_primary(self) -> DSLExpression:
        """Parse primary expression."""
        # Parenthesized expression
        if self._match(DSLTokenType.LPAREN):
            expr = self._parse_pipeline()
            self._consume(DSLTokenType.RPAREN, "Expected ')' after expression.")
            return expr
        
        # List literal
        if self._match(DSLTokenType.LBRACKET):
            return self._parse_list()
        
        # Dictionary literal
        if self._match(DSLTokenType.LBRACE):
            return self._parse_dict()
        
        # Function call
        if self._check(DSLTokenType.IDENTIFIER) and self._check_next(DSLTokenType.LPAREN):
            return self._parse_function_call()
        
        # Property access
        if self._check(DSLTokenType.IDENTIFIER) and self._check_next(DSLTokenType.DOT):
            return self._parse_property_access()
        
        # Command (check if it's a standalone identifier)
        if self._check(DSLTokenType.IDENTIFIER):
            # Look ahead to see if this is a command (end of expression or followed by operator)
            current_pos = self.current
            identifier = self._advance()
            
            # If this is the end of the expression or followed by operators, it's a command
            if (self._is_at_end() or 
                self._check(DSLTokenType.NEWLINE) or 
                self._check(DSLTokenType.EOF) or
                self._check(DSLTokenType.SEMICOLON) or
                self._check(DSLTokenType.PIPE)):
                
                return DSLExpression(
                    type=DSLExpressionType.COMMAND,
                    value=identifier.value,
                    children=[],
                )
            
            # Otherwise, treat as variable/identifier
            return DSLExpression(
                type=DSLExpressionType.IDENTIFIER,
                value=identifier.value,
            )
        
        # Literal
        if self._match(DSLTokenType.STRING):
            value = self._previous().value
            # Remove quotes
            return DSLExpression(
                type=DSLExpressionType.LITERAL,
                value=value[1:-1],
                metadata={"type": "string"},
            )
        
        if self._match(DSLTokenType.NUMBER):
            value = self._previous().value
            if "." in value:
                return DSLExpression(
                    type=DSLExpressionType.LITERAL,
                    value=float(value),
                    metadata={"type": "float"},
                )
            else:
                return DSLExpression(
                    type=DSLExpressionType.LITERAL,
                    value=int(value),
                    metadata={"type": "int"},
                )
        
        if self._match(DSLTokenType.BOOLEAN):
            value = self._previous().value
            return DSLExpression(
                type=DSLExpressionType.LITERAL,
                value=value == "true",
                metadata={"type": "bool"},
            )
        
        if self._check(DSLTokenType.IDENTIFIER):
            identifier = self._advance()
            return DSLExpression(
                type=DSLExpressionType.IDENTIFIER,
                value=identifier.value,
            )
        
        raise ValueError(f"Unexpected token: {self._peek().value}")
    
    def _parse_command(self) -> DSLExpression:
        """Parse command expression."""
        command = self._advance()
        args = []
        
        while not self._is_at_end() and not self._check(DSLTokenType.NEWLINE) and not self._check(DSLTokenType.SEMICOLON) and not self._check(DSLTokenType.PIPE):
            if self._check(DSLTokenType.EOF):
                break
            
            arg = self._parse_primary()
            args.append(arg)
        
        return DSLExpression(
            type=DSLExpressionType.COMMAND,
            value=command.value,
            children=args,
        )
    
    def _parse_function_call(self) -> DSLExpression:
        """Parse function call expression."""
        identifier = self._advance()
        self._consume(DSLTokenType.LPAREN, "Expected '(' after function name.")
        
        args = []
        if not self._check(DSLTokenType.RPAREN):
            args.append(self._parse_pipeline())
            while self._match(DSLTokenType.COMMA):
                args.append(self._parse_pipeline())
        
        self._consume(DSLTokenType.RPAREN, "Expected ')' after arguments.")
        
        return DSLExpression(
            type=DSLExpressionType.FUNCTION_CALL,
            value=identifier.value,
            children=args,
        )
    
    def _parse_property_access(self) -> DSLExpression:
        """Parse property access expression."""
        identifier = self._advance()
        self._advance()  # Skip '.'
        property_name = self._advance()
        
        return DSLExpression(
            type=DSLExpressionType.PROPERTY_ACCESS,
            value=identifier.value,
            children=[
                DSLExpression(type=DSLExpressionType.IDENTIFIER, value=property_name.value)
            ],
        )
    
    def _parse_list(self) -> DSLExpression:
        """Parse list literal."""
        items = []
        
        if not self._check(DSLTokenType.RBRACKET):
            items.append(self._parse_pipeline())
            while self._match(DSLTokenType.COMMA):
                items.append(self._parse_pipeline())
        
        self._consume(DSLTokenType.RBRACKET, "Expected ']' after list items.")
        
        return DSLExpression(
            type=DSLExpressionType.LIST,
            value="list",
            children=items,
        )
    
    def _parse_dict(self) -> DSLExpression:
        """Parse dictionary literal."""
        items = []
        
        if not self._check(DSLTokenType.RBRACE):
            # Parse key: value pairs
            key = self._parse_primary()
            self._consume(DSLTokenType.COLON, "Expected ':' after dictionary key.")
            value = self._parse_pipeline()
            items.append((key, value))
            
            while self._match(DSLTokenType.COMMA):
                key = self._parse_primary()
                self._consume(DSLTokenType.COLON, "Expected ':' after dictionary key.")
                value = self._parse_pipeline()
                items.append((key, value))
        
        self._consume(DSLTokenType.RBRACE, "Expected '}' after dictionary items.")
        
        return DSLExpression(
            type=DSLExpressionType.DICT,
            value="dict",
            metadata={"items": items},
        )
    
    # Helper methods
    def _is_at_end(self) -> bool:
        """Check if we're at the end of tokens."""
        return self._peek().type == DSLTokenType.EOF
    
    def _peek(self) -> DSLToken:
        """Get current token without consuming it."""
        return self.tokens[self.current]
    
    def _previous(self) -> DSLToken:
        """Get previous token."""
        return self.tokens[self.current - 1]
    
    def _advance(self) -> DSLToken:
        """Consume and return current token."""
        if not self._is_at_end():
            self.current += 1
        return self._previous()
    
    def _check(self, token_type: DSLTokenType, value: Optional[str] = None) -> bool:
        """Check current token type and optionally value."""
        if self._is_at_end():
            return False
        token = self._peek()
        if token.type != token_type:
            return False
        if value is not None and token.value != value:
            return False
        return True
    
    def _check_next(self, token_type: DSLTokenType, value: Optional[str] = None) -> bool:
        """Check next token type and optionally value."""
        if self.current + 1 >= len(self.tokens):
            return False
        token = self.tokens[self.current + 1]
        if token.type != token_type:
            return False
        if value is not None and token.value != value:
            return False
        return True
    
    def _match(self, token_type: DSLTokenType, value: Optional[str] = None) -> bool:
        """Match and consume token if it matches."""
        if self._check(token_type, value):
            self._advance()
            return True
        return False
    
    def _consume(self, token_type: DSLTokenType, message: str) -> DSLToken:
        """Consume token or raise error."""
        if self._check(token_type):
            return self._advance()
        raise ValueError(f"{message} Got {self._peek().value} instead.")


def parse_dsl(text: str) -> DSLExpression:
    """Parse DSL text into expression."""
    lexer = DSLLexer(text)
    tokens = lexer.tokenize()
    parser = DSLParser(tokens)
    return parser.parse()
