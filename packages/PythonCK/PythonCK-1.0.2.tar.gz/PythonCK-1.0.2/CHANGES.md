
> PythonCK: decorator @need_dir('somename', parent=True, mode='a', chdir=True)


> 161106: bug fix in memorized: It should acknowledge the filename too in case
  we have function of same name in different module.

FEATURES 
========

## decorator.AbstractClassbasedDecorator
- Migrate some complex stateful decorator to class-style instead
  - It can also be benefitting as TDD as well.
  - Need this: The class-based deco with instance-method is quite complex
    - https://christiankaula.com/python-decorate-method-gets-class-instance.html
  - Test-based caching revisit (after I migrated to class-base deco).
    - It's now much cleaner & nicer to write a unittest on this.
  - Note: This is slightly complicate due to the "optional deco args" problem.
    - First, this is almost completely independent signature.
    - Second, if I want to retain the deco to be class-based (e.g., for subclass
      of this deco), the previously use meta-deco won't suffice.
  - Solution: see new `AbstractClassbasedDecorator`, to be used as ABC.


## decorator.cache_to_file
- 150402: Report hit/miss rate at atexit
  - Pretty straight-forward, after migrated to class-based deco
  - same for lazy_algo_property
  - Remark: Use `__slots__` to ensure minimal footprint
- more practical isw/osw with boolean value.
  - `isw=False` will skip write if all(bool(i) is False for i in inputs)
- 150505 Question: Is my cache_to_file support nested call?
  - Use case: In MyGanga.IOUtils, it feels proper to batch the remote call 
    into one (best practice I learning from Google's). The hacking to cache
    LHCbDataset.getCatalogue seems appropriate to make a batch call, but 
    also as appropriate to cache those result indexed by single lfnuri.
  - My guess is it's fine. The cache's shelfid is made from func.__module__
    and func.__name__, so I should be able to get through...
  - Confirmed, it's fine. Key is made properly regardless the nesting context.
> Override cache
> early_giveup
> functools.wrap for class-based deco
  - The trick is in __slots__, variables not in there will be readonly
> The asynchorousity should be baked into cache_to_file directly
> cache-viewer
  > Goal: Be able to print-out a table, for each cached function. For example, 
    get_raw_list_LFN, a table with BKQ uri, date modified, num-of-lfn inside.
  - motivation: for `GangaCK` BKQ viewer
  - Not easy. Starting from hashkey, I cannot easily revert to original key
    for the sake of presentation.
  - If I want to store the original key into cache as well, the existing schema
    will need to be changed, and now I'll still caching accessURL of real 2012 
    data, I may have to come back to this later...
> fix input_skip_write, output_skip_write


## decorator.report
> report_pretty: Derived decorator from @report, don't show verbose result, 
  just say that this step is completed.


## ioutils
- Can `get_size` be smart about directory's date_modified? (For ganga PFN's size cache)
  - Possible: use `os.stat(path).st_mtime`

## itertools
- Enhanced classical Enum
  - Motivation:
    - 1. Avoid the hard-coded string check, e.g., tau.type == 'h1'.
    - 2. Slightly shorter syntax: --> tau.type.h1  # Return True
  - Feature:
    - The container (records all type) should still be subclass of tuple
    - The element (individual item) should be subclass of str
    - Backward-compat with previous impl
    - String op compat (e.g., tau.type.h1 + '_mu' == 'h1_mu')
    - Implemented, now part of MyPythonLib.Itertools. 


## logger
- 161104: Logger now support multiline and long-line wrapping.
- Disable rainbow on cluster (so that stderr via ganga is nicer)
  - Key trick: Use `SLURMD_NODENAME` and `SLURM_JOB_NAME` to determine the state.
  - Hmm, but that's strange. I can use rainbow alright in interactive session,
    but it doesn't work on the subjobs as workernodes...
- temporary disable logging, using context-statement.
  - Done, derive from capture_start, capture_stop I already made for Sepressle.
> whitelist & blacklist regex

--------------------------------------------------------------------------------

Changes History
===============

### 161010: Clean-up & packaging
- Refactored those related to Gaudi into another package. 
  Now, `PythonCK` should contain purely python utils, no `ROOT`, no Gaudi.
- Chose `GNU GPLv3` as license.
- start renaming submodule in lowercase. It's more standard.
- Fixing failed test
- Try packaging the project, the right way
  - https://jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/
  - setup.py
  - tox
- check how to sphinx + gitlab(wiki) --> hmm, perhaps not so possible...
- Update some test coverage
  - Move some small test case into doctest
- cleanup changes+issues
- git commit 
- Push to gitlab, private for now


