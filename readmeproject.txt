The function 'bmc' does the bounded model checking. Input should be of the form (initial states, transition relation, formula).

When running the code as is, it will ask for these inputs. These should be given using variables of the form x0,x1,x2..., and y0,y1,y2...
etc. But before these, it will ask for the number of labels as well. 

For eg: (x0.y0)                          - Representing the transitions (1)->(1)			-number of labels=1
	(((!x0).(!x1)).((!y0)=(y1)))     - Respresenting the transitions (0,0)->(0,1), (0,0)->(1,0)	-numbr of labels=2



It does BMC and recurrence diameter for the output.



The functions 'callFunction' and 'callFunctionL' is used to do the appropriate action depending on which type of key is seen. For example, if it is X(something),
call function will call the function corresponding to X and do it on (something).

kInduction has been implemented. After the BMC part, it will ask for a saftey property.


For doing bmc on arbitrary ltl formulas, change the value of n to some constant times the value given in the code(line 5).


eg:

Number of labels: 2                                                   
Enter initial states: (x0.(!x1))   #(1,0)
Enter transitions: (((x0.(!x1)).((!y0).y1))+(((!x0).x1).(y0.(!y1))))  #(1,0)->(0,1) and (0,1)->(1,0)
Enter LTL formula: F(Xx0)                         #these three are to be inputted


formula: ('F', ('X', ('PROP', 'x0')))

init: ('AND', ('PROP', 'x0'), ('NOT', ('PROP', 'x1')))

trans: ('OR', ('AND', ('AND', ('PROP', 'x0'), ('NOT', ('PROP', 'x1'))), ('AND', ('NOT', ('PROP', 'y0')), ('PROP', 'y1'))), ('AND', ('AND', ('NOT', ('PROP', 'x0')), ('PROP', 'x1')), ('AND', ('PROP', 'y0'), ('NOT', ('PROP', 'y1')))))

BMC: sat
Recurrence Diameter: 1  #everything from formula to this will be printed
Enter safety condition:x0 #enter saftey condition
k-Induction result: [y_1,0 = False, y_1,1 = True, y_0,1 = False, y_0,0 = True] #(y_0,0, y_0,1)->(y_1,0, y_1,1) is (1,0)->(0,1). x0 =0 in this second state.