![oeh logo](https://github.com/NSW-OEH-EMS-KST/grid-garage/blob/master/img/oehlogo.png)

ArcGIS python toolbox supporting table-based processing.

The toolbox is being developed under ArcGIS 10.4.

**"Grid Garage" is a set of script tools that grew over time to manage processing projects within the Knowledge Services Team of the NSW Office of Environment and Heritage. The toolset proves very useful when dealing with large amounts of heterogenous data, some of which may be suffering from data management issues such as lack of metadata, non-standard spatial references, etc. etc. The tools allow for table-based reporting of outputs and easy chaining of results into inputs.**

In *grid-garage*, tools inherit from a base tool and decorators are used to implement tool parameters i.e. in *grid-garage* the user interface is generated simply by applying method decorators with suitable arguments. Tool development is simple - follow a pattern from existing tools.

