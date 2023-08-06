
Build Requirements

Centos: 

	yum -y install npm gcc

Test
----

    make test

Overrides
---------

- `python` version:

        make PYTHON_VERSION='2.7.8' test
        make PYTHON_VERSION='2.7.8' virtualenv
- `pep8` options:

        make PEP8_OPTIONS='--max-line-length=120' python-pep8

If you have already downloaded the tarballs you need (Python and/or virtualenv) you can work offline like this:

    make ONLINE=false virtualenv
