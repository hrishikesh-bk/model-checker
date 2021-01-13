# USAGE

```python

from ply_parser import *

tree = parser.parse("G ((a ^ (X (F (X (tru U (G fls)))))) U ((F d) . (b + (! c))))")
print(tree)

# for monadic:

print(tree.child)
print(tree.child.type)

# for dyadic:

print(tree.child.left)
print(tree.child.left.type)
print(tree.child.right.type)
print(tree.child.right.type)

```
