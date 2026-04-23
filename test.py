from src.nyang._02_parser import print_parse_line, parse_line
from src.nyang._01_lexer import print_lex_line, lex_line

nyanglang = input()

# print_lex_line(lex_line(nyanglang))
print_parse_line(parse_line(lex_line(nyanglang)))