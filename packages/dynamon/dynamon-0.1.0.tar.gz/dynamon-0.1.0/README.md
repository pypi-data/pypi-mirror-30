# Python API for [dynamon.io](https://dynamon.io)

*Dynamon – Dynamic monitoring of real time data*


## Installing

```
pip install dynamon
```


## Using

### API

**`dynamon.push(x, y)`**<br>
Push data point `(x, y)` to graph. `x` defaults to current time.

**`dynamon.push(x, [y1, y2, ...])`**<br>
Push data points `(x, y<sub>i</sub>)` for multiple lines in one graph.
`x` defaults to current time.

**`dynamon.push('Hello world')`**<br>
Push plain text.

*All invocations of `dynamon.push` take an optional keyword argument `id='foo'` for use multiple graphs and text elements.*

**`dynamon.clear()`**<br>
Clear all graphs and text elements at `path`.

**`dynamon.path = 'my-unique-path`**<br>
Set the path for output: `https://dynamon.io/my-unique-path`. If not specified, a random path is generated.

See [dynamon.io](https://dynamon.io) for further details.


### Example

See [`test.py`](test.py) for an example.


## Technical details

This API caches `dynamon.push(..)` requests for `dynamon.cache_timeout` seconds
(defaulting to 1). After this time a batched http request is made with all
cached data. This is good for performance.
