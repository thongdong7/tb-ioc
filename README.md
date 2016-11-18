# Example

## Factory

### Create object by calling a static method of class.

```yaml
services:
  MyService:
    factory: [my_package.my_file.MyFactoryClass, my_static_method_name]
    arguments: [...] # arguments for `my_static_method_name`
    calls: [...] # call to methods of returned object from factory
```

### Create a factory object for class

Use to hide object class

```yaml
services:
  AbcFactory:
    factory_class: my_package.abc.Abc
```

at another place, you could create `Abc` object by use `AbcFactory` instead of remember the long class name `my_package.abc.Abc`
 
```yaml
services:
  MyAbc:
    factory: AbcFactory
    arguments: [arg1, arg2]
```


## Calls

```yaml
services:
  MyService:
    class: ...
    calls:
      - [method_without_arguments]
      - [method_with_arguments, [arg1, arg2]]
```
