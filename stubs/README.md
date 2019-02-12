This dir was used in an attempt to set up customized stub files for annotating e.g. Flask functions. Unfortunately, VSCode is proving rather fiddly, so this aspect of the codebase is being shelved indefinitely.

If you want to try and re-instate customize stubs, then you'll probably need to add sth like the following to the \_init_setup.sh script:

```bash
    ## Enable mypy stubs files to be found; see: https://github.com/python/mypy/wiki/Creating-Stubs-For-Python-Modules
    export MYPYPATH=$PWD/stubs
```
