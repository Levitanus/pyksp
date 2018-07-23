
var1.val = 1
var2.val = 2

# if we have to check type of input
var1.val = var2

# but it could be accendently typed worse,
# skipping the type-check:
var1.val = var2.val

# or much more worse:
somevar = var1 + var2
var1 += var2
# sic!
var1 = var2
