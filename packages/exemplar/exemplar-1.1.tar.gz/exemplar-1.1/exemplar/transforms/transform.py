import inspect
from linked_list import LinkedList

class Transform(object):

    """
    If aux_types is:

    ```
    aux_types = {
      'ex_key_1' : dict
    }
    ```

    Then, a user of the Exemplar API can do:

    ```
    Parser(
      src=['an', 'example', 'sentence', '.'],
      src_aux={ 'vocabulary':['an', 'example', 'sentence', '.'] },
      trg=[ [1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1] ]
    )
    ```

    using an arbitrary key, like 'vocabulary', in `src_aux`, and Exemplar will
    check if 'vocabulary' and 'ex_key_1' represent the same data.

    Importantly:

    - Every aux key used in `transform` should appear in `aux_types`.
    - The example aux types can be object, allowing any type.
    """
    aux_types = {}  # keys --> types

    def __init__(self):
        self.aux = None

    @staticmethod
    def transform(src_aux):
        """
        This reducer processes `src_aux`

        @returns out_aux (dict): transformed `src_aux` 

        TODO: Can we guarantee that this does not mutate `src_aux`?
        """
        raise NotImplementedError

    def process_line(self, src, src_aux=None):
        """
        Calls transform, and then updates self.aux
        """
        if src_aux is None:
            src_aux = {}
        src_aux[None] = src
        out_aux = self.transform(src_aux)
        self.update_aux(out_aux)
        return out_aux[None]

    def update_aux(self, new_aux):
        """Merge new_aux into self.aux"""
        if self.aux is None:
            self.aux = new_aux  # copy?
            return

        for key, val in new_aux.items():
            if key is None:
                # this is returned by `process_line`, mutating it would create an
                # aliasing issue 
                continue
            
            if isinstance(val, set):
                self.aux[key].update(val)
            elif isinstance(val, list):
                self.aux[key].extend(val)
            elif isinstance(val, int):
                self.aux[key] += val
            elif isinstance(val, bool):
                self.aux[key] = self.aux[key] or val
            elif isinstance(val, dict):
                self.aux[key].update(val)

    def process_lines(self, lines, src_aux=None):
        if isinstance(lines, str):
            with open(lines, 'r') as f:
                lines = f.readlines()

        for line in lines:
            yield self.process_line(line, src_aux)

    __call__ = process_lines


class TransformChain(Transform, LinkedList):
    """
    A single transform formed of a chain of transforms sequentially applied.
    """
    def __init__(self, *transforms):
        Transform.__init__(self)
        LinkedList.__init__(self, *transforms)
        
    def transform(self, aux):
        return reduce(
            lambda aux, transform:transform.transform(aux),
            self,
            aux
        )

    def __repr__(self):
        return 'Chain({})'.format(repr(list(self))[1:-1])


class TransformMap(Transform):
    """
    A transform formed by renaming src_aux keys
    """
    def __init__(self, out2src_keys):
        """
        Arguments:
          - out2src_keys (dict)
        """
        super(TransformMap, self).__init__()
        self.src2out_keys = { 
            src_key: out_key for out_key, src_key in out2src_keys.items()
        }
    
    def transform(self, src_aux):
        return { self.src2out_keys[k] : v 
                 for k, v in src_aux.items() 
                 if k in self.src2out_keys }

    def __repr__(self):
        return "Map({})".format(repr(self.src2out_keys))


class CompoundTransform(Transform):
    """
    A Transform that is defined as the combination of other Transforms
    """

    # TODO: Build a trie from the transforms, to avoid recomputing common 
    # chain beginnings. Create TransformTrie(CompoundTransform).
    # Exemplar is a TransformTrie not a CompoundTransform

    def __init__(self, transforms):
        """
        Arguments:
          - transforms (list): A list of Transforms used to compute this 
          transform's outputs
        """
        super(CompoundTransform, self).__init__()
        
        self.transforms = transforms

    def transform(self, src_aux):
        """
        This is the pure function that doesn't modify self.aux
        """
        out_aux = {}
        for transform in self:
            aux = transform.transform(src_aux)  # compute auxiliary output
            out_aux.update(aux)
        return out_aux

    def __iter__(self):
        return iter(self.transforms)

    def __repr__(self):
        return "Compound({})".format(repr(self.transforms))


def _infer_types_from_defaults(optional_args):
    """
    Infers the types of all the optional args

    Returns:
      - a dict mapping every optional arg of f to a type such that its default
      value is an instance of that type, (checking with isinstance).
    """
    return {
        # if default is None we can't infer the type
        name: object if default is None else type(default)
        for name, default in optional_args.items()
    }

def _describe(f):
    """
    Parameters:
      - f: For example, f(src, name0, name1, name2=v2, name3=v3)

    Returns:
      - a dict mapping every positional argument of f to object, except the first.
      - a dict mapping every optional argument of f to its default value

    """
    argspec = inspect.getargspec(f)
    args = argspec.args[1:]  # Ignore the first argument (src)
    defaults = argspec.defaults or []

    optional_args = dict(zip(args[-len(defaults):], defaults))
    types = {
        name: object
        for name in args if name not in optional_args
    }
    return types, optional_args


def LambdaTransform(f, types=None, pure=False, name=None):
    """
    Creates a subclass of Transform using f to implement Transform.transform

    @param f (function): A function with signature f(src, name0, name1, name2=val2, name3=val3)

    The semantics of f are as follows:
      - the value of src is expected to be provided by the searcher,
        by passing them to Exemplar.__init__ in src.
      - the values of name0 and name1 are expected to be provided by the searcher,
        by passing them to Exemplar.__init__ in src_aux.
      - the values of name2 and name3 are fixed as val2 and val3

    @param types (dict): An optional dictionary to be used as Transform.aux_types
    for the keys name0, name1
    @param pure (bool): True if f is 'pure' in the sense that it produces no
    auxiliary data. That is, `f` returns `out` only, not `out, out_aux`
    """
    f_types, optional_args = _describe(f)

    _optional_types = _infer_types_from_defaults(optional_args)

    if types is not None:
        f_types.update(types)

    class Meta(type):
        def __repr__(cls): return (name or f.__name__).upper()

    class Lambda(Transform):
        __metaclass__ = Meta
        aux_types = f_types

        @staticmethod
        def transform(src_aux):
            src = src_aux[None]
            out_aux = {}
            if pure:
                out =  f(src, **{k:v for k,v in src_aux.items() if k is not None})
            else:
                out, out_aux = f(src, **{k:v for k,v in src_aux.items() if k is not None})
            out_aux[None] = out
            return out_aux

        def __repr__(self):
            return name or f.__name__

    return Lambda

def PureTransform(f, **kwargs):
    return LambdaTransform(f, pure=True, **kwargs)
