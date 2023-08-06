
A=2.25
C=4
X=1.0
__NAME__=1
B=5+A
Y=X
Z=A+B+C-(Y*X)/2
textfile = open("tmp.txt", "w")
textfile.write("Entered Equations: \n\n")
for i in['z=a+b+c-(y*x)/2', 'a = 2.25', 'b = 5+a', 'c = 4', 'x=1.0', 'y=x', '__name__ =1']: 
    textfile.write(i + "\n")
textfile.write("\nResults: \n\n")
print("A = " + str(float(A)), file=textfile)
print("B = " + str(float(B)), file=textfile)
print("C = " + str(float(C)), file=textfile)
print("X = " + str(float(X)), file=textfile)
print("Y = " + str(float(Y)), file=textfile)
print("Z = " + str(float(Z)), file=textfile)
print("__NAME__ = " + str(float(__NAME__)), file=textfile)
textfile.close()
