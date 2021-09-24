# Model design principle

* Please try to use structured data model as much as possible.
* Please think about the ownership of the data as early as possible.
  * In the future, we can share the editing authority of a data to others
* Please use external services as much as possible.

# Authentication
* Please use OAuth to simplify the registration procedure.

# Code quality
* Please introduce coding style as early as possible
  * PyCharm
  * autopep8
* Please introduce linter as early as possible
  * pylint
* Please introduce python typing as early as possible
  * source code
  * runtime check: mypy

# CI service
* GitHub Actions

# Development procedure
* First phase, R&D, EOD `undefined`:
  * commit the code to main branch and push it.
* Growth phase, boosting, EOD `undefined`:
  * create a pull request and send review.
  * create a lot of test cases to make sure the system is available.
