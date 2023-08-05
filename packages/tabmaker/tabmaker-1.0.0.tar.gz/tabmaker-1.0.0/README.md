tabmaker
========

This program installs a script which generates song lyrics with chords above the correct words given a file in the correct format.

Syntax:
```
tabmaker in_file[ out_file]
```

infile must be a plain text file with square brackets around the chords:

```
[c]Twinkle, twinkle [f]little [c]star,
[f]How I [c]wonder [g]what you [c]are.
```

outfile is optional (defaults to the standard output) and prints the chords above the lyrics like so:

```
c                f      c    
Twinkle, twinkle little star,
f     c      g        c   
How I wonder what you are.
```
