# Lang int

## Concrete syntax

```bnf
exp ::= int
exp ::= input_int()
exp ::= -exp
exp ::= exp1 + exp2
exp ::= exp1 - exp2

stmt ::= print(exp)
stmt ::= exp

LInt ::= stmt∗

The asterisk (∗) indicates a list of statements
```


## Abstract syntax

```bnf
exp ::= Constant(int)
exp ::= Call(Name('input_int'),[])
exp ::= UnaryOp(USub(),exp)
exp ::= BinOp(exp,Add(),exp)
exp ::= BinOp(exp,Sub(),exp)

stmt ::= Expr(Call(Name('print'),[exp]))
stmt ::= Expr(exp)

LInt ::= Module(stmt∗)

The asterisk (∗) indicates a list of statements
```
