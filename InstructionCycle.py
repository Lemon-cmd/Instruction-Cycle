
# coding: utf-8

# In[130]:


import time                     #using time library as clock speed

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
        overflow = "NO OVERFLOW"
        
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
        
        if result.zfill(maxlen)[2] == "1":
            overflow = "OVERFLOW DETECTED"
            
        return result.zfill(maxlen), overflow

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
        overflow = "NO OVERFLOW"
        maxlen = max(len(a), len(b))

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
        
        if result.zfill(maxlen)[2] == "1":     
            overflow = "OVERFLOW DETECTED"
        
        if (int(a,2) < int(b,2)):
            #if a < b, performs two-complement
            opcode, operand = self.oneComplement(result.zfill(maxlen))       #apply one complement to the result
            one = "00001"
            add, ignore = self.add(operand, one)  #ignore is just the overflow str from add method
            return opcode + add, overflow         #perform two complement and return the result
        else:
            return result.zfill(maxlen), overflow 
    
    def operate(self, op, op1 , op2):
        """Operate Method"""
        if op in self.operations:      #no need for loop here; this saves some run time complexity
            if op == "01":
                return "ADDITION", self.operations[op](op1, op2)
            
            else:
                return "SUBTRACTION", self.operations[op](op1, op2)
        else:
            print("ERROR: Operation not found")
            


# In[136]:


class Controller():
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
        
        
        self.DATA = []
        self.lengthR = len(self.RAM)
        self.MDR = None              #Memory Data Register
        self.CIR = None              #Current Instruction Register 
        self.MAR = None              #Memory Address Register  
        self.AC = None               #Accumulator
        self.PC = 0                  #Program Counter  
        self.clock = time.time()     #Clock
        self.ALU = ALU()             #Arithematic Logical Unit
        self.running = True          #a flag indicating if the system is running 
        self.oldPC = 0               #a register that holds the old value of PC
    
    def delay(self):
        """Delay method"""
        time.sleep(1)
        
    def loadPC(self, PC):
        return self.RAM[PC]          #return PC contents
    
    def loadMDR(self, MAR):
        index = int(self.MAR[2:],2)   
        print("Index: ", index)
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
        if self.PC < len(self.RAM):
            self.PC = self.PC + 1                    #increment PC
        self.CIR = self.loadCIR(self.MAR)        #load opcode into CIR 
        
        if (self.CIR != "00"):
            self.MDR = self.loadMDR(self.MAR)        #load content of the address into MDR
                          
        print("MAR: " + self.MAR + " MDR: " + str(self.MDR) + " Instruction: " + self.CIR + " PC: ", self.PC)
        
    def decode(self):
        """Decode Method"""
        if (self.CIR == "00"):            #if code is 00, it indicates that the block contains an operand
            print("Operand: ", self.MAR)
            self.DATA.append(self.MAR)    #appends to the data 
            
        elif (self.CIR == "11"):          #JUMP INSTRUCTION
            
            self.oldPC = self.PC          #save the old content of PC 
            self.PC = self.jump(self.MAR) #jump to the next address
            print("INTERRUPTED")
            self.delay()
            print("JUMPING from " + str(self.oldPC) + " to " + str(self.PC))
            
            #fetch and decode the jump block
            self.fetch()          
            self.decode()
            
            print("RESUMING OPERATION AT LOCATION", self.oldPC)
            print()
            self.PC = self.oldPC         #revert back to the old PC
            
        else:  #if the instruction is ADD 01 or SUBTRACT 10
            print("Instruction: ", self.CIR)
            
            if (self.AC == None):        #Make sure that the Accumulator is empty
                self.AC = self.MDR       #set AC equals to the content of MDR if AC is empty
                
            else:  #If AC is not empty, then there are two operands to perform the arithematic
                print("Performing: ", self.execute(self.CIR, self.AC, self.MDR))
                self.AC = None      #clear AC
              
    def execute(self, CIR, AC, MDR):
        operation, result = self.ALU.operate(CIR, AC, MDR)  #call ALU and perform the arithematic
        self.delay()
        self.store(result)  #store result onto memory
        
        return operation, "Result: " + str(result)
    
    def store(self, result):
        if len(self.RAM) < 64:  #6 bits for address
            self.RAM.append(result)
    
    def run(self):
        while self.PC < self.lengthR and self.running:
            self.fetch()
            self.decode()
            self.delay()
    
        print("\n" + str(round(time.time() - self.clock, 4)) + " s\n")

        


# In[137]:


controller = Controller()
controller.run()

