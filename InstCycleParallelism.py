
# coding: utf-8

# In[4]:


import time 

class ALU():
    """Arithmetic Logic Unit Class"""
    def __init__(self):
        #a dictionary that holds operations keys and the corresponding operation in accordance to the key
        #Lambda is used to created an empty function in which I assigned it to the corresponding operation
        self.operations = {
            "01" : lambda a, b: self.add(a,b),          #opcode is 01 then it is addition
            "10" : lambda a, b: self.subtract(a,b)      #opcode is 10 then it is subtraction
        }
        
    def add(self, a, b):
        """Add operation"""
        #I got the code from stackoverflow and made some small changes to it
        maxlen = max(len(a), len(b))
        
        overflow = False  #a variable to check for overflow
        #Normalize lengths
        a = a.zfill(maxlen)
        b = b.zfill(maxlen)
        result = ''
        carry = 0
        for i in range(maxlen-1, -1, -1):
            r = carry
            r += 1 if a[i] == '1' else 0
            r += 1 if b[i] == '1' else 0

            result = ('1' if r % 2 == 1 else '0') + result
            carry = 0 if r < 2 else 1       

        if carry !=0 : 
            result = '1' + result
        if result.zfill(maxlen)[2] == "1":       #simply check if the overflow bit is 1
            overflow = True
            
        return result.zfill(maxlen), str(overflow), a, b

    def oneComplement(self, difference):
        """One Complement Method"""
        opcode = difference[:2]
        operand = difference[2:]
        result = ''
        
        for i in range(len(operand)):               #flip the bits to their opposite
            if (operand[i] == '0'):
                result += '1'
            else:
                result += '0'
         
        final = opcode + result
        
        return final[:2], final[2:]         #return opcode, operand

    
    def subtract(self, a, b):
        """Subtraction Method"""
        #Used the add method and changes the rule in the for loop 
        maxlen = max(len(a), len(b))
        overflow = False                #variable for checking overflow
        
        #Normalize lengths
        a = a.zfill(maxlen)
        b = b.zfill(maxlen)
        result = ''
        carry = 0

        for i in range(maxlen-1, -1, -1):
            r = carry
            r += 1 if a[i] == '1' and b[i] == '0' else 0
            r += 1 if a[i] == '0' and b[i] == '1' else 0
    
            result = ('1' if r % 2 == 1 else '0') + result
            carry = 1 if a[i] == '0' and b[i] == '1' else 0
       
        if carry !=0 : 
            result = '1' + result
            
        if result.zfill(maxlen)[2] == "1":      #simply check if the overflow bit is 1
            overflow = True
        
        if (int(a,2) < int(b,2)):
            #if a < b, performs two-complement
            opcode, operand = self.oneComplement(result.zfill(maxlen))       #apply one complement to the result
            one = "00001"
            add, ignore = self.add(operand, one)  #ignore is just the overflow str from add method
            return opcode + add, overflow, a, b         #perform two complement and return the result
        else:
            return result.zfill(maxlen), str(overflow), a, b 
    
    def operate(self, op, op1 , op2):
        """Operate Method"""
        if op in self.operations:      #no need for loop here; this saves some run time complexity
            result, overflow, a, b = self.operations[op](op1, op2)
            if op == "01":
                return "ADDITION", result, overflow, a, b
            
            else:
                return "SUBTRACTION", result, overflow, a, b
        else:
            print("ERROR: Operation not found")
            


# In[5]:


