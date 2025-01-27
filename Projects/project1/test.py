def my_function (a:int, b:int)-> int:
    """my_Function Provides addition given two integers given by user
    intput arg:
     a:int
     b:int
     Return 
     c: int
    """

    c=a+b
    return c
var1 =int(input("Enter the First Integer:") )
var2= int(input("Enter the Second Integer:") )
var3= my_function(var1, var2)
print ("Answer is", var3)

