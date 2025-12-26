# basic calculator

# get user input
a = input("enter the first number: ")
b = input("enter the second number: ")
c = input("enter the operatiop (=,-,*,/) : ") 
d = 0
#perform the operation
if c == "+":
    d = int(a) + int(b)
elif c == "-":
    d = int(a) - int(b)
elif c == "*" or c == "x":
    d = int(a) * int(b)
elif c == "/" or c == "//":
    d = int(a) / int(b) 
#handle invalid operation
else:
    print("invalid operation")
#print the result
print(d)
