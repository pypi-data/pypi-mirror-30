from validation import Validation
import re
import json

class Validator(object):

    def __init__(self, it:any):
        self.it = it

    def __validate(self, validation:Validation, it:any, *args):
        if validation == Validation.EQUALS:
            for value in args:
                print(it,value)
                if it != value: return False
            return True
        elif validation == Validation.ANY:
            for value in args:
                 if it == value: return True
            return False
        elif validation == Validation.NONE:
            for value in args:
                 if it == value: return False
            return True
        else: return False
  

    def __parse(self, notation:str, validation:Validation, it:any, *args):
        if re.match('[A-Za-z0-9]+([.][A-Za-z0-9]+)*', notation) == None: return False
        elif isinstance(it, (list, tuple)):            
            return self.__parse(notation, validation, {str(i):it[i] for i in range(len(it))}, *args)
        elif isinstance(it, dict):
            if len(notation.split(".")) == 1:
                key = notation.split(".")[0]
                if key not in it: raise Exception("Not found: "+notation)
                return self.__validate(validation, it[key], *args)
            elif len(notation.split(".")) == 2:
                splitNotation = notation.split(".")
                innerKey = splitNotation[1]
                outerKey = splitNotation[0]
                del splitNotation[0]
                notation = ".".join(splitNotation)
                if isinstance(it[outerKey], dict):
                    return self.__validate(validation, it[outerKey][innerKey], *args)
                return self.__parse(notation, validation, it[outerKey], *args)
            else:
                splitNotation = notation.split(".")
                key = splitNotation[0]
                del splitNotation[0]
                notation = ".".join(splitNotation)
                if key not in it: raise Exception("Not found: "+notation)
                return self.__parse(notation, validation, it[key], *args)

        else: return self.__validate(validation, it, args)

    def parse_and_validate(self, notation:str, validation:Validation, *args):
        return self.__parse(notation,validation, self.it, *args)

validator = Validator(json.loads('[{ "name":"John", "age":30, "cars": [ {"name":"Ford", "type":"sedan"}, {"name":"Nissan", "type":"truck"}, {"name":null, "type":"truck"} ] }]'))
#validator = Validator(json.loads('{ "name":"John", "age":30, "cars": { "car1":"Ford", "car2":"BMW", "car3":"Fiat" } }'))
print(validator.parse_and_validate("cars.2.name", Validation.EQUALS, None))