class PU():
    def __init__(self, PC, AC, RAM, size, n):
        """Processing Unit; takes parameter PC, AC, RAM, size of the RAM;"""
        self.n = n
        self.PC = PC             #PC 
        self.RAM = RAM           #RAM 
        self.length = size       #size of RAM  
        self.MDR = None          #Memory Data Register
        self.CIR = None          #Current Instruction Register
        self.MAR = None          #Memory Address Register
        self.AC = AC             #Accumulator
        self.ALU = ALU()         #ALU
        self.oldPC = 0           #A register that temporarily store the current PC 
        self.calCheck = 0        #A register that indicates if the instruction is to calculate
        self.jumpCheck = 0       #A register that indicates if the instruction is to jump
        
    def loadPC(self, PC):
        return self.RAM[PC]          #return PC contents
    
    def loadMDR(self, MAR):
        index = int(self.MAR[2:],2)   #grab the proper index; convert the address from binary to integer 
        print()
        return self.RAM[index]       #return the data at the specified address
    
    def loadCIR(self, MAR):
        return MAR[:2]          #return opcode
    
    def jump(self, MAR):
        jumpIndex = int(MAR[2:],2)
        return jumpIndex              #return the new content of PC
        
    def fetch(self):
        """Fetching Method"""
        self.MAR = self.loadPC(self.PC)          #load PC contents to MAR
        self.CIR = self.loadCIR(self.MAR)        #load opcode into CIR 
        if self.PC < self.length:
            print("MAR: " + self.MAR + " Instruction: " + self.CIR + " PC: ", self.PC)
            self.PC = self.PC + self.n                    #increment PC
        
    def decode(self):
        if (self.CIR != "00"):
            self.MDR = self.loadMDR(self.MAR)        #load content of the address into MDR
            print(self.MDR)
            
        if self.CIR == "10" or self.CIR == "01":
            self.calCheck = 1            #if instruction is add or subtract, calCheck is True
            
        elif self.CIR == "11":
            self.jumpCheck = 1           #if instruction is jump, then jumpCheck is true
    
    def execute(self):
        if (self.calCheck == 1):         #if the instruction is to calculate
            print("Instruction: ", self.CIR + " MDR:", self.MDR)
            if self.AC == None:        #check if AC is full/empty
                self.AC = self.MDR
                self.calCheck = 0
            elif self.AC != None:                        #if AC is full, perform calculation on AC and MDR
                operation, result, overflow, a, b = self.ALU.operate(self.CIR, self.AC, self.MDR)
                time.sleep(1)  #delay output
                print("Performed:", operation, a, b + " Result:", result + " Overflow:", overflow)
                self.store(result)  #store the result
                self.AC = None      #clear AC and calCheck
                self.calCheck = 0
        
        elif (self.jumpCheck == 1):       #if the instruction is to jump,
            print("Instruction: ", self.CIR)
            self.oldPC = self.PC          #save the old content of PC 
            self.PC = self.jump(self.MAR) #jump to the next address
            print("\nINTERRUPTED")
            time.sleep(1)       #pause for 1 second
            print("JUMPING from " + str(self.oldPC) + " to " + str(self.PC))
            
            #fetch and decode and execute
            self.fetch()          
            self.decode()
            self.execute()
            
            print("RESUMING OPERATION AT LOCATION", str(self.oldPC) + "\n")
            self.PC = self.oldPC         #revert back to the old PC
            self.jumpCheck = 0           #set jumpCheck back to 0 and continue where it left off
       
    def store(self, result):
        if len(self.RAM) < 32:  #5 bits for address
            self.RAM.append(result)
            


# In[6]:


class System():
    def __init__(self):
        #2 bits for opcode and 6 bits for address so the RAM will have the size of 64 based on the 6 bits
        #1 bit for the overflow and 5 bits for the actual operand
        #overflow bit is always left empty
        #00 indicates that it is an operand
        #01 indicates ADDITION
        #10 indicates SUBTRACTION
        #11 indicates JUMP
        
        self.RAM = ["00000101", #0
                    "00000110",  
                    "00000100",
                    "00000001",
                    "01000000",
                    "01000001", 
                    "10000010",
                    "10000000",  #7
                    "01001101",
                    "11001100",
                    "00000111",
                    "00000010",
                    "01001010",  #12
                    "00011111",
                    "01001101",
                    "01000011",
                    "01000000",
                    "01000001",
                    "00001001",
                    "01000000",
                    "01000001"
                   ]
        
        self.size = len(self.RAM)
        self.clock = time.time()     #start clock of the system
        self.AC = None   #Accumulator 
        self.N = 2
        self.firstUnit = PU(0, self.AC, self.RAM, self.size, self.N)  #give each unit a different PC
        self.secondUnit = PU(1, self.AC, self.RAM, self.size, self.N) #both share the AC, RAM
        self.counter = 0  #a counter for the loop
        #the PC of each Unit will increment by 2 because there are only two units
        #if the system was to have n units running at a time, then the PC of each will increment by n
        
    def delay(self):
        #delay method; delay by .25 sec
        time.sleep(.25)
    
    def run(self):
        """Run Method"""
        """ F D E
              F D E
            for N number of Units running, size is divided by n
            
        """
        while self.counter < (self.size // self.N):     
            self.firstUnit.fetch()
            self.delay()
            self.firstUnit.decode()
            self.secondUnit.fetch()
            self.delay()
            self.firstUnit.execute()
            self.delay()
            self.secondUnit.decode()
            self.secondUnit.execute()
            self.delay()
            self.counter += 1
        #subtract current time with the time when the system starts
        print("\n" + str(round(time.time() - self.clock, 8)) + " s\n")    
    


# In[7]:


sys = System()
sys.run()

