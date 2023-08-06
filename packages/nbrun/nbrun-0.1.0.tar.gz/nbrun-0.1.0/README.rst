nbrun
=====

Runs Jupyter notebooks in parallel to verify that they are not raising any exceptions.

What for?
---------
When managing a data science project you need to confidently be able to refactor your shared code and notebook dependencies. Validating that all of your notebooks are still runnable helps gain confidence that they are still intact after such changes.

This script can be fired from a CI tool like Travis to ensure that future pull requests does not break your notebooks.

How to use?
-----------
The script searches recursively for :code:`.ipynb` within the specified path. Use :code:`--timeout` to limit the maximum time a notebook are allowed to run.
For example :code:`nbrun --timeout 60 ./notebooks` will run all notebooks found in the folder, but will timeout if any of the notebooks did not terminate after one minute.

Sometimes you don't want to run nbrun on specific notebooks. Suffixing notebook file names with a `_` will cause nbrun to skip this notebook file.
For example :code:`notebook_.ipynb` will not be ignored.
