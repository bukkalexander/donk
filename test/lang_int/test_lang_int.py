from unittest.mock import patch

from donk.lang_int.ast_nodes import main


def test_main():
    with patch("builtins.input", return_value="1337"):
        main()
