Guesslang documentation
=======================

Guesslang detects the programming language of a given source code:

.. code-block:: python

  from guesslang import Guess


  name = Guess().language_name("""
      % Quick sort

    	-module (recursion).
    	-export ([qsort/1]).

    	qsort([]) -> [];
    	qsort([Pivot|T]) ->
    	       qsort([X || X <- T, X < Pivot])
    	       ++ [Pivot] ++
    	       qsort([X || X <- T, X >= Pivot]).
  """)

  print(name)  # >>> Erlang

Guesslang supports ``20 programming languages``:

+-------------+-------------+-------------+-------------+-------------+
| C           | C#          | C++         | CSS         | Erlang      |
+-------------+-------------+-------------+-------------+-------------+
| Go          | HTML        | Java        | Javascript  | Markdown    |
+-------------+-------------+-------------+-------------+-------------+
| Objective-C | PHP         | Perl        | Python      | Ruby        |
+-------------+-------------+-------------+-------------+-------------+
| Rust        | SQL         | Scala       | Shell       | Swift       |
+-------------+-------------+-------------+-------------+-------------+

The current ``guessing accuracy is higher than 90%``.

You can contribute to Guesslang on Github
`<https://github.com/yoeo/guesslang>`_.

Full documentation at https://guesslang.readthedocs.io/en/latest/

