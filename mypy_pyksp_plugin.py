import typing as ty
import mypy.plugin as mp
import mypy.types as mt

# import pyksp.base_types as bt


def check(arg: ty.Any) -> ty.NoReturn:
    raise Exception(arg)


def vars_callback(ctx: mp.FunctionContext) -> mt.Type:  # type: ignore
    print('vars_callback')
    # print(ctx.arg_types)
    # print(ctx.arg_kinds)
    # print(ctx.callee_arg_names)
    # print(ctx.arg_names)
    # print(ctx.default_return_type)
    # print(ctx.args)
    # print(ctx.context)
    # print(ctx.api)
    # print('\n')
    # return ty.Callable[[int], None]


def LocCallback(ctx: mp.AnalyzeTypeContext) -> mt.Type:
    print('LocCallback')
    print(ctx.type)
    print('context')
    print(dir(ctx.context))
    print(ctx.context)
    print(ctx.context.args)  # type: ignore
    print('args')
    arg = ctx.context.args[0]  # type: ignore
    print(dir(arg))
    print(arg.name)
    for arg in ctx.context.args:  # type: ignore
        print(arg)
    print(ctx.api)
    print('\n')
    return ctx.api.named_type('pyksp.base_types.ArrInt', [])
    # return mt.AnyType(0)


class KspPlugin(mp.Plugin):
    def get_function_hook(
            self, fullname: str
    ) -> ty.Optional[ty.Callable[[mp.FunctionContext], mt.Type]]:
        # print(fullname)
        if fullname == 'pyksp.simple_test.vrs':
            print('vrs')
            return vars_callback
        if fullname.startswith('pyksp.simple_test.LocMeta'):
            print('---------LOCMETA------------')
        return None

    def get_method_signature_hook(
            self, fullname: str
    ) -> ty.Optional[ty.Callable[[mp.MethodSigContext], mt.CallableType]]:
        # print(fullname)
        if fullname == 'pyksp.simple_test.vrs':
            print('vrs')
            return vars_callback  # type: ignore
        if fullname.startswith('pyksp.simple_test.LocMeta'):
            print('---------LOCMETA------------')
        return None

    def get_type_analyze_hook(
            self, fullname: str
    ) -> ty.Optional[ty.Callable[[mp.AnalyzeTypeContext], mt.Type]]:
        # print(fullname)
        if fullname == 'pyksp.simple_test.Loc':
            return LocCallback
        return None


def plugin(version: str) -> ty.Type[KspPlugin]:
    return KspPlugin
