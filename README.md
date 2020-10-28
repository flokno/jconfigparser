

jconfigparser
===

![python](https://img.shields.io/badge/python-3.6--3.8-informational.svg?style=flat)
[![pypi](https://img.shields.io/pypi/v/jconfigparser.svg?style=flat)](https://pypi.org/project/jconfigparser/)
![license](https://img.shields.io/pypi/l/jconfigparser.svg?color=red&style=flat)
[![code style](https://img.shields.io/badge/code%20style-black-202020.svg?style=flat)](https://github.com/ambv/black)

`jconfigparser` is an extension of the `python` `configparser` standard module which adds the following features inspired by [`TOML`](https://github.com/toml-lang/toml):

- Section name depth with dot notation: `[a.b]` 
- Values on right hand side can be everything that is understood by [JSON](https://www.json.org/json-en.html).
- Values that appear twice or more often are stored as a `list`, see example `output` below (this behavior is configurable).

## Example

Say we have the following configuration file in `test.jconf`:

```
[atoms]
file:                          geometry.in
format:                        aims

[calculator.aims]
xc:                            pbesol
charge_mix_param:              0.3
sc_accuracy_rho:               1e-6

output: band  0     0     0     0.00  0.25  0.25  50   Gamma  Delta
output: band  0.00  0.25  0.25  0     0.5   0.5   50   Delta  X

[calculator.socketio]
port:                          null

[basissets.aims]
default:                       light
```



This file can be parsed with

```python
import jconfigparser as jc

config = jc.Config('test.jconf')
```

`config` will be a modified `dict` that hold the information like

```python
{
    "atoms": {"file": "geometry.in", "format": "aims"},
    "calculator": {
        "aims": {
            "xc": "pbesol",
            "charge_mix_param": 0.3,
            "sc_accuracy_rho": 1e-06,
            "output": [
                "band  0     0     0     0.00  0.25  0.25  50   Gamma  Delta",
                "band  0.00  0.25  0.25  0     0.5   0.5   50   Delta  X",
            ],
        },
        "socketio": {"port": None},
    },
    "basissets": {"aims": {"default": "light"}},
}
```



Furthermore, `config` supports

* Attribute access, e.g., `config.atoms.file`
* Write itself: `config.write("new.jconf")`

## Changelog
- v0.1.3: per default, use case-sensitive keys
