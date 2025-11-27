# assignment operators
# binary operators
# transposition

A = [[ 1, 2, 3 ] ;
     [ 4, 5, 6 ] ; 
     [ 7, 8, 9 ]];

B = [ [ 1, 2, 3 ] ;  
      [ 4, 5, 6 ] ; 
      [ 7, 8, 9 ]];

D1 = A.+B' ; # add element-wise A with transpose of B
D2 -= A.-B' ; # substract element-wise A with transpose of B
D3 *= A.*B' ; # multiply element-wise A with transpose of B
D4 /= A./B' ; # divide element-wise A with transpose of B




