import pyGHDL.libghdl     as libghdl
from pyGHDL.libghdl       import name_table, files_map, errorout_console
from pyGHDL.libghdl.vhdl  import nodes, sem_lib
import pyGHDL.libghdl.utils as pyutils
import pyGHDL.libghdl.vhdl.nodes_meta as nodes_meta
from typing import List, Any, Generator

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

#################################################
############ Global node functions 
#################################################
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

def GetNodeType (node) -> str:
    """Return the name of the node type"""
    if nodes.Get_Kind(node) == nodes.Iir_Kind.Design_Unit:
        return "Design name: "
    elif nodes.Get_Kind(node) == nodes.Iir_Kind.Entity_Declaration:
        return "Entity name: "
    elif  nodes.Get_Kind(node) == nodes.Iir_Kind.Interface_Signal_Declaration:
        return "Entity Interface port name: "
    elif nodes.Get_Kind(node) == nodes.Iir_Kind.Architecture_Body:
         return "Architecture name: "
    elif nodes.Get_Kind(node) == nodes.Iir_Kind.Constant_Declaration:
        return "Constant declaration name: "
    elif nodes.Get_Kind(node) == nodes.Iir_Kind.Signal_Declaration:
        return "Signal declaration name: "    
    else :
        return "Unknown type: "


def DisplayNodeInfo(node) -> str:
    """Return General information regarding the node"""
    return GetNodeType(node)+ str(getIdentifier(node)) + " |l-"+ str(getNodeLineInFile(node)) + " c-:"+ str(getNodeColumInFile(node))
#################################################
############End Global node functions 
#################################################


def list_units(filename):
    """ 
        Display informations about the VHDL file.
        At the end this function could be simlar has vhdl-disp_tree but for human eyes
     """
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
    #print(DisplayNodeInfo(designUnit))

    #iterate over every VHDL constructs below designUnit
    #for libraryUnit in pyutils.constructs_iter(designUnit):
    for libraryUnit in libghdl.utils.constructs_iter(designUnit):
        print(DisplayNodeInfo(libraryUnit))


def main(self):
    init()
    list_units(self)


if __name__ == "__main__":
    main("adder_file.vhd")