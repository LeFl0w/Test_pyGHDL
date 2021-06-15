library IEEE;
use ieee.std_logic_1164.all;
entity adder is
  -- `i0`, `i1` and the carry-in `ci` are inputs of the adder.
  -- `s` is the sum output, `co` is the carry-out.
  port (
    i0, i1 : in bit; 
    ci : in bit; 
    s : out bit; 
    co : out bit;
    test: inout bit;


    --type std_logic
    t1: in std_logic;
    t2: out std_logic_vector(5 downto 0);
    
    --type integer
    t3 : in integer range 0 to 4;
    t4: out integer
    
    );
end adder;

architecture rtl of adder is
  constant C_LEFTBOUND :integer:= 10;

  signal sig1_int : integer;
  signal sig2_int : integer range 4 to 5;

  signal sig3_std_logic : std_logic;
  signal sig4_std_logic_vector: std_logic_vector(4 downto 0);
  signal sig5 : std_logic_vector(C_LEFTBOUND downto 0);
  signal sig6: std_logic_vector(30 downto sig5'right);
begin
   --  This full-adder architecture contains two concurrent assignment.
   --  Compute the sum.
   s <= i0 xor i1 xor ci;
   --  Compute the carry.
   co <= (i0 and i1) or (i0 and ci) or (i1 and ci);
end rtl;

