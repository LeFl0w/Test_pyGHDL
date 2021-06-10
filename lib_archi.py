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

def getNodeLineInFile (node):
    """ Return the line in original file of the node :obj:`node` """
    loc = nodes.Get_Location(node)
    fil = files_map.Location_To_File(loc)
    pos = files_map.Location_File_To_Pos(loc, fil)
    line = files_map.Location_File_To_Line(loc, fil)
    return line

def getNodeColumInFile (node):
    """ Return the column in original file of the node :obj:`node` """
    loc = nodes.Get_Location(node)
    fil = files_map.Location_To_File(loc)
    pos = files_map.Location_File_To_Pos(loc, fil)
    line = files_map.Location_File_To_Line(loc, fil)
    col = files_map.Location_File_Line_To_Offset(loc, fil, line)
    return col

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
    print("name:"+ str(getIdentifier(designUnit)) + " line "+ str(getNodeLineInFile(designUnit)) + " column "+ str(getNodeColumInFile(designUnit)))
    
    while designUnit != nodes.Null_Iir:
        libraryUnit = nodes.Get_Library_Unit(designUnit)

        if nodes.Get_Kind(libraryUnit) == nodes.Iir_Kind.Entity_Declaration:
            name=getIdentifier(libraryUnit)
            #internal AST conversion tables up to line
            loc = nodes.Get_Location(libraryUnit)
            fil = files_map.Location_To_File(loc)
            pos = files_map.Location_File_To_Pos(loc, fil)
            line = files_map.Location_File_To_Line(loc, fil)
            col = files_map.Location_File_Line_To_Offset(loc, fil, line)
            print("name:"+ str(getIdentifier(libraryUnit)) + " line "+ str(getNodeLineInFile(libraryUnit)) + " column "+str(getNodeColumInFile(libraryUnit)))

        elif nodes.Get_Kind(libraryUnit) == nodes.Iir_Kind.Architecture_Body:
            print("architecture %s" % getIdentifier(libraryUnit))
            
        else:
            print("unknown designUnit!")
        designUnit = nodes.Get_Chain(designUnit)


def main(self):
    init()
    list_units(self)


if __name__ == "__main__":
    main("adder_file.vhd")