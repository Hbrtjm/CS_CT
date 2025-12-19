
a = zeros(5, 1);   # 5x1 column vector
b = ones(3, 1);    # 3x1 column vector
c = eye(4);        # 4x4 identity matrix

d = zeros(5, 1);   # 5x1 column vector
e = ones(1, 5);    # 1x5 row vector
f = eye(3, 3);     # 3x3 identity matrix

g = a + d;         # 5x1 + 5x1 = 5x1
print g;
h = b .+ b;        # 3x1 .+ 3x1 = 3x1
print h;
n = h .* h;       # 3x1 .* 3x1 = 3x1
print n;
n = n ./ h;       # 3x1 ./ 3x1 = 3x1
print n;
