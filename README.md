# Project Salamandra

**Salamandra** is an extensible [Pythonic](https://en.wikipedia.org/wiki/Python_(programming_language)) 
infrastructure for loading, analyzing, generating and storing of netlists. 
Salamandra is under development and evolving so documentation of the latest features is missing and expected to be added
soon.

Salamandra is developed by [EnICS labs](https://enicslabs.com/) and is being made available under the permissive 
Apache 2.0 open source license. See [LICENSE](LICENSE).

## Getting Salamandra
Source code is maintained at https://github.com/enics-labs/salamandra

To install Salamandra use `pip install salamandra`

If you want a specific version you can do `pip install salamandra==#version#`

To install a specific version locally (only for user) you can install it inside a `virtualenv`

or `pip install --user salamandra==#version#`
which will Install it to the Python user install directory for your platform. 

Typically `~/.local/` on Linux, or `%APPDATA%Python` on Windows

## Basic Commands

**Note: Only Python3 is supported by Salamandra.**

Salamandra is object-oriented. The four basic classes are `Component`, `Net` , `Param` and `Pin`. The following code creates an NMOS transistor skeleton.

```
import salamandra as slm
nmos = slm.Component('nmos')
nmos.add_pin(slm.Pin('source'))
nmos.add_pin(slm.Pin('drain'))
nmos.add_pin(slm.Pin('gate'))
nmos.add_pin(slm.Pin('body'))
```

The nmos component above has no internal structure, but can be used as a leaf node for higher levels, 
as shown in the example below. Note below the usage of `Input`, `Output` and `Inout`, 
which are of subclass `Pin`, and imply the pin's direction in digital designs.
```
inv = slm.Component('inv')

#pins
inv.add_pin(slm.Input('I'))
inv.add_pin(slm.Output('ZN'))
inv.add_pin(slm.Inout('VDD'))
inv.add_pin(slm.Inout('VSS'))

#subcomponents
inv.add_subcomponent(nmos, 'n1')
inv.add_subcomponent(pmos, 'p1')

#connections
inv.connect('I', 'n1.gate')
inv.connect('I', 'p1.gate')
inv.connect('ZN', 'n1.drain')
inv.connect('ZN', 'p1.drain')
inv.connect('VDD', 'p1.source')
inv.connect('VDD', 'p1.body')
inv.connect('VSS', 'n1.source')
inv.connect('VSS', 'n1.body')
```
Components, such as nmos, resistors, capacitors, etc., 
may have parameters, such as width, length etc.
To be able to make the component compatible to Netlist exporting, those parameters should be added to the component. 
The following code demonstrates how to add parameters to components.
```
# adding new params to inv
nmos.set_spice_param('W', 200E-9)
nmos.set_spice_param('L', 60E-9)
nmos.set_spice_param('mult', 2)
nmos.set_spice_param('nf', 0)

# changing a specific parameter value in the component
nmos.set_spice_param('nf',2)
```

## Other Commands

-   A component can be created from an existing one(clone it):
    ```
    inv = Component('inv')
    inv.add_pin(Input('A'))
    inv.add_pin(Output('Z'))
    
    inv_cloned = Component('inv2', inv)
    ```
-   Salamandra can use busses also:
     ```
    and_ = Component('and')
    and_.add_pinbus(Bus(Input, 'A', 2))  # arguments: type-input, bus_name-A, width-2.
    and_.add_pin(Output('Z'))
    
    nand = Component('nand')
    nand.add_pinbus(Bus(Input, 'A', 2))
    nand.add_pin(Output('Z'))
    nand.add_net(Net('A1A2'))
    
    nand.add_subcomponent(and_, 'i_and')
    nand.add_subcomponent(inv, 'i_inv')
    
    nand.connect_bus('A', 'i_and.A')  # connect_bus for busses
    nand.connect('A1A2', 'i_and.Z')
    nand.connect('A1A2', 'i_inv.A')
    nand.connect('Z', 'i_inv.Z')
    
    # now the connectivity is:
    #    //instances
    #    and i_and(.A({A[1:0]}), .Z(A1A2));
    #    inv i_inv(.A(A1A2), .Z(Z));
    
    # you can disconnect them also
    nand.disconnect('i_inv.Z')
    nand.disconnect_bus('i_and.A')
    
    # and after disconnect the connectivity is:
    #    //instances
    #    and i_and(.A(), .Z(A1A2));
    #    inv i_inv(.A(A1A2), .Z());
    ```
-   Pins can also be connected to constants like 1'bx, 1'b1 or 1'b0
    
-   And if you want to map constants('1', '0') to 'tiehi' and 'tielo' driver cells,
    it can be done with hilomap function:
    ```
    tielo = Component('tielo')
    tielo.add_pin(Output('Y'))
    
    tiehi = Component('tiehi')
    tiehi.add_pin(Output('Y'))
    
    inv.add_pin(Inout('VDD'))
    nand.connect("1'b1", 'i_inv.VDD')
    
    # relevant verilog print:
    # 	//instances
    #	and i_and(.A(), .Z(A1A2));
    #	inv i_inv(.A(A1A2), .VDD(1'b1), .Z());  # 1'b1 connected to VDD
    
    nand.hilomap(tiehi, tielo)
    
    # relevant verilog print:
    #	//instances
    #	and i_and(.A(), .Z(A1A2));
    #	inv i_inv(.A(A1A2), .VDD(HI), .Z());  # connected VDD to tiehi output
    #	tiehi tiehi(.Y(HI));  # added tiehi instance to component
    ```
-   If you want to uniquify the instances in the netlist,
    e.g., every instance of a component will be a new component,
    you can do this using the ```uniq()``` function:
    ```
    nand.add_subcomponent(inv, 'i_inv2')  
    # now there are two instances of inv component: 'i_inv1', 'i_inv2'
    # relevant verilog print:
    #	//instances
    #	inv i_inv(.A(A1A2), .VDD(HI), .Z());
    #	inv i_inv2(.A(), .VDD(), .Z());
    
    nand.uniq()
    
    # now there are two components of inv(inv_0, inv_1), one for each instance
    # relevant verilog print:
    #	//instances
    #	inv_0 i_inv(.A(A1A2), .VDD(HI), .Z());
    #	inv_1 i_inv2(.A(), .VDD(), .Z());
    ```
-   Salamandra also supports assignments using the `connect_nets()` function:
    ```
    inv = Component('inv')
    inv.add_pin(Input('A'))  
    inv.add_pin(Output('Z'))
    # add_pin also add Net with same name attached to this pin
    # you can disable it with add_pin_adds_net in Component
    
    inv.connect_nets('A', 'Z')
    
    # relevant verilog print:
    #	//assignments
    #	assign Z = A;
    ```
-   You can flatten your netlist using `flatten` function, this will flatten your
    netlist until the physical components (checking with __is_physical flag):
    ```
    inv.set_is_physical(True)
    and_.set_is_physical(True)
    
    # we will add another wrapper to nand(that we saw earlier)
    chip = Component('chip')
    chip.add_pinbus(Bus(Input, 'A', 2))
    chip.add_pin(Output('Z'))
    chip.add_subcomponent(nand, 'nand')
    chip.connect_bus('A', 'nand.A')
    chip.connect('Z', 'nand.Z')
    
    chip.print_verilog()
    # relevant verilog print:
    #	//wires
    #	wire [1:0] A;
    #	wire Z;
    #
    #	//instances
    #	nand nand(.A({A[1:0]}), .Z(Z));
    
    chip.flatten()
    chip.print_verilog()
    # relevant verilog print:
    #	//wires
    #	wire [1:0] A;
    #	wire Z;
    #	wire nand__A1A2;
    #
    #	//instances
    #	and nand__i_and(.A({A[1:0]}), .Z(nand__A1A2));
    #	inv nand__i_inv(.A(nand__A1A2), .Z(Z));
    ```
    We can see that it added its inner nets, 
    subcomponents and their connectivity to itself,
    adding the component name as a prefix (e.g., "A1A2" -> "nand__A1A2")
        
-   You can also add properties to objects (pin/net/bus/component) like add tpd value to pin, or 'is_clk' flag
    and after that you can filter pins (or subcomponents/nets...) like this:
    ```
    inv = Component('inv').set_property('is_optimized', True)  # set_property(property, value)
    inv.add_pin(Input('A').set_property('tpd', 0.1))
    inv.add_pin(Inout('VDD').set_property('is_supp', True))
    
    # now we can get filterd pins as we wish
    fast_pins = inv.get_pins(filter=lambda p: p.get_property('tpd') and p.get_property('tpd') < 0.2)
    vdd_pins = inv.get_pins(filter=lambda p: p.get_property('is_supp'))
    ```

- If you want to get component's connectivity paths, you can get this with `connectivity_paths` method
    which will return 3 dictionaries, one dict that has all connectivity, forward and backward of pins&nets.
    second dict that has forward connectivity, and third backward connectivity.
    for example:
    ```     
    all_connectivity_dict:
       (('A',Input): [('A',Net)], ('A',Net): [('A',Input),('X.A',Input),..])
    
    forward connectivity dict:
       (('A',Input): [('A',Net)], ('A',Net): [('X.A',Input)], ('X.A',Input): [('X.O',Output)],..)
    ```

- Before you export your netlist you can add verilog code to your netlist:
    ```
    y = Net('y')
    nand.add_net(y)
    nand.add_verilog_code("\tassign {}=1'b0;".format(y.get_object_name()))
    
    # relevant verilog print:
    #	//verilog code
    #	assign y=1'b0;
    ```

## Export Netlist
-   Salamandra currently supports exporting netlists as verilog netlist or as spectre netlist (Cadence's spice simulator).
    The following code will print the verilog netlist to STDOUT using `print_verilog`.
    ```
    my_design.print_verilog()
    ```
-   If you want it to also print all of its descendants (as modules) you can do that using the flag `include_descendants=True`:
    ```
    my_design.print_verilog(include_descendants=True)
    ```
    You can also write it to a file using `write_verilog_to_file(path)` with `append` flag if you want to append to the file,
    whether it exist or not.

-   Similarly, less recommended method for exporting into a file, you can use `write_verilog`. 
    The function returns a list of lines defining the component as a verilog module:
    ```
    f = open('module.v', 'w')
    for l in sfpga.write_verilog():
       f.write(l+'\n')
    f.close()
    ```

-   In a similar way you can print spectre netlist by using `print_spectre` like this:
    ```
    comp.print_spectre()
    ```
    or any of the verilog functions above, for spectre (`write_spectre_to_file`, etc.)
    
Note: You might want to run `legalize()` on the component before exporting, to check for unexportable structures
such as partially-connected busses. If it finds such problems, `legalize()` will try to fix
what it can. For example, it will connect the undriven bits of a bus to ```{1'bx}``` and connect. 
unloaded outputs/inouts to ```UC_###``` nets.

## Import Netlist
Salamandra currently supports importing netlists from verilog and spectre netlists.
`verilog2slm` is used to import a verilog netlist as components. 
The following code will read the verilog netlist and convert it to components in salamandra:

`components = verilog2slm_file('verilog_file.v')`

it also supports reading an STD cells (takes only I/Os of the modules)

`std_components = verilog2slm_file('std_cells.v',  is_std_cell=True)`
Note: there is a sample std_cells.v file under `verilog_files/more`

and if you want to enable implicit wires you can also
enable it through the flag `implicit_wire=True`

as well you can enable the flag `implicit_instance` to let salamandra guess components
if it isn't shown in the text or not created before. 

The same way you can import spectre netlist using `spectre2slm`:

`comp = spectre2slm_file('spectre_file.scs', top_cell_name='comp')`

## Contributions
Salamandra was first developed by [Tzachi Noy](https://github.com/noytzach) for internal use at EnICS labs.
[Bnayah Levy](https://github.com/SwarleyBL) later joined and helped cleaning, restructuring and adding lots of useful features.

We are open to contributions from the community. We follow the "fork-and-pull" Git workflow.
* Fork the repo on GitHub
* Clone the project to your own machine
* Commit changes to your own branch
* Push your work back up to your fork
* Submit a Pull request so that we can review your changes

**NOTE:** Be sure to merge the latest from "upstream" before making a pull request!

Feel free to [submit](https://github.com/enics-labs/salamandra/issues) issues and enhancement requests.

## Publication
Please acknowledge Salamandra if you use it in a 
published or presented research project.