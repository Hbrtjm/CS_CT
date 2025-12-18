# Test matrix multiplication

print "=== Test 1: 2x3 * 3x2 matrix multiplication ===";
A = [1, 2, 3 ; 4, 5, 6];
B = [7, 8 ; 9, 10 ; 11, 12];
C = A * B;
print "A =", A;
print "B =", B;
print "A * B =", C;

print "=== Test 2: 2x2 * 2x2 matrix multiplication ===";
D = [1, 2 ; 3, 4];
E = [5, 6 ; 7, 8];
F = D * E;
print "D =", D;
print "E =", E;
print "D * E =", F;

print "=== Test 3: Identity matrix multiplication ===";
I = eye(3);
M = [1, 2, 3 ; 4, 5, 6 ; 7, 8, 9];
R = I * M;
print "I =", I;
print "M =", M;
print "I * M =", R;

print "=== Test 4: Vector (column) multiplication ===";
v1 = [1 ; 2 ; 3];
v2 = [4, 5, 6];
result = v2 * v1;
print "v1 =", v1;
print "v2 =", v2;
print "v2 * v1 =", result;

