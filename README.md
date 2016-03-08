# Shiv

A different kind of cut that makes it easier to extract the kinds of things I tend to need to extract.

Also, a toy project for learning more rust.

Split by delimiter
```
shiv -d '\t' -f 1-4 6-9
```

Extract fields by regular expression
```
shiv -e '\d+' -f 1-2
shiv -e 'a(foo)b(bar)c'
```

Extract fields from given formats
```
shiv --csv -f 2-4
shiv --tsv -f 3
```
