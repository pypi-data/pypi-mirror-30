# -*- coding:utf-8 -*-
import sys
import re
import os
import time
import copy
import json
import platform

if sys.version[0] != '2':
    from functools import reduce

    raw_input = input


class T(object):
    version = 'V2.0.8'
    __log_title = 'FuncLib ( ' + version + ' ) --> T.log'
    __log_title_fix = 'FuncLib ( ' + version + ' ) --> T.'

    @staticmethod
    def info():
        keys = T.each(lambda x: T.replace(r'\n|\s|=', '', x[:8]), T.__info.split('T.')[1:])
        docs_vars = vars(T)
        docs_keys = T.each(lambda x: '_T__' + x, keys)
        docs = {}
        for key in keys:
            docs[key] = docs_vars[docs_keys[keys.index(key)]]
        return {'keys': keys, 'docs': docs}

    __info = """
===================================================================================
                                    Func-Lib
                    A data processing methods lib for Python(2/3)
-----------------------------------------------------------------------------------
                             Author: @CN-Tower
                          Create At: 2018-2-2
                          Update At: 2018-3-15
                            Version: """ + version + """
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
    """

    @staticmethod
    def index(predicate, _list):
        if _list and T.typeof(_list, list, map, tuple):
            if predicate in _list:
                return _list.index(predicate)
            elif isinstance(predicate, dict):
                for i in range(0, len(_list)):
                    tmp_bool = True
                    for key in predicate:
                        if key not in _list[i] or predicate[key] != _list[i][key]:
                            tmp_bool = False
                            break
                    if tmp_bool:
                        return i
                return -1
            elif T.typeof(predicate, 'func'):
                for i in range(0, len(_list)):
                    if predicate(_list[i]):
                        return i
            return -1
        return -1

    __index = """ 
    ### T.index
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
    """

    @staticmethod
    def find(predicate, _list):
        idx = T.index(predicate, _list)
        if idx != -1:
            return _list[idx]
        return None

    __find = """
    ### T.find
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
    """

    @staticmethod
    def filter(predicate, _list):
        tmp_list = T.clone(_list)
        ret_list = []
        while True:
            index = T.index(predicate, tmp_list)
            if index == -1:
                break
            else:
                ret_list.append(tmp_list[index])
                if index < len(tmp_list) - 1:
                    tmp_list = tmp_list[index + 1:]
                else:
                    break
        return ret_list

    __filter = """
    ### T.filter
        Looks through each value in the list, returning an array of all the values
        that pass a truth test (predicate).
        eg:
            from funclib import T
            persons = [{"name": "Tom", "age": 20},
                       {"name": "Jerry", "age": 20},
                       {"name": "Jerry", "age": 35}]

            Jerry = T.filter({"age": 20}, persons)
            Mary = T.filter(lambda x: x['name'] == 'Jerry', persons)
            print(Jerry)  # => [{'age': 20, 'name': 'Tom'},
                                {'age': 20, 'name': 'Jerry'}]
            print(Mary)   # => [{'age': 20, 'name': 'Jerry'},
                                {'age': 35, 'name': 'Jerry'}]
    """

    @staticmethod
    def reject(predicate, _list):
        index = T.index(predicate, _list)
        if index != -1:
            tmp_list = T.clone(_list)
            del tmp_list[index]
            return T.reject(predicate, tmp_list)
        return _list

    __reject = """
    ### T.reject
        Returns the values in list without the elements that the truth test (predicate)
        passes.
        The opposite of filter.
        eg:
            from funclib import T
            persons = [{"name": "Tom", "age": 12},
                       {"name": "Jerry", "age": 20},
                       {"name": "Mary", "age": 35}]

            not_Mary = T.reject({"name": "Mary"}, persons)
            adults = T.reject(lambda x: x['age'] < 18, persons)

            print(not_Mary)  # => [{"age": 12, "name": "Tom"},
                                   {"age": 20, "name": "Jerry"}]
            print(adults)    # => [{"age": 20, "name": "Jerry"},
                                   {"age": 35, "name": "Mary"}]
    """

    @staticmethod
    def reduce(*args):
        return reduce(*args)

    __reduce = """
    ### T.reduce
        Returns the buildIn method 'reduce', in python 3 the 'reduce' is imported
        from functools.
        eg:
            from funclib import T
            num_list = [1 , 2, 3, 4]
            print(T.reduce(lambda a, b: a + b, num_list))  # => 10
    """

    @staticmethod
    def contains(predicate, _list):
        index = T.index(predicate, _list)
        return index != -1

    __contains = """
    ### T.contains
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
    """

    @staticmethod
    def flatten(_list, is_deep=False):
        if _list and T.typeof(_list, list, map):
            tmp_list = []
            for item in _list:
                if isinstance(item, list):
                    if is_deep:
                        tmp_list += T.flatten(item, True)
                    else:
                        tmp_list += item
                else:
                    tmp_list.append(item)
            return tmp_list
        return _list

    __flatten = """
    ### T.flatten
        Flattens a nested array (the nesting can be to any depth). If you pass shallow,
        the array will only be flattened a single level.
        eg:
            from funclib import T
            flt_list_01 = T.flatten([1, [2], [3, [[4]]]])
            flt_list_02 = T.flatten([1, [2], [3, [[4]]]], True)
            print(flt_list_01)  # => [1, 2, 3, [[4]]]
            print(flt_list_02)  # => [1, 2, 3, 4];
    """

    @staticmethod
    def each(*args):
        return list(map(*args))

    __each = """
    ### T.each
        Produces a new values list by mapping each value in list through a transformation
        function (iteratee). 
        eg:
            from funclib import T
            num_list = [1 , 2, 3, 4]
            list_10 = T.each(lambda x: x % 2, num_list)
            print(list_10)  #=> [1, 0, 1, 0]
    """

    @staticmethod
    def uniq(_list, *args):
        tmp_list = T.clone(_list)
        if T.typeof(tmp_list, tuple, map):
            tmp_list = list(tmp_list)
        if tmp_list and T.typeof(tmp_list, list):
            if len(args) == 0:
                for i in range(0, len(tmp_list)):
                    if len(tmp_list) <= i + 1:
                        break
                    tmp_list = tmp_list[:i + 1] + T.reject(
						lambda x: x == tmp_list[i], tmp_list[i + 1:])
            else:
                for i in range(0, len(tmp_list)):
                    if len(tmp_list) <= i + 1:
                        break
                    tmp_list = tmp_list[:i + 1] + T.reject(
                        lambda x: T.__cpr_val(args, x, tmp_list[i]), tmp_list[i + 1:])
        return tmp_list
    
    @staticmethod
    def __cpr_val(args, dict1, dict2):
        v1 = T.__get_val(args, dict1)
        v2 = T.__get_val(args, dict2)
        return  v1[0] and v2[0] and v1[1] == v2[1]
    
    @staticmethod
    def __get_val(args, _dict):
        tmp_val = _dict
        for i in range(0, len(args)):
            if T.typeof(tmp_val, dict) and tmp_val.has_key(args[i]):
                tmp_val = tmp_val[args[i]]
            else:
                return False, None
        return True, tmp_val
    
    __uniq = """
    ### T.uniq
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
    """

    @staticmethod
    def pluck(body, *key, **opt):
        if isinstance(body, dict):
            tmp_body = [body]
        else:
            tmp_body = body
        if T.typeof(tmp_body, list, map, tuple):
            for k in key:
                field_k = T.each(lambda x: x[k], tmp_body)
                if len(field_k) > 0:
                    tmp_body = reduce(T.list, T.each(lambda x: x[k], tmp_body))
                tmp_body = T.list(tmp_body)
            if bool(opt) and "uniq" in opt and opt['uniq']:
                tmp_body = T.uniq(tmp_body)
        return tmp_body

    __pluck = """
    ### T.pluck
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
    """

    @staticmethod
    def pick(origin, *layers, **kwargs):
        if 'new_layers' in kwargs:
            layers = kwargs['new_layers']
        if origin and layers:
            layer = layers[0]
            if isinstance(origin, dict) and layer in origin:
                if len(layers) == 1:
                    return origin[layer]
                elif len(layers) > 1:
                    return T.pick(origin[layer], new_layers=layers[1:])
            if T.typeof(origin, list, map, tuple):
                if isinstance(layer, list) and len(layer) == 1 \
                        and isinstance(layer[0], int) and -len(origin) <= layer[0] < len(origin):
                    if len(layers) == 1:
                        return origin[layer[0]]
                    elif len(layers) > 1:
                        return T.pick(origin[layer[0]], new_layers=layers[1:])
                else:
                    layer_val = T.find(layer, origin)
                    if layer_val:
                        if len(layers) == 1:
                            return layer_val
                        elif len(layers) > 1:
                            return T.pick(layer_val, new_layers=layers[1:])
        if 'default' in kwargs:
            return kwargs['default']
        else:
            return None

    __pick = """
    ### T.pick
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
    """

    @staticmethod
    def every(predicate, _list):
        if _list and T.typeof(_list, list, map, tuple):
            for item in _list:
                if predicate != item:
                    if isinstance(predicate, dict):
                        for key in predicate:
                            if key not in item or predicate[key] != item[key]:
                                return False
                    elif T.typeof(predicate, 'func'):
                        if not bool(predicate(item)):
                            return False
                    else:
                        return False
            return True
        return False

    __every = """
    ### T.every
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
    """

    @staticmethod
    def some(predicate, _list):
        if _list and T.typeof(_list, list, map, tuple):
            for item in _list:
                if predicate != item:
                    if isinstance(predicate, dict):
                        tmp_bool = True
                        for key in predicate:
                            if key not in item or predicate[key] != item[key]:
                                tmp_bool = False
                        if tmp_bool:
                            return True
                    elif T.typeof(predicate, 'func'):
                        if bool(predicate(item)):
                            return True
                else:
                    return True
            return False
        return False

    __some = """
    ### T.some
        Returns true if any of the values in the list pass the predicate
        truth test. Short-circuits and stops traversing the list if a true
        element is found.
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
    """

    @staticmethod
    def list(*values):
        def list_handler(val):
            if isinstance(val, list):
                return val
            return [val]

        if len(values) == 0:
            return []
        elif len(values) == 1:
            return list_handler(values[0])
        else:
            return reduce(lambda a, b: list_handler(a) + list_handler(b), values)

    __list = """
    ### T.list
        Return now system time.
        eg:
            from funclib import T
            print(T.list())       # => []
            print(T.list([]))     # => []
            print(T.list({}))     # => [{}]
            print(T.list(None))   # => [None]
            print(T.list('test')) # => ['test']
    """

    @staticmethod
    def drop(_list, is_without_0=False):
        if bool(_list):
            if isinstance(_list, tuple):
                _list = list(_list)
            if isinstance(_list, list):
                tmp_list = []
                for item in _list:
                    if bool(item) or (is_without_0 and item == 0):
                        tmp_list.append(item)
                return tmp_list
        return _list

    __drop = """
    ### T.drop
        Delete false values expect 0.
        eg:
            from funclib import T
            tmp_list = [0, '', 3, None, [], {}, ['Yes'], 'Test']
            drop_val = T.drop(tmp_list)
            without_0 = T.drop(tmp_list, True)

            print(drop_val)  # => [3, ['Yes'], 'Test']
            print(without_0)  # => [0, 3, ['Yes'], 'Test']
    """

    @staticmethod
    def dump(_json):
        if isinstance(_json, list) or isinstance(_json, dict) or isinstance(_json, tuple):
            return json.dumps(_json, sort_keys=True, indent=2)
        return _json

    __dump = """
    ### T.dump
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
    """

    @staticmethod
    def clone(obj):
        return copy.deepcopy(obj)

    __clone = """
    ### T.clone
        Create a deep-copied clone of the provided plain object.
        eg:
            from funclib import T
            persons = [{"name": "Tom", "age": 12},
                       {"name": "Jerry", "age": 20}]
            persons_01 = persons
            persons_02 = T.clone(persons)
            T.find({'name': 'Tom'}, persons)['age'] = 18

            print(persons_01)  # => [{"name": "Tom", "age": 18},
                                     {"name": "Jerry", "age": 20}]
            print(persons_02)  # => [{"name": "Tom", "age": 12},
                                     {"name": "Jerry", "age": 20}]
    """

    @staticmethod
    def test(pattern, origin):
        return re.search(pattern, origin) is not None

    __test = """
    ### T.test
        Check is the match successful, a boolean value will be returned.
        eg:
            from funclib import T
            not_in = T.test(r'ab', 'Hello World!')
            in_str = T.test(r'll', 'Hello World!')
            print(not_in)  # => False
            print(in_str)  # => True
    """

    @staticmethod
    def replace(*args):
        return re.sub(*args)

    __replace = """
    ### T.replace
        Replace sub string of the origin string with re.sub()
        eg:
            from funclib import T
            greetings = 'Hello I\'m Tom!'
            print(T.replace(r'Tom', 'Jack', greetings)) # => Hello I'm Jack!
    """

    @staticmethod
    def iscan(exp):
        if isinstance(exp, str):
            try:
                exec (exp)
                return True
            except:
                return False
        return False

    __iscan = """
    ### T.iscan
        Test is the expression valid, a boolean value will be returned.
        eg:
            from funclib import T
            print(T.iscan("int('a')"))  # => False
            print(T.iscan("int('5')"))  # => True
    """

    @staticmethod
    def log(*msgs, **conf):
        line_len = 87
        title = T.__log_title
        if 'title' in conf and str(conf['title']):
            tt = str(conf['title'])
            title = len(tt) <= 35 and tt or tt[:35]
        if 'len' in conf and T.typeof(conf['len'], int) and conf['len'] > 40:
            line_len = conf['len']
        line_b = '=' * line_len
        line_m = '-' * line_len
        line_s = '- ' * int((line_len / 2))
        title = ' ' * int((line_len - len(title)) / 2) + title
        print('%s\n%s\n%s' % (line_b, title, line_m))
        if len(msgs) > 0:
            for i in range(0, len(msgs)):
                if i > 0:
                    print(line_s)
                print(T.dump(msgs[i]))
        else:
            print('Have no Message!')
        print(line_b)

    __log = """
    ### T.log
        Show log clear in console.
        eg:
            from funclib import T
            persons = [{"name": "Tom", "hobbies": ["sing", "running"]},
                       {"name": "Jerry", "hobbies": []}]

            T.log(persons)  # =>
===========================================================================
                        """ + __log_title + """
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
    """

    @staticmethod
    def timer(fn, times=60, interval=1):
        if not T.typeof(fn, 'func') or not isinstance(times, int) or not isinstance(interval, int) \
                or times < 1 or interval < 0:
            return
        is_time_out = False
        count = 0
        while True:
            count += 1
            if count == times:
                fn()
                is_time_out = True
                break
            elif fn():
                break
            time.sleep(interval)
        return is_time_out

    __timer = """
    ### T.timer
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
    """

    @staticmethod
    def now():
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    __now = """
    ### T.now
        Return now system time.
        eg:
            from funclib import T
            print(T.now()) # => '2018-2-1 19:32:10'
    """

    @staticmethod
    def help(*args, **kwargs):
        row_cols = 6
        docs_info = T.info()
        keys = docs_info['keys']
        docs = docs_info['docs']
        max_key_len = max(T.each(lambda x: len(x), keys)) + 6
        if len(args) > 0:
            is_show_hint = False
            if args[0] in keys:
                T.clear()
                if args[0] == 'info':
                    print(docs['info'])
                else:
                    is_show_hint = True
                    T.log(docs[args[0]], title=T.__log_title_fix + args[0])
            if 'keep' in kwargs and kwargs['keep']:
                T.help(hint=is_show_hint, **kwargs)
        else:
            if not ('keep' in kwargs and kwargs['keep']):
                T.clear()
                print(docs['info'])
            elif 'hint' in kwargs and kwargs['hint']:
                print('')
                hints = T.each(lambda x: T.__fix_str(
                    T.__fix_str(str(keys.index(x))) + x, keys.index(x) % row_cols + 1, max_key_len
                ), keys)
                end = 0
                while True:
                    sta = end
                    end += row_cols
                    if end > len(hints):
                        hints.append(' ' * (end - len(hints)) * max_key_len + ' ')
                        end = len(hints)
                    print('[ ' + reduce(lambda a, b: a + ' ' + b, hints[sta:end]) + ']')
                    if end == len(hints):
                        break
                print('')
            idx = raw_input('Input a method or it\'s index (Nothing input will Return!): ')
            if idx:
                if T.iscan('int(%s)' % idx) and int(idx) in range(0, len(keys)):
                    T.clear()
                    is_show_hint = False
                    key = keys[int(idx)]
                    if idx == '0':
                        print(docs[key])
                    else:
                        is_show_hint = True
                        T.log(docs[key], title=T.__log_title_fix + key)
                    T.help(keep=True, hint=is_show_hint)
                else:
                    T.help(idx, keep=True)

    @staticmethod
    def __fix_str(string, column=0, max_len=14):
        str_len = len(string)
        tmp_str = string
        if column == 0:
            tmp_str = string + ': T.'
            if str_len == 1:
                tmp_str = '0' + tmp_str
        elif str_len < max_len:
            tmp_str = string + ' ' * (max_len - str_len - 1)
            if column == 1 or column == 2:
                tmp_str += ' '
            elif column == 3:
                tmp_str = tmp_str[:-1]
        return tmp_str

    @staticmethod
    def clear():
        if platform.system() == "Windows":
            os.system('cls')
        else:
            os.system('clear')

    @staticmethod
    def typeof(var, *types):
        if len(types) > 0:
            for _type in types:
                if (isinstance(_type, type) and isinstance(var, _type)) \
                        or (_type == 'func' and 'function' in str(type(var))):
                    return True
        return False
