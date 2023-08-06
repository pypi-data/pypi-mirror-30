from lark import Lark
from xocver_lang.transformers import TreeTransformer
from xocver_lang.grammar import grammar


def eval_expr(expr, context=None):
    context = context or {}
    lark_parser = Lark(grammar, parser='earley', start='start', lexer='dynamic')
    tree = lark_parser.parse(expr)
    transformer = TreeTransformer(context)
    result = transformer.transform(tree)

    return result, transformer.vars
