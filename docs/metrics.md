# Metrics and units

---

Although metrics and units are not hard-coded in any way and can be interpreted
by target code generator in arbitrary ways, we should defined some common ground
to be able to port experiments between platforms.

pyFlies assumes the following metrics and units:

- for coordinate system we assume that center of the screen is (0, 0) and the
  screen extends 100 units in each direction where going up and right is
  a positive direction.

- colors are in standard CSS format - `#<red two hex digits><green two hex
  digits><blue two hex digits>`. E.g. `#a489f3`.
  
- for time unit we assume miliseconds.


!!! tip

    In the VS Code editor you can use various extensions to make your editing experience
    more pleasant. For example, for working with colors you can use 
    [Color Manager](https://marketplace.visualstudio.com/items?itemName=RoyAction.color-manager)
