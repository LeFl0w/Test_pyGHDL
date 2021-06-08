import pyGHDL.libghdl     as libghdl
from pyGHDL.libghdl       import name_table, files_map, errorout_console
from pyGHDL.libghdl.vhdl  import nodes, sem_lib


def init():
    """Initialization: set options and then load libaries"""
    libghdl.initialize()

    # Print error messages on the console.
    errorout_console.Install_Handler()

    # Set options. This must be done before analyze_init()
    libghdl.set_option("--std=08")

    # Finish initialization. This will load the standard package.
    if libghdl.analyze_init_status() != 0:
        self.fail("libghdl initialization error")

def getIdentifier(node):
    """Return the Python string from node :obj:`node` identifier"""
    return name_table.Get_Name_Ptr(nodes.Get_Identifier(node))

def list_units(filename):
    # Load the file
    file_id = name_table.Get_Identifier(str(filename))
    sfe = files_map.Read_Source_File(name_table.Null_Identifier, file_id)
    if sfe == files_map.No_Source_File_Entry:
        print("cannot open file '%s'" % filename)
        return

    # Parse
    file = sem_lib.Load_File(sfe)

    # Display all design units
    designUnit = nodes.Get_First_Design_Unit(file)
    while designUnit != nodes.Null_Iir:
        libraryUnit = nodes.Get_Library_Unit(designUnit)

        if nodes.Get_Kind(libraryUnit) == nodes.Iir_Kind.Entity_Declaration:
            print("entity %s" % getIdentifier(libraryUnit))

        elif nodes.Get_Kind(libraryUnit) == nodes.Iir_Kind.Architecture_Body:
            print("architecture %s" % getIdentifier(libraryUnit))
            
        else:
            print("unknown designUnit!")
        designUnit = nodes.Get_Chain(designUnit)


def main():
    init()
    list_units("adder.vhd")


if __name__ == "__main__":
    main()