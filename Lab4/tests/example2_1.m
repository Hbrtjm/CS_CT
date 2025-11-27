# assignment operators
# binary operators
# transposition

A = [[ 1, 2, 3 ] ;
     [ 4, 5, 6 ] ; 
     [ 7, 8, 9 ]];

B = [ [ 1, 2, 3 ] ;  
      [ 4, 5, 6 ] ; 
      [ 7, 8, 9 ]];


C = -A;     # assignemnt with unary expression
C = B' ;    # assignemnt with matrix transpose
C = A+B ;   # assignemnt with binary addition
C = A-B ;   # assignemnt with binary substraction
C = A*B ;   # assignemnt with binary multiplication
C = A/B ;   # assignemnt with binary division
C = A.+B ;  # add element-wise A to B
C = A.-B ;  # substract B from A 
C = A.*B ;  # multiply element-wise A with B
C = A./B ;  # divide element-wise A by B

C += B ;  # add B to C 
C -= B ;  # substract B from C 
C *= A ;  # multiply A with C
C /= A ;  # divide A by C



