from unittest.mock import patch

from donk.lang_int.ast_nodes import *


def test_main():
    with patch("builtins.input", return_value="1337"):
        main()


def test_ex_1_1(capsys):
    """
    Create three programs in the LInt language and test whether partially
    evaluating them with pe_Lint and then interpreting them with interp_Lint gives
    the same result as directly interpreting them with interp_Lint.
    """
    programs = [
        Module([Expr(Call(Name("print"), [UnaryOp(USub(), Constant(3))]))]),
        Module([Expr(Call(Name("print"), [BinOp(Constant(5), Add(), Constant(6))]))]),
        Module(
            [
                Expr(
                    Call(
                        Name("print"),
                        [
                            BinOp(
                                Constant(10),
                                Sub(),
                                UnaryOp(USub(), BinOp(Constant(5), Add(), Constant(6))),
                            )
                        ],
                    )
                )
            ]
        ),
    ]

    for idx, program in enumerate(programs, start=1):
        assert is_lang_int(program), f"Program #{idx} is not in lang_int."

        capsys.readouterr()  # clear any prior output
        interp_lang_int(program)
        direct_stdout = capsys.readouterr().out

        pe_program = pe_P_int(program)
        assert is_lang_int(pe_program), f"Partially evaluated program #{idx} is not in lang_int."

        interp_lang_int(pe_program)
        pe_stdout = capsys.readouterr().out
        assert direct_stdout == pe_stdout, (
            f"Program #{idx} changed its output after partial evaluation."
        )
