# JavaScript Object Graphs with Python

This Python module serializes and deserializes cyclic object graphs in the [JSOG format](https://github.com/simoneggler/jsog-python).

## Source code

The official repository is (https://github.com/simoneggler/jsog-python).

## Download

Jsog is available in PyPI:

    $ pip install jsog3

## Usage

This code mimics the standard *json* python package:

    import jsog33

	string = jsog3.dumps(cyclicGraph);
	cyclicGraph = jsog3.loads(string);

It can be used to convert between object graphs directly:

    import jsog3

	jsogStructure = jsog3.encode(cyclicGraph);	// has { '@ref': 'ID' } links instead of cycles
	cyclicGraph = jsog3.decode(jsogStructure);

## Author

* Jeff Schnitzer (jeff@infohazard.org)
* Simon Eggler (simon.eggler@gmx.net)

## License

This software is provided under the [MIT license](http://opensource.org/licenses/MIT)
