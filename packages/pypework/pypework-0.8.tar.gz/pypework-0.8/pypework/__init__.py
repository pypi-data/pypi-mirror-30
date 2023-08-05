## Pipeable Object Classes ##

class AbstractPipeFunction:
    def __init__(self, function, *arguments, **keywords):
        self.function = function
        self.arguments = arguments
        self.keywords = keywords

    def __rrshift__(self, other):
        return self(other)

class PipeFunction(AbstractPipeFunction):
    def __call__(self, operand):
        return self.function(operand, *self.arguments, **self.keywords)

class PartialPipeFunction(AbstractPipeFunction):
    def __call__(self, operand):
        def replace_placeholders(argument):
            if argument.__class__ == Placeholder:
                return argument._invoke_on(operand)
            else:
                return argument

        arguments = map(replace_placeholders, self.arguments)
        keywords = { k:replace_placeholders(v) for (k,v) in self.keywords.items() }
        
        return self.function(*arguments, **keywords)

        

## Identifier Chain Processor Classes ##

import inspect

class AbstractIdentifierCatcher:
    def __init__(self, _identifier_chain=None, scope=None):
        if _identifier_chain:
            self._identifier_chain = _identifier_chain
        elif scope:
            self._identifier_chain = __import__(scope)
        else:
            caller_frame = inspect.currentframe().f_back
            detected_module_name = caller_frame.f_globals.get("__name__", "<unknown module>")
            self._identifier_chain = __import__(detected_module_name)

    def __getattr__(self, name):
        return self.__class__( getattr(self._identifier_chain, name) )

    def __rrshift__(self, other):
        return self()(other)

class FunctionCatcher(AbstractIdentifierCatcher):
    def __call__(self, *arguments, **keywords):
        return PipeFunction(self._identifier_chain, *arguments, **keywords)

class PartialCatcher(AbstractIdentifierCatcher):
    def __call__(self, *arguments, **keywords):
        return PartialPipeFunction(self._identifier_chain, *arguments, **keywords)

def invoke_deferred_chain(input_object, chain):
    head = chain[0]
    
    if len(chain) == 1:
        return head.invoke_on(input_object)
    else:
        tail = chain[1:]
        sub_object = head.invoke_on(input_object)
        return invoke_deferred_chain(sub_object, tail)

class DeferredAttribute:
    def __init__(self, attribute_name):
        self._attribute_name = attribute_name

    def invoke_on(self, input):
        return getattr(input, self._attribute_name)

    def __repr__(self):
        return f"DeferredAttribute: .{self._attribute_name}"

class DeferredMethodCall:
    def __init__(self, *arguments, **keywords):
        self.arguments = arguments
        self.keywords = keywords

    def invoke_on(self, input):
        return input(*self.arguments, **self.keywords)

    def __repr__(self):
        return f"DeferredMethodCall: {self.arguments} {self.keywords}"

class DeferredSubscript:
    def __init__(self, key):
        self.key = key

    def invoke_on(self, input):
        return input.__getitem__(self.key)

    def __repr__(self):
        return f"DeferredSubscript: {self.key}"

class Placeholder:
    def __init__(self, chain=[]):
        self._chain = chain

    def __add_link(self, new_link):
        new_chain = [*self._chain, new_link]
        return Placeholder(chain = new_chain)

    def __getattr__(self, attribute):
        return self.__add_link( DeferredAttribute(attribute) )

    def __getitem__(self, key):
        return self.__add_link( DeferredSubscript(key) )

    def __call__(self, *arguments, **keywords):
        return self.__add_link( DeferredMethodCall(*arguments, **keywords) )

    def _invoke_on(self, input_object):
        if self._chain == []:
            return input_object
        else:
            return invoke_deferred_chain(input_object, self._chain)

    def __repr__(self):
        return f"ChainCatcher: {self._chain}"

    def __rrshift__(self, other):
        return self._invoke_on(other)

## Placeholders ##
    
____ = Placeholder()