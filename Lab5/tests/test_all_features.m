# Comprehensive test suite for the matrix language interpreter

print "=== Test 1: Variable assignments ===";
x = 5;
y = 10;
z = x + y;
print "x =", x;
print "y =", y;
print "z = x + y =", z;

print "=== Test 2: String operations ===";
s1 = "Hello";
s2 = "World";
s3 = s1 + " " + s2;
print s3;

print "=== Test 3: If-else statements ===";
a = 10;
if (a > 5)
    print "a is greater than 5";
else
    print "a is not greater than 5";

b = 3;
if (b > 5)
    print "b is greater than 5";
else
    print "b is not greater than 5";

print "=== Test 4: Nested if-else ===";
c = 15;
if (c > 20)
    print "c > 20";
else if (c > 10)
    print "10 < c <= 20";
else
    print "c <= 10";

print "=== Test 5: While loops ===";
i = 1;
while (i <= 5) {
    print i;
    i = i + 1;
}

print "=== Test 6: For loops ===";
for j = 1:5
    print j;

print "=== Test 7: Break and continue ===";
for k = 1:10 {
    if (k == 3)
        continue;
    if (k == 7)
        break;
    print k;
}

print "=== Test 8: Matrix creation (square) ===";
v1 = zeros(3);
print "zeros(3) =", v1;
v2 = ones(3);
print "ones(3) =", v2;

print "=== Test 9: Vector creation (explicit dims) ===";
v3 = zeros(3, 1);
print "zeros(3, 1) =", v3;
v4 = ones(1, 3);
print "ones(1, 3) =", v4;

print "=== Test 10: Matrix creation ===";
m1 = zeros(2, 3);
print "zeros(2, 3) =", m1;
m2 = ones(2, 3);
print "ones(2, 3) =", m2;
m3 = eye(3);
print "eye(3) =", m3;

print "=== Test 11: Vector addition ===";
va = zeros(3, 1);
vb = ones(3, 1);
vc = va + vb;
print "zeros(3,1) + ones(3,1) =", vc;

print "=== Test 12: Vector element-wise operations ===";
vd = ones(3, 1);
ve = ones(3, 1);
vf = vd .+ ve;
print "ones(3,1) .+ ones(3,1) =", vf;
vg = vd .- ve;
print "ones(3,1) .- ones(3,1) =", vg;
vh = vd .* ve;
print "ones(3,1) .* ones(3,1) =", vh;

print "=== Test 13: Matrix literal ===";
mat = [1, 2, 3 ; 4, 5, 6];
print "mat =", mat;

print "=== Test 14: Matrix transpose ===";
matt = mat';
print "mat' =", matt;

print "=== Test 15: Matrix indexing ===";
print "mat[0, 0] =", mat[0, 0];
print "mat[1, 2] =", mat[1, 2];

print "=== Test 16: Matrix assignment ===";
mat[0, 1] = 99;
print "After mat[0, 1] = 99:", mat;

print "=== Test 17: Scalar operations ===";
n1 = 10;
n2 = 3;
print "10 + 3 =", n1 + n2;
print "10 - 3 =", n1 - n2;
print "10 * 3 =", n1 * n2;
print "10 / 3 =", n1 / n2;

print "=== Test 18: Unary negation ===";
p = 5;
q = -p;
print "-5 =", q;

print "=== Test 19: Compound assignments ===";
r = 10;
r += 5;
print "r after += 5:", r;
r -= 3;
print "r after -= 3:", r;
r *= 2;
print "r after *= 2:", r;
r /= 4;
print "r after /= 4:", r;

print "=== Test 20: Scalar multiplication with matrix ===";
sm = ones(2, 2);
sm2 = sm * 5;
print "ones(2,2) * 5 =", sm2;

print "=== Test 21: Matrix element-wise operations ===";
ma = [1, 2 ; 3, 4];
mb = [5, 6 ; 7, 8];
mc = ma .+ mb;
print "[1,2;3,4] .+ [5,6;7,8] =", mc;
md = ma .- mb;
print "[1,2;3,4] .- [5,6;7,8] =", md;
me = ma .* mb;
print "[1,2;3,4] .* [5,6;7,8] =", me;

print "=== All tests completed ===";

