__ONION_PROPS__

ONION_PROPS is a simple python module meant to simplify interaction with java .properties files. 
It provides the benefit of being able to parse properties hierarchically to provide a more robust way of storing and using properties.
Currently it provides the ability to:
 * load properties from a file (and interact with it as you would a normal dictionary)
 * interact (add/delete/edit) with properties
 * save properties to a file

ONION_PROPS also supports comments, you can specify whether or not to include comments within any interactor method as well as whether or not to include a timestamp.


USAGE:

To import base parser class:
```from onion_props.onion_props import PropParser```

NOTE:
To add properties to the parser object, it is advised that you also import:
```from onion_props.onion_props import Property, Properties```
As they are the custom data storage classes PropParser uses.
It is possible to add properties as standard dictionary key-values, but in order to add comments, you must import the `Property` class.


