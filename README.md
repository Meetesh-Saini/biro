# biro 
biro (pronounced as _B-row_ and mispelling of _bro_) is an esoteric programming language.

Principle of biro: Don't complicate things

## Rules 
- Typed language
- Initialization of variables is mandatory
- All global variable declaration or function declaration starts with `biro`
    ```cpp
    biro a : num = 0 // global variable

    biro myfunc(a,b) : (num,num,str)
    ```
- Local variables are prefixed with `smallbiro`
    ```cpp 
    smallbiro i : num = 0 // local variable
    ```

## Features
- Every loop is infinite loop. Break it using condition.
- No `else`, only `if`. Why do we need `else` when we have `if`?
- Arithmetic operators
- Logical operators
- No bitwise operators (why do we need them, we can implement them using arithmetic operators)
- Built-in Data types and structures
    - number (always a float)
    - string 
    - boolean
    - array
    - stack 
    - queue
- Biro have three comparison operator `equals` or `==`, `more` or `>` and `less` or `<`. Why do we need `>=`, `<=` when they can be written as `a == b or a > b` and `a == b or a < b` respectively.


## Equivalent of Biro in other languages
| Biro | Python | C++ |
|---|---|---|
|loop | while True| while(true)|
|is `condition` ? | if `condition` : | if (`condition`)|
|donate| return| return|
|proceed|continue|continue|
|leave|break|break|
|attempt|try|try|
|arrest|except|catch|
|equals|==|==|
|more|>|>|
|less|<|<|
|and|and|&&|
|or|or|\|\||
|true|True|true|
|false|False|false|
|num|float|float|
|str|str|std::string|
|bool|bool|bool|

## How your biro works?
```
+-------------+                  +------------+
|             |   preprocessor   |            |
|    biro     +----------------->|  pirocode  |
|             |                  |            |
+-------------+                  +-----+------+
                                       |
                                       |  transpile
                                       |
                                       |
                                       v
 +--------------+                +------------+
 |              |    compile     |            |
 |  executable  |<---------------+    C++     |
 |   birocode   |                |            |
 |              |                +------------+
 +--------------+
```