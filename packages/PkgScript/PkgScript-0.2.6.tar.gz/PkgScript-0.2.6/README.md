# pkgscript (version 0.2)

Python module that allows a packaged module to run properly as a script. 

It imports the enclosing package(s) into the script, allowing the script to 
import other modules from the same package family (using explicit relative or 
absolute import statements).

**!!!  
`import_parent_packages()` must be called before any package-sibling imports  
!!!**


## Examples:

```python
### Milo.mod_script.py
import pkgscript
# Only call function if module is being run as a script
if (__name__ == "__main__") and (__package__ is None):
    pkgscript.import_parent_packages("Milo")
from Milo.version import __version__
from .version import __version__    # same as previous line
```
```python
### top_pkg.sub_pkg.sub_sub_pkg.mod_script.py
import pkgscript
# Only call function if module is being run as a script
if (__name__ == "__main__") and (__package__ is None):
    pkgscript.import_parent_packages("top_pkg.sub_pkg.sub_sub_pkg")
# Import top_pkg.sub_pkg.other_module
from top_pkg.sub_pkg import other_module
from .. import other_module    # same as previous line
from ...sub_pkg import other_module    # same as previous line
```

## Credits

This software is adapted from helpful code posted by @vaultah  
    (https://gist.github.com/vaultah/d63cb4c86be2774377aa674b009f759a)  
    in response to a question on Stack Overflow  
    (https://stackoverflow.com/a/28154841/9639441)


## License

This software is released under The MIT License (MIT).

_Copyright (c) 2018, Padraic Shafer_

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.