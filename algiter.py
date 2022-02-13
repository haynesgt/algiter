from dataclasses import dataclass
import itertools
import random
from typing import List, Callable

class Expr:
    pass

@dataclass
class Op:
    name: str
    precedence: int
    fn: Callable[[any], any]
    def compute(self, context, left, right):
        return self.fn(self, context, left, right)
    def __str__(self):
        return self.name

ADD = Op(name="+", precedence=0, fn=lambda self, context, left, right: left + right);
SUB = Op(name="-", precedence=0, fn=lambda self, context, left, right: left - right);
MUL = Op(name="*", precedence=1, fn=lambda self, context, left, right: left * right);
DIV = Op(name="/", precedence=1, fn=lambda self, context, left, right: left / right);

@dataclass
class BoolExpr:
    left: Expr
    right: Expr
    op: Op
    def compute(self, context):
        return self.op.compute(context, self.left.compute(context), self.right.compute(context))
    def __str__(self):
        return f"({self.left}){self.op}({self.right})"

@dataclass
class Symbol:
    index: int
    def compute(self, context):
        return context.get_symbol(self.index)
    def __str__(self):
        return chr(120 + self.index)

@dataclass
class Literal:
    value: float
    def compute(self, context):
        return self.value
    def __str__(self):
        return str(self.value)

def permutations(fn):
    left = fn()
    for i in itertools.count():
        next_left = next(left)
        right = fn()
        for j in range(i + 1):
            next_right = next(right)
            yield next_left, next_right
            if i != j:
                yield next_right, next_left

def algiter():
    index = 0
    subiters = None
    while True:
        # yield Literal(value=0.5 / (random.random() - 0.5))
        # yield Literal(value=random.random())
        if index < 4:
            yield Literal(value=index)
            if index > 0:
                yield Literal(value=-index)
        if index < 3:
            yield Symbol(index=index)
        index += 1
        if subiters == None:
            subiters = permutations(algiter)
        left, right = next(subiters)
        for op in (ADD, SUB, MUL, DIV):
            if isinstance(left, Literal) and isinstance(right, Literal):
                continue
            for l, r in ((left, right), (right, left)):
                if isinstance(l, Literal) and l.value == 0 and op in (ADD, SUB):
                    break
                if isinstance(l, Literal) and l.value == 1 and op == MUL:
                    break
                if isinstance(l, Literal) and l.value == 0 and op in (MUL, DIV):
                    break
                if l == r and op == SUB:
                    break
            else:
                if isinstance(right, Literal) and right.value == 1 and op == DIV:
                    continue
                else:
                    yield BoolExpr(left=left, op=op, right=right)


@dataclass
class Context:
    symbols: List[float]
    def get_symbol(self, i):
        return self.symbols[i]
    def compute(self, expr):
        try:
            return expr.compute(self)
        except:
            return None
    def __str__(self):
        return "Context(" + ",".join(f"{chr(120 + i)}={self.symbols[i]}" for i in range(len(self.symbols))) + ")"


def test():
    alg = algiter()
    context = Context(symbols=[random.randint(0, 1000) for i in range(3)])
    print(context)
    for i in range(0, 200):
        expr = next(alg)
        try:
            value = expr.compute(context)
        except:
            value = None
        print(expr, value)

if __name__ == "__main__":
    for left, right in permutations(algiter):
        if left == right:
            continue
        works = False
        same = True
        for i in range(0, 5):
            context = Context(symbols=[random.randint(0, 1000) for i in range(3)])
            left_value = context.compute(left)
            right_value = context.compute(right)
            if left_value != right_value:
                same = False
                break
            if left_value is not None:
                works = True
        if same:
            print(f"{left} = {right}")

