# FuncLib
```
    ===================================================================================
                                        FuncLib
                        A data processing methods lib for Python(2/3)
    -----------------------------------------------------------------------------------
                                 Author: @CN-Tower
                              Create At: 2018-2-2
                              Update At: 2018-3-15
                                Version: V2.0.8
                                 GitHub: http://github.com/CN-Tower/FuncLib
    -----------------------------------------------------------------------------------
                          0: T.info                 1: T.index
                          2: T.find                 3: T.filter
                          4: T.reject               5: T.reduce
                          6: T.contains             7: T.flatten
                          8: T.each                 9: T.uniq
                         10: T.pluck               11: T.pick
                         12: T.every               13: T.some
                         14: T.list                15: T.drop
                         16: T.dump                17: T.clone
                         18: T.test                19: T.replace
                         20: T.iscan               21: T.log
                         22: T.timer               23: T.now
    ===================================================================================
```
## Quick Start
```
$ pip install funclib
$ python
>>> from funclib import T         # If Python3 uses "from funclib.funclib import T" instead!
>>> T.help()
```
## Methods
 * [T.index   ](#tindex)
 * [T.find    ](#tfind)
 * [T.filter  ](#tfilter)
 * [T.reject  ](#treject)
 * [T.reduce  ](#treduce)
 * [T.contains](#tcontains)
 * [T.flatten ](#tflatten)
 * [T.each    ](#teach)
 * [T.uniq    ](#tuniq)
 * [T.pluck   ](#tpluck)
 * [T.pick    ](#tpick)
 * [T.every   ](#tevery)
 * [T.some    ](#tsome)
 * [T.list    ](#tlist)
 * [T.drop    ](#tdrop)
 * [T.dump    ](#tdump)
 * [T.clone   ](#tclone)
 * [T.test    ](#ttest)
 * [T.replace ](#treplace)
 * [T.iscan   ](#tiscan)
 * [T.log     ](#tlog)
 * [T.timer   ](#ttimer)
 * [T.now     ](#tnow)
 * [T.help    ](#thelp)
## Document
### T.index
```
    Looks through the list and returns the item index. If no match is found,
    or if list is empty, -1 will be returned.
    eg:
        from funclib import T
        persons = [{"name": "Tom", "age": 12},
            {"name": "Jerry", "age": 20},
            {"name": "Mary", "age": 35}]

        Jerry_idx = T.index({"name": 'Jerry'}, persons)
        Mary_idx  = T.index(lambda x: x['name'] == 'Mary', persons)

        print(Jerry_idx)  # => 1
        print(Mary_idx)   # => 2

```
### T.find
```
    Looks through each value in the list, returning the first one that passes
    a truth test (predicate), or None.If no value passes the test the function
    returns as soon as it finds an acceptable element, and doesn't traverse
    the entire list.
    eg:
        from funclib import T
        persons = [{"name": "Tom", "age": 12},
            {"name": "Jerry", "age": 20},
            {"name": "Mary", "age": 35}]

        Jerry = T.find({"name": 'Jerry'}, persons)
        Mary  = T.find(lambda x: x['name'] == 'Mary', persons)

        print(Jerry)  # => {'age': 20, 'name': 'Jerry'}
        print(Mary)   # => {'age': 35, 'name': 'Mary'}

```
### T.filter
``` 
    Looks through each value in the list, returning an array of all the values that
    pass a truth test (predicate).
    eg:
        from funclib import T
        persons = [{"name": "Tom", "age": 20},
                   {"name": "Jerry", "age": 20},
                   {"name": "Jerry", "age": 35}]

        Jerry = T.filter({"age": 20}, persons)
        Mary = T.filter(lambda x: x['name'] == 'Jerry', persons)
        print(Jerry)  # => [{'age': 20, 'name': 'Tom'}, {'age': 20, 'name': 'Jerry'}]
        print(Mary)   # => [{'age': 20, 'name': 'Jerry'}, {'age': 35, 'name': 'Jerry'}]
        
```
### T.reject
``` 
    Returns the values in list without the elements that the truth test (predicate) passes.
    The opposite of filter.
    eg:
        from funclib import T
        persons = [{"name": "Tom", "age": 12},
                   {"name": "Jerry", "age": 20},
                   {"name": "Mary", "age": 35}]

        not_Mary = T.reject({"name": "Mary"}, persons)
        adults = T.reject(lambda x: x['age'] < 18, persons)

        print(not_Mary)  # => [{"age": 12, "name": "Tom"}, {"age": 20, "name": "Jerry"}]
        print(adults)    # => [{"age": 20, "name": "Jerry"}, {"age": 35, "name": "Mary"}]

```
### T.reduce
```
    Returns the buildIn method 'reduce', in python 3 the 'reduce' is imported from functools.
    eg:
        from funclib import T
        num_list = [1 , 2, 3, 4]
        print(T.reduce(lambda a, b: a + b, num_list))  # => 10

```
### T.contains
```
    Returns true if the value is present in the list.
    eg:
        from funclib import T
        persons = [{"name": "Tom", "age": 12},
                   {"name": "Jerry", "age": 20},
                   {"name": "Mary", "age": 35}]

        is_contains_Jerry = T.contains({"name": "Jerry", "age": 12}, persons)
        is_contains_Mary = T.contains(lambda x: x['name'] == 'Mary', persons)

        print(is_contains_Jerry)  # => False
        print(is_contains_Mary)   # => True

```
### T.flatten
```
    Flattens a nested array (the nesting can be to any depth). If you pass shallow,
    the array will only be flattened a single level.
    eg:
        from funclib import T
        flt_list_01 = T.flatten([1, [2], [3, [[4]]]])
        flt_list_02 = T.flatten([1, [2], [3, [[4]]]], True)
        print (flt_list_01)  # => [1, 2, 3, [[4]]]
        print (flt_list_02)  # => [1, 2, 3, 4];

```
### T.each
```
    Produces a new values list by mapping each value in list through a transformation
    function (iteratee).
    eg:
        from funclib import T
        num_list = [1 , 2, 3, 4]
        list_10 = T.each(lambda x: x % 2, num_list)
        print(list_10)  #=> [1, 0, 1, 0]

```
### T.uniq
```
    Produces a duplicate-free version of the array.
    In particular only the first occurence of each value is kept.
    eg:
        from funclib import T
        persons00 = ("Tom", "Tom", "Jerry")
        persons01 = ["Tom", "Tom", "Jerry"]
        demo_list = [False, [], False, True, [], {}, False, '']
        persons02 = [{"name": "Tom", "age": 12, "pet": {"species": "dog", "name": "Kitty"}},
                     {"name": "Tom", "age": 20, "pet": {"species": "cat", "name": "wang"}},
                     {"name": "Mary", "age": 35, "pet": {"species": "cat", "name": "mimi"}}]
                     
        unique_persons00 = T.uniq(persons00)
        unique_persons01 = T.uniq(persons01)
        unique_demo_list = T.uniq(demo_list)
        unique_name = T.uniq(persons02, 'name')
        unique_pet = T.uniq(persons02, 'pet', 'species')
        
        print(unique_persons00)  # => ["Jerry", "Tom"]
        print(unique_persons01)  # => ["Jerry", "Tom"]
        print(unique_demo_list)  # => [False, [], True, {}, '']
        
```
### T.pluck
```
    Pluck the collections element.
    eg:
        from funclib import T
        persons = [{"name": "Tom", "hobbies": ["sing", "running"]},
            {"name": "Jerry", "hobbies": []},
            {"name": "Mary", "hobbies": ['hiking', 'sing']}]

        hobbies = T.pluck(persons, 'hobbies')
        hobbies_uniq = T.pluck(persons, 'hobbies', uniq=True)

        print(hobbies)      # => ["sing", "running", 'hiking', 'sing']
        print(hobbies_uniq) # => ["sing", "running", 'hiking']

```
### T.pick
```
    Pick values form dict or list.
    eg:
        from funclib import T
        Tom = {
            "name": "Tom",
            "age": 12,
            "pets": [
                {"species": "dog", "name": "Kitty"},
                {"species": "cat", "name": "mimi"}
            ]
        }
        pets = T.pick(Tom, 'age')
        first_pet_species = T.pick(Tom, 'pets', [0], 'species')
        find_mimi_species = T.pick(Tom, 'pets', {'name': 'mimi'}, 'species')
        find_dog_name = T.pick(Tom, 'pets', lambda x: x['species'] == 'dog', 'name')
        print(pets)               # => 12
        print(first_pet_species)  # => dog
        print(find_mimi_species)  # => cat
        print(find_dog_name)      # => Kitty
            
```
### T.every
```
    Returns true if all of the values in the list pass the predicate truth test.
    Short-circuits and stops traversing the list if a false element is found.
    eg:
        from funclib import T
        num_list = [1, 1, 2, 3, 5, 8]
        persons = [{"name": "Tom", "age": 12, "sex": "m"},
                   {"name": "Jerry", "age": 20, "sex": "m"},
                   {"name": "Mary", "age": 35, "sex": "f"}]

        is_all_five = T.every(5, num_list)
        is_all_male = T.every({"sex": "m"}, persons)
        is_all_adult = T.every(lambda x: x['age'] > 18, persons)
        print(is_all_five)   # => False
        print(is_all_male)   # => False
        print(is_all_adult)  # => False

```
### T.some
```
    Returns true if any of the values in the list pass the predicate truth test.
    Short-circuits and stops traversing the list if a true element is found.
    eg:
        from funclib import T
        num_list = [1, 1, 2, 3, 5, 8]
        persons = [{"name": "Tom", "age": 12, "sex": "m"},
                   {"name": "Jerry", "age": 20, "sex": "m"},
                   {"name": "Mary", "age": 35, "sex": "f"}]

        is_any_five = T.some(5, num_list)
        is_any_male = T.some({"sex": "m"}, persons)
        is_any_adult = T.some(lambda x: x['age'] > 18, persons)
        print(is_any_five)   # => True
        print(is_any_male)   # => True
        print(is_any_adult)  # => True

```
### T.list
```
    Return now system time.
    eg:
        from funclib import T
        print(T.list())       # => []
        print(T.list([]))     # => []
        print(T.list({}))     # => [{}]
        print(T.list(None))   # => [None]
        print(T.list('test')) # => ['test']

```
### T.drop
```
    Delete false values expect 0.
    eg:
        from funclib import T
        tmp_list = [0, '', 3, None, [], {}, ['Yes'], 'Test']
        drop_val = T.drop(tmp_list)
        without_0 = T.drop(tmp_list, True)

        print(drop_val)  # => [3, ['Yes'], 'Test']
        print(without_0)  # => [0, 3, ['Yes'], 'Test']

```
### T.dump
```
    Return a formatted json string.
    eg:
        from funclib import T
        persons = [{"name": "Tom", "hobbies": ["sing", "running"]},
            {"name": "Jerry", "hobbies": []}]
        print(T.dump(persons)) #=>
        [
          {
            "hobbies": [
              "sing",
              "running"
            ],
            "name": "Tom"
          },
          {
            "hobbies": [],
            "name": "Jerry"
          }
        ]

```
### T.clone
```
    Create a deep-copied clone of the provided plain object.
    eg:
        from funclib import T
        persons = [{"name": "Tom", "age": 12}, {"name": "Jerry", "age": 20}]
        persons_01 = persons
        persons_02 = T.clone(persons)
        T.find({'name': 'Tom'}, persons)['age'] = 18
        print(persons_01)  # => [{"name": "Tom", "age": 18}, {"name": "Jerry", "age": 20}]
        print(persons_02)  # => [{"name": "Tom", "age": 12}, {"name": "Jerry", "age": 20}]

```
### T.test
```
    Check is the match successful, a boolean value will be returned.
    eg:
        from funclib import T
        not_in = T.test(r'ab', 'Hello World!')
        in_str = T.test(r'll', 'Hello World!')
        print(not_in)  # => False
        print(in_str)  # => True

```
### T.replace
```
    Replace sub string of the origin string with re.sub()
    eg:
        from funclib import T
        greetings = 'Hello I\'m Tom!'
        print(T.replace('Tom', 'Jack', greetings))  # => Hello I'm Jack!

```
### T.iscan
```
    Test is the expression valid, a boolean value will be returned.
    eg:
        from funclib import T
        print(T.iscan("int('a')"))  # => False
        print(T.iscan("int('5')"))  # => True

```
### T.log
```
    Show log clear in console.
    eg:
        from funclib import T
        T.log([{"name": "Tom", "hobbies": ["sing", "running"]}, {"name": "Jerry", "hobbies": []}])

        # =>
        ===========================================================================
                                    FuncLib ( V2.0.8 )
        ---------------------------------------------------------------------------
        [
          {
            "hobbies": [
              "sing",
              "running"
            ],
            "name": "Tom"
          },
          {
            "hobbies": [],
            "name": "Jerry"
          }
        ]
        ===========================================================================

```
### T.timer
```
    Set a timer with interval and timeout limit.
    eg:
        from funclib import T
        count = 0
        def fn():
            global count
            if count == 4:
                return True
            count += 1
            print(count)
        T.timer(fn, 10, 2)
        # =>
            >>> 1  #at 0s
            >>> 2  #at 2s
            >>> 3  #at 4s
            >>> 4  #at 4s

```
### T.now
```
    Return now system time.
    eg:
        from funclib import T
        print(T.now()) # => '2018-2-1 19:32:10'

```
### T.help
```
    Return the FuncLib or it's method doc
    eg:
        from funclib import T
        T.help('index')
        # =>
    ===========================================================================
                            FuncLib ( V2.0.8 ) --> T.index
    ---------------------------------------------------------------------------
        Looks through the list and returns the item index. If no match is found,
        or if list is empty, -1 will be returned.
        eg:
            from funclib import T
            persons = [{"name": "Tom", "age": 12},
                {"name": "Jerry", "age": 20},
                {"name": "Mary", "age": 35}]

            Jerry_idx = T.index({"name": 'Jerry'}, persons)
            Mary_idx  = T.index(lambda x: x['name'] == 'Mary', persons)

            print(Jerry_idx)  # => 1
            print(Mary_idx)   # => 2
    ===========================================================================

```
