# Example

## Factory

```yaml
services:
  MyService:
    factory: [my_package.my_file.MyFactoryClass, my_static_method_name]
    arguments: [...] # arguments for `my_static_method_name`
    calls: [...] # call to methods of returned object from factory
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
