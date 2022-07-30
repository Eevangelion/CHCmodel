#!/usr/bin/env python3
### Model Validator
import sys
import os

from core import CliCmd, add_in_out_args, add_bool_argument
from horndb import HornClauseDb, HornRule, FolModel, load_horn_db_from_string
from solver_utils import pushed_solver
from time import time

import z3
import pysmt.solvers.z3 as pyz3

from pysmt.smtlib.parser import SmtLibZ3Parser, SmtLibCommand

import logging

log = logging.getLogger(__name__)


def define_fun_to_lambda(env, cmd):
    converter = pyz3.Z3Converter(env, z3.get_ctx(None))
    name, params, ret_sort, body = cmd.args
    zparams = [converter.convert(p) for p in params]
    zbody = converter.convert(body)
    res = z3.Lambda(zparams, zbody)
    return res


def load_model_from_file(fname):
    log.info('Loading model file {}'.format(fname))
    model = FolModel()
    with open(fname, 'r') as script:
        parser = SmtLibZ3Parser()
        for cmd in parser.get_command_generator(script):
            if type(cmd) == SmtLibCommand and cmd.name == 'define-fun':
                name = cmd.args[0]
                lmbd = define_fun_to_lambda(parser.env, cmd)
                model[name] = lmbd
    return model


def parse_file(fname):
    benchmark = ""
    flag = True
    with open(fname, 'r') as f_:
        for line in f_.readlines():
            if line == "(get-model)\n":
                flag = True
                continue
            if line == "(exit)\n":
                flag = True
            if flag:
                benchmark += line
            if line == "(check-sat)\n":
                flag = False
    return benchmark


class ModelValidator(object):
    def __init__(self, db, model):
        self._db = db
        self._model = model
        self._solver = z3.Solver(ctx=db.get_ctx())

    def _validate_rule(self, r):
        with pushed_solver(self._solver) as s:

            uninterp_sz = r.uninterp_size()
            for idx, term in enumerate(r.body()):
                if idx < uninterp_sz:
                    s.add(self._model.eval(term))
                else:
                    s.add(term)

            if not r.is_query():
                t = self._model.eval(r.head())
                s.add(z3.Not(t))
                
            res = s.check()
            if res == z3.unsat:
                pass
            else:
                #log.warning('Failed to validate a rule')
                #log.warning(r)
                if res == z3.sat:
                    print('Model is')
                    print(s.model())
                #else:
                    #log.warning('Incomplete solver')

            return res == z3.unsat

    def validate(self):
        res = True
        for i, r in enumerate(self._db.get_rules()):
            v = self._validate_rule(r)
            # print("Rule №", i + 1, ": ", r.head(), r.body(), sep='')
            print("Rule №", i + 1, ": ", r.head(), r.body(), " is ", "OK" if v else "NOT OK", sep='')
            res = res and v
            if res == False:
                return False
        for i, q in enumerate(self._db.get_queries()):
            v = self._validate_rule(q)
            # print("Query №", i + 1, ": ", q.head(), q.body(), sep='')
            print("Query №", i + 1, ": ", q.head(), q.body(), " is ", "OK" if v else "NOT OK", sep='')
            res = res and v
            if res == False:
                return False
        return res


class ChcModelCmd(CliCmd):
    def __init__(self):
        super().__init__('chcmodel', 'Model validator', allow_extra=False)

    def mk_arg_parser(self, ap):
        ap = super().mk_arg_parser(ap)
        ap.add_argument('-m', dest='model_file',
                         metavar='FILE', help='Model in SMT2 format', default='model.smt2')
        add_bool_argument(ap, "simplify-queries", dest='simple_q',
                          default=False, help='Automatically simplify queries')
        ap.add_argument('in_file',  metavar='FILE', help='Input file')
        return ap


    def run(self, args, extra=None):
        _benchmark = parse_file(args[0])
        db = load_horn_db_from_string(_benchmark,
                                    simplify_queries=False)
        model = load_model_from_file(args[0])
        validator = ModelValidator(db, model)
        res = validator.validate()
        return 0 if res else 1


if __name__ == '__main__':
    startTime = time()
    #logging.basicConfig(level=logging.INFO)
    cmd = ChcModelCmd()
    args = sys.argv[1:]
    res = cmd.main(args)
    print("Model is not correct!" if res else "Model is correct!")
    lastTime = time()
    print("Done in {0:.4f} s.".format(lastTime - startTime))
    sys.exit(res)
