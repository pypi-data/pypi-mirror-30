## Loaderr
Ever wonder why the solutions you think of in your head never work? Why your ability to write awesome code is limited? Well here it is – you're not using `Loaderr`.

With `Loaderr`, you can create simple loading icons to use in your projects. Say you want your program to seem like it's processing something?

```
from loaderr import *
loading("Processing$.$", dots, medium, 5)
```

It's that simple! With this code, your program will literally halt its progress just to print:

```
Processing.
Processing..
Processing...
```

## Tutorial
There are two functions in `Loaderr`.

+ `clear_line()`
Sets the cursor back so text can be printed over it.

+ `loading(string, logo, timing, repeat)`
Creates a "loading" thing.

    + The `string` is determines what surrounds the loading animation. For example `Loading$$` will create `Loading.` -> `Loading..` -> `Loading...`. The two `$` indicate where the animation is placed. If the string is empty, it replaces the entire string.

    + The `logo` is an array that stores the animation. To get the dots, you could do `[".", "..", "..."]`.

    + The `timing` is an array the stores the wait times within each animation. For example, `[0.5]` will display the animation every half a second. `[0.1, 0.2]` will display the first frame after `0.1` seconds and the next after `0.2` seconds.

    + The `repeat` is the amount of times to loop the animation.


## Pre-Sets
There are several pre-defined animations and wait times. These are inside the `loaderr.py` file. For example, `loaderr.table_flip` is `(╯°□°）╯┳━┳` -> `(╯°□°）╯┳━┳` -> `(╯°□°）╯︵┻━┻` -> `(╯°□°）╯︵  ┳━┳`
