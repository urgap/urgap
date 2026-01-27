
Contribution Guidelines
#######################


Summary
*******

In general, contribution to urgap is very welcome! Feel free to fork and/or clone
urgap. If you want to improve code or contribute new features/tools/algorithms
please read these guidelines first. If something is unclear please contact one
of the authors for help or let us know via e.g. an issue.

We are happy to include your name to the list of contributors in the `README`_.
Drop a line to one of the developers if you want to get included (and of course
you actually contributed something)

.. _README:
   https://github.com/fu/urgap2/blob/master/README.rst

Commit messages
***************

First of all, please be concise and as descriptive (explicit is better than
implicit :) ) as possible. It is always
helpful to point out, which parts of urgap were changed/fixed (e.g.
documentation or example scripts etc. ). At the same time, please avoid
unnecessarily long messages.
If possible, always use a headline in your commit message and list all changes as bullet points.


Code standards and conventions
******************************

Since this a collaborative project, you will encounter different coding styles.
Despite the fact that we know that diversity is beautiful, we need to keep some
common line on how to code (This list may be further extended). We generally use
black style (https://github.com/psf/black)
Additionally this list will give you some things to think about:

  | Re-think naming of variables at least twice
  | Re-check deleting of own debug code before sending Pull requests
  | Re-check own files created by nosetests and add it into '.gitignore' before sending Pull requests


Test philosophy
***************

Test your code! Seriously, test you code! If you add new functionality or nodes
at the same time provide (a) test function(s). We have already a set of tests
and different files, which can be used for the test. Avoid adding new test files
if possible to keep the repo small.


Sphinx guide
************

We use Sphinx to automatically build and format the documentation. Please keep
this style in your docstrings


Other rules and considerations
******************************

Please focus on contributing mainly source code and refrain from adding large files (e.g. mzML files).
For such files, please contact the urgap team so they can be committed by our labbot, which allows us
to keep the overview of code contributions neat and clean.

Merge/pull requests
*******************

Please use the pull request to push your code to the master repository. It will
be automatically tested github actions using tox if the module is still working in
unix environments. Pull requests will be discussed by the main dev
team and merged into urgap.


Issues
******

If you have an issue or problem, please first search all open issues and pull
request to avoid duplication of efforts. If you have a fix for the problem you
may directly open a pull request. On the other hand, if you plan to or
are already working on implementing new stuff, you may also open an issue and
(pre-) announce your contribution. Please tag then the issue with
'enhancement'. In general the core team of urgap will also take care of crucial
bugs in the main code. Since urgap is open source, we cannot maintain every detail
and assure its compatibility and functionality (please be reminded here to test
your code, seriously, test your code)


Citation
********

Be reminded that in an academic world citations are the only credit that one can hope for ;)
If you use urgap, do not forget to cite us

tba
