# dds_pylib

## Diversified Data Python Helper Library

### List of available utilities

1. dates
    1. classes
        1. Gregorian()
    1. functions
        1. todays_julian()
        1. gregorian2julian()
        1. julian2gregorian()
1. pyext
    1. objects
        1. ObjectDict

### Running Tests

Change current directory to library base directory

Run all tests. This will run all the test*.py modules inside the test package.

```console
> python -m unittest discover -v
test_decode (test.test_base.TestBase36) ... ok
test_encode (test.test_base.TestBase36) ... ok
test_gregorian (test.test_dates.TestGregorian) ... ok
test_j2g (test.test_dates.TestJulian2Gregorian) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.011s

OK
```

Limit tests to a specific test module

```console
> python -m unittest test.test_dates
..
----------------------------------------------------------------------
Ran 2 tests in 0.004s

OK
```

Add `-v` switch to makes output more verbose

```console
> python -m unittest -v test.test_dates
test_gregorian (test.test_dates.TestGregorian) ... ok
test_j2g (test.test_dates.TestJulian2Gregorian) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.007s

OK
```

Further limit test to a specific TestCase

```console
> python -m unittest -v test.test_dates.TestGregorian
test_gregorian (test.test_dates.TestGregorian) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.005s

OK
```

Optionally further limit test to a specific TestCase.method

```console
> python -m unittest -v test.test_dates.TestGregorian.test_gregorian
test_gregorian (test.test_dates.TestGregorian) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.004s

OK
```

#### This library should test full tested
