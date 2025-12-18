# Test 1-d vectors and matrix functions

# Explicit dimensions for vectors
a = zeros(5, 1);   # 5x1 column vector
b = ones(3, 1);    # 3x1 column vector
c = eye(4);        # 4x4 identity matrix

# Two arguments - explicit dimensions
d = zeros(5, 1);   # 5x1 column vector
e = ones(1, 5);    # 1x5 row vector
f = eye(3, 3);     # 3x3 identity matrix

# Operations with vectors
g = a + d;         # 5x1 + 5x1 = 5x1 (should work)
print g;
h = b .+ b;        # 3x1 .+ 3x1 = 3x1 (should work)
print h;
n = h .* h;       # 3x1 .* 3x1 = 3x1 (should work)
print n;
n = n ./ h;       # 3x1 ./ 3x1 = 3x1 (should work)
print n;
