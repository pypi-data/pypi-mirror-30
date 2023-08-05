Humilis plug-in to deploy an Autoscaling Group
===================================================

[![PyPI](https://img.shields.io/pypi/v/humilis-asg.svg?style=flat)](https://pypi.python.org/pypi/humilis-asg)

A [humilis][humilis] plug-in layer that deploys an Autoscaling Group. 

[humilis]: https://github.com/humilis/humilis


## Installation


```
pip install humilis-asg
```


To install the development version:

```
pip install git+https://github.com/humilis/humilis-asg
```


## Development

Assuming you have [virtualenv][venv] installed:

[venv]: https://virtualenv.readthedocs.org/en/latest/

```
make develop
```

Configure humilis:

```
make configure
```


## Testing

You can test the deployment with:

```
make test
```

If the tests break you can make sure you are not leaving any infrastructure
behind with:

```bash
make delete
```


## More information

See [humilis][humilis] documentation.

[humilis]: https://github.com//humilis/blob/master/README.md


## Contact

If you have questions, bug reports, suggestions, etc. please create an issue on
the [GitHub project page][github].

[github]: http://github.com/humilis/humilis-asg


## License

This software is licensed under the [MIT license][mit].

[mit]: http://en.wikipedia.org/wiki/MIT_License

See [License file][LICENSE].

[LICENSE]: https://github.com/humilis/humilis-asg/blob/master/LICENSE.txt


© 2017 German Gomez-Herrero, [Find Hotel][fh] and others.

[fh]: http://company.findhotel.net
