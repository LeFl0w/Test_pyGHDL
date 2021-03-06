import pyGHDL.libghdl     as libghdl
from pyGHDL.libghdl       import name_table, files_map, errorout_console
from pyGHDL.libghdl.vhdl  import nodes, sem_lib
import pyGHDL.libghdl.utils as pyutils
import pyGHDL.libghdl.vhdl.nodes_meta as nodes_meta

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

def EvaluateRightBoundary(node) -> str:
    """ Get string value for Iir_Kind.Range_Expression :right boundary"""
    return EvaluateBoundary(node,"Right")

def EvaluateLeftBoundary(node) -> str:
    """ Get string value for Iir_Kind.Range_Expression :Left boundary"""
    return EvaluateBoundary(node,"Left")

def EvaluateBoundary(node,dir) -> str:
    """ Get string value for Iir_Kind.Range_Expression :right or left boundary"""
    if dir=="Right":
        Get_Bound=nodes.Get_Right_Limit_Expr
    elif dir =="Left":
        Get_Bound=nodes.Get_Left_Limit_Expr
    else :
        return "Invalid Bonndary request"

    #get name if it is driven by a constant
    if nodes.Get_Kind(Get_Bound(node))==nodes.Iir_Kind.Simple_Name: 
        Bound= getIdentifier(Get_Bound(node))
    #integer return the value
    if nodes.Get_Kind(Get_Bound(node))==nodes.Iir_Kind.Integer_Literal:
        Bound=nodes.Get_Value(Get_Bound(node))
    #attribute case
    if nodes.Get_Kind(Get_Bound(node))==nodes.Iir_Kind.Attribute_Name:
        Bound=getIdentifier(nodes.Get_Prefix(Get_Bound(node)))+"'"+getIdentifier(Get_Bound(node))
    return Bound

def EvaluateaAgregDirection(node) -> str:
    """ Get string value for Iir_Kind.Range_Expression :direction"""     
    #FIXME how to get to Direction_Type  value which is defined in types.ads?
    # value 1 is "downto" 0 is "to"
    if nodes.Get_Direction(node): 
        Direction=s "downto" 
    else:
        Direction="to"
    return Direction



def DisplayNodeInfo(node) -> str:
    """Return General information regarding the node"""
    return GetNodeType(node)+ str(getIdentifier(node)) + " |l-"+ str(getNodeLineInFile(node)) + " c-:"+ str(getNodeColumInFile(node))
#################################################
############End Global node functions 
#################################################



#################################################
###  port specific function
#################################################
def get_port_mode(port) -> str:
    """Return the Mode of a port, as a string"""
    mode = nodes.Get_Mode(port)
    return (
        "in"
        if mode == nodes.Iir_Mode.In_Mode
        else "out"

        if mode == nodes.Iir_Mode.Out_Mode
        else "inout"

        if mode == nodes.Iir_Mode.Inout_Mode
        else "buffer"

        if mode == nodes.Iir_Mode.Buffer_Mode
        else "linkage"

        if mode == nodes.Iir_Mode.Linkage_Mode
        else "unknown"
    )
    

def get_port_type(port) -> str:
    "Return the Type and range of a port, as a string"
    subtype = nodes.Get_Subtype_Indication(port)
    if subtype == nodes.Null_Iir:
        #we are dealing with ownership problem. 
        #This port should have the same type as the previous type definition
        #see /doc/internals/AST.rst
        if nodes.Get_Is_Ref(port):
            #FIXME : How to get back to previous subtype definition?
            return "same definition as previous one"
        else:
            return "Unknown empty Type."

    else:
        skind = nodes.Get_Kind(subtype)

        #type simple name (node is subtype_indication)
        if skind == nodes.Iir_Kind.Simple_Name:
            return getIdentifier(subtype)
        
        #type array subtype (node is subtype_indication)
        if skind == nodes.Iir_Kind.Array_Subtype_Definition  :
            MarkType = getIdentifier(nodes.Get_Subtype_Type_Mark(subtype))
        
            for rng in pyutils.flist_iter(nodes.Get_Index_Constraint_List(subtype)):
                if nodes.Get_Kind(rng) == nodes.Iir_Kind.Range_Expression:
                    LeftBound=EvaluateLeftBoundary(rng)
                    Direction=EvaluateaAgregDirection(rng)
                    RightBound=EvaluateRightBoundary(rng)
                    return MarkType+" " + str(LeftBound) +" " +str(Direction)+" "+str(RightBound)

                return "UNSUPPORTED array_subtype_definition"

        #this type includes integer with range definition (node is subtype_indication)
        #the structure is sligtly different from the previous one as there is no list for constraints
        if skind == nodes.Iir_Kind.Subtype_Definition :
            #get type
            MarkType = getIdentifier(nodes.Get_Subtype_Type_Mark(subtype))
            #get informations from subnode range_expression
            NodeRangeExpression=nodes.Get_Range_Constraint(subtype)
            #get ranges 
            LeftBound=EvaluateLeftBoundary(NodeRangeExpression)
            Direction=EvaluateaAgregDirection(NodeRangeExpression)
            RightBound=EvaluateRightBoundary(NodeRangeExpression)

            return MarkType+" " + str(LeftBound) +" " +str(Direction)+" "+str(RightBound)

    return "UNSUPPORTED"

def DisplayPortInfo(node) -> str:
    """Return General information regarding the the port"""
    return  DisplayNodeInfo(node) + " |Dir :"+ get_port_mode(node) + " |Type: " +get_port_type(node)
################################################
##end port specific functions
#################################################


#################################################
###  declaration specific function
#################################################
def DisplayDeclInfo(node) -> str:
    """Return General information regarding architecture declaration"""
    return  DisplayNodeInfo(node) +" |Type: " +get_port_type(node)
#################################################
### End  declaration specific function
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
    print(DisplayNodeInfo(designUnit))

    while designUnit != nodes.Null_Iir:
        #analysing nodes of type library Unit
        libraryUnit = nodes.Get_Library_Unit(designUnit)

        #VHDL entity
        if nodes.Get_Kind(libraryUnit) == nodes.Iir_Kind.Entity_Declaration:
            name=getIdentifier(libraryUnit)
            print(DisplayNodeInfo(libraryUnit))
            if nodes_meta.Has_Port_Chain(nodes.Get_Kind(libraryUnit)):
                print("Info: Entity has got ports")
                for port in pyutils.chain_iter(nodes.Get_Port_Chain(libraryUnit)):
                    print(DisplayPortInfo(port))
            else :
                print("Info: Entity hasn't got any port")

        #VHDL Architecture    
        elif nodes.Get_Kind(libraryUnit) == nodes.Iir_Kind.Architecture_Body:
            name=getIdentifier(libraryUnit)
            print(GetNodeType(libraryUnit) + str(name))

            if nodes_meta.Has_Declaration_Chain(nodes.Get_Kind(libraryUnit)):
                print("Info: Architecture  has got declarations")
                #get every architecture declarations
                for Declarations in pyutils.declarations_iter(libraryUnit):
                # for Definitions in pyutils.chain_iter(nodes.Get_Declaration_Chain(libraryUnit)):
                    print(DisplayDeclInfo(Declarations))

        else:
            print("unknown designUnit!")
        designUnit = nodes.Get_Chain(designUnit)


def main(self):
    init()
    list_units(self)


if __name__ == "__main__":
    main("adder_file.vhd")