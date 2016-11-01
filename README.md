# grid-garage-3
ArcGIS python toolbox supporting table-based processing.

The toolbox is being developed under ArcGIS 10.4. It appears to load Ok in 10.1 (10.2, 10.3 unavailable) but some tool parameter inputs sometimes look a little funny...

**"Grid Garage" is a set of script tools that grew over time to manage processing projects within the Knowledge Services Team of the NSW Office of Environment and Heritage. The toolset proves very useful when dealing with large amounts of data, some of which may be suffering from data management issues such as lack of metadata, non-standard spatial references, etc. etc. The tools allow for table-ised reporting of outputs.**

*grid-garage-3 is intended to replace grid-garage-2 as the older back-end just became unfocussed, cluttered and difficult to maintain.* 

In grid-garage-3, tools inherit from a base tool and decorators are available to add attributes to the tool and most importantly to wrap the class method that returns tool parameters. Thus in the grid-garage-3 the user interface is generated simply by applying method decorators with suitable arguments. Tool development is extremely simple - follow a pattern from an existing tool.

TODO: Base code needs to be documented using sphinx or whatever.
