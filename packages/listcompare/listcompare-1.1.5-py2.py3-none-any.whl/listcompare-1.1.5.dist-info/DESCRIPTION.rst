This module provides support to compare two lists that have same or different types of data in it.
 Examples lis1 = [1,2,3] 
lis2 = [2,1] 
plc.compare_list(lis1, dlis2) # True 
lis1 = [1,2,3] 
lis2 = [2,1,'3'] 
plc.compare_list(lis1, lis2) # False 
lis1 = ['1','2','3'] 
lis2 = ['2','1'] 
plc.compare_list(lis1, lis2) # False 
lis1 = [1,2,3] 
lis2 = [2,1,3] 
plc.compare_list(lis1, lis2) # True 
lis1 = [{1:1,2:2}] 
lis2 = [{1:1,2:2}] 
plc.compare_list(lis1, lis2) # True  


