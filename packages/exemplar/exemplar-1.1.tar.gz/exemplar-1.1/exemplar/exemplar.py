import pycosat
from transforms import Transform, TransformChain, TransformMap, CompoundTransform, Ident
from pprint import pprint
from itertools import groupby

class NoSuchTransformException(Exception):
    def __init__(self, exemplar):
        self.message = "No such {} found.".format(exemplar.__class__.__name__)


class BadExampleException(Exception):
    """ For example, duplicate values in an Exemplar's self.src_aux """


class Exemplar(CompoundTransform):
    """
    A Transform defined by example, not procedure.
    """
    candidates = []

    def __init__(self, src, trg, src_aux=None, trg_aux=None):
        self.src_aux = src_aux or {}
        self.trg_aux = trg_aux or {}
        self.src_aux[None] = src
        self.trg_aux[None] = trg

        self.validate_example()

        transforms = self.search()

        super(Exemplar, self).__init__(transforms)

    def validate_example(self):
        if len(self.src_aux) != len(list(groupby(self.src_aux.values()))):
            raise BadExampleException('Multiple sources found with identical examples')

    @staticmethod
    def satisfied(transform, src_aux):
        """
        Generates tuples with 3 elements:
        1. satisfying_transform
        2. out_aux (result of running the transform on src_aux)
        """
        transform.aux_types[None] = object

        if len(transform.aux_types) == 1:
            # Type-satisfied by trivial aux_map.
            try:
                out_aux = transform.transform(src_aux)
                yield transform, out_aux  # Yay! that was easy
            except BaseException:
                pass  # There's no solution
            return

        # transform key --> list of possible src_aux keys
        transform_possibilities = {}

        for transform_key, t in transform.aux_types.items():
            possible_src_keys = [
                k for k, v in src_aux.items() if isinstance(v,t)
            ]
            if not possible_src_keys:
                return  # no mapping of self.src_aux can satisfy transform
            transform_possibilities[transform_key] = possible_src_keys

        # 1. Create CNF variables
        pairs = []  # every possible t -> s pair.
        for t_key, possible_src_keys in transform_possibilities.items():
            for src_key in possible_src_keys:
                pairs.append((t_key, src_key))
        # 0 cannot be a variable name because 0 = -0
        var2pair = dict(enumerate(pairs, start=1))
        pair2var = {pair: var for var, pair in var2pair.items()}

        # 2. Write CNF clauses
        # Rule A: At least 1 src_key per transform_key
        cnf = map(
            lambda t_key_possible_src_keys: map(
                lambda src_key: pair2var[(t_key_possible_src_keys[0], src_key)],
                t_key_possible_src_keys[1]),
            transform_possibilities.items())

        # Rule B: No 2 src_keys with the same transform_key
        for t_key, possible_src_keys in transform_possibilities.items():
            for src_key_1, src_key_2 in zip(
                    possible_src_keys, possible_src_keys[1:]):
                cnf.append([-pair2var[(t_key, src_key_1)], -
                            pair2var[(t_key, src_key_2)]])

        # 3. Iteratively find and yield possible solutions
        for solution in pycosat.itersolve(cnf):
            aux_map = dict( var2pair[var] for var in solution if var > 0 )

            satisfying_transform = TransformChain(TransformMap(aux_map), transform)

            # Try running transform on src_aux
            try:
                out_aux = satisfying_transform.transform(src_aux)
                yield satisfying_transform, out_aux
            except BaseException:
                continue  # discard this solution.

    @staticmethod
    def filter_candidates(candidates, src_aux):
        for f in candidates:
            for satisfying_transform, out_aux in Exemplar.satisfied(f, src_aux):
                yield satisfying_transform, out_aux

    @staticmethod
    def best_map(out_aux, trg_aux):
        aux_map = {}  # trg key --> out key
        for trg_k, trg_v in trg_aux.items():
            for out_k, out_v in out_aux.items():
                if trg_v == out_v:
                    if trg_k not in aux_map or trg_k == out_k:
                        aux_map[trg_k] = out_k
        return aux_map

    @staticmethod
    def score_map(aux_map):
        return (
            int(None in aux_map), # f computes self.trg_aux[None]
            len(aux_map), # f computes values in trg_aux
            sum(trg_k == out_k for trg_k, out_k in aux_map.items())
        )

    def expand_search(self, src_aux, targets):
        """
        Parameters
        ----------
        src_aux (dict): Search sources.
        targets (set) : Keys of the remaining search targets in self.trg_aux

        Returns
        -------
        Transform
            - A Transform that can run on src_aux to compute some of the targets
        list
            - A list of 2-element tuples: 
                1. A Transform that can run on src_aux
                2. The `out_aux` dictionary it produces.
        set
            - Keys of the remaining search targets in self.trg_aux
        """


        trg_aux = { k:v for k,v in self.trg_aux.items() if k in targets }

        """
        ----------------
        Search Algorithm
        ----------------

        ** Step 1 **
        Find candidates. Candidates are tuples with 2 elements:
            1. A transform that can run on src_aux
            2. The out_aux that results from running the transform on src_aux
        """
        candidates = list(self.filter_candidates(self.candidates, src_aux))
        # Fail early if no candidates can even run on self.src_aux:
        if not candidates: raise NoSuchTransformException(self)

        """
        ** Step 2 **
        Sort the candidates according to the number of self.trg_aux values they
        compute, and greedily select candidates.
        """

        candidates = map(
            lambda (transform, out_aux):(transform,
                out_aux,
                self.best_map(out_aux, trg_aux))
            , candidates)

        # Rank functions, best first
        transforms = sorted(
            candidates,
            key=lambda (_, __, aux_map):self.score_map(aux_map),
            reverse=True
            )
        # transforms looks like [(satisfying_transform, out_aux, trg2out_aux_map), ...]

        seen_keys = set()
        for _, out_aux, trg2out_aux_map in transforms:
            for key in seen_keys:
                # Deduplicate: No two transform should compute the same trg aux value
                trg2out_aux_map.pop(key, None)
            seen_keys = seen_keys | set(trg2out_aux_map)
        
        """
        ** Step 3 **
        - Create the Compound transform we have so far. (Leaf node)
        - Return the intermediate transforms and the values they compute
        - Return the reamining set of uncomputed targets
        """
        # functions that were selected to compute trg_aux values
        final_transforms = filter(lambda x: x[-1], transforms)
        final_transforms = map(lambda (transform, _, trg2out_aux_map):
            TransformChain(transform, TransformMap(trg2out_aux_map)),
            final_transforms
            )

        if final_transforms:
            if len(final_transforms) == 1:
                transform = final_transforms[0]
            else:            
                transform = CompoundTransform(final_transforms)
        else:
            transform = Ident

        # Assert that all trg_aux values can be computed:
        if len(seen_keys) == len(trg_aux):
            return transform, [], seen_keys

        # transforms whose out_aux might be a step towards computing trg_aux
        intermediate_transforms = map(
            lambda (transform, out_aux, _):(transform, out_aux),
            transforms
            )

        return transform, intermediate_transforms, seen_keys

    def search(self, max_depth=3):
        sources = [ (TransformChain(), self.src_aux) ]
        targets = set(self.trg_aux)
        transforms = []
        step = 0

        # print 'Searching...', self.src_aux, '->', self.trg_aux

        while sources and targets:
            step += 1
            # print '\n** STEP {} ***'.format(step)

            chain, src_aux = sources.pop(0)

            if len(chain) >= max_depth:
                continue

            try:
                transform, int_transforms, keys_found = self.expand_search(
                    src_aux=src_aux,
                    targets=targets
                )
            except NoSuchTransformException:
                continue
            
            if keys_found:
                transforms.append( chain.append(transform) )

            for transform, intermediate_aux in int_transforms:
                if transform is not Ident: 
                    # Note that chain.append is NOT a mutator.
                    sources.append( (chain.append(transform), intermediate_aux) )
                    # maybe if keys_found we should sources.prepend instead

            targets -= keys_found

        print "\nSearch concluded in {} steps:".format(step)

        if targets:
            raise NoSuchTransformException(self)

        pprint(transforms)
        return transforms