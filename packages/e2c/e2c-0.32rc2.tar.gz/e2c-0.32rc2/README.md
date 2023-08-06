<div align="center">
    <img src="../../images/e2c-logo.png"><br><br>
</div>
<br>

| **`Documentation`** | **`Master`** | **`Develop`** | **`Tests`** |
|---------------------|--------------|---------------|-------------|
| [![docs](https://readthedocs.org/projects/e2c/badge/?version=latest)](http://e2c.readthedocs.io/en/latest) | [![pipeline status](https://gitlab.com/elastic-event-components/e2c/badges/master/pipeline.svg)](https://gitlab.com/elastic-event-components/e2c/master/develop) | [![pipeline status](https://gitlab.com/elastic-event-components/e2c/badges/develop/pipeline.svg)](https://gitlab.com/elastic-event-components/e2c/commits/develop) | [![coverage report](https://gitlab.com/elastic-event-components/e2c/badges/develop/coverage.svg)](https://gitlab.com/elastic-event-components/e2c/commits/develop) |

<br>

# E2C.py - Elastic Event Components for Python

**Elastic Event Components** is an open source software library to build flexible architectures using
dataflow graphs. A graph node represents any operation, while the graph edges represent the parameters
of the operation. Each parameter can be bound to any number of operations and thus brought 
into a flow. Elastic Event Components also includes flow visualization.
<br>
<br>
Through E2C, processes and software architectures can be visualized by dataflow graphs, 
which can be converted into executable applications. **Functional dependencies can be defused** 
by E2C and thus significantly increase the changeability and quality of 
components and software projects.

## Installation
*See [Installing E2C](../../INSTALL.md) for instructions
on how to build from source.*

#### *Try your first E2C program*

```shell
$ python
```

```python
>>> import e2c

>>> config = (
... '.run -- action',
... 'action.render -- render',
... '   render.out -- .out',
... 'action.log -- log',
... '   log.store -- .out')

>>> def action(data: str, render, log):
...    render(data)
...    log('Render done!')

>>> graph = e2c.Graph[str, str](config)
>>> graph.actor('action', action)
>>> graph.actor('render', lambda dat, out: out(dat))
>>> graph.actor('log', lambda dat, store: store(dat))

>>> graph.visualize()
>>> graph.run_continues('Hello, E2C', print)

Hello, E2C
Render done!
```

<div align="center">
  <img src="../../images/quickstart.png"><br><br>
</div>

## For more information
* [E2C website](http://e2c.readthedocs.io/en/latest/)

## License
[Apache 2.0 License](LICENSE)
