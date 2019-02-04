import typing as ty
import mypy.plugin as mp
import mypy.types as mt


def check(arg: ty.Any) -> ty.NoReturn:
    raise Exception(arg)


def vars_callback(ctx: mp.FunctionContext) -> mt.Type:
    args = ctx.args[0][0].type  # type: ignore
    for idx, arg in enumerate(args.arg_types):
        if str(arg) in (
                'pyksp.service_types.LocInt',
                'pyksp.service_types.LocStr',
                'pyksp.service_types.LocFloat',
                'pyksp.service_types.LocArrInt',
                'pyksp.service_types.LocArrStr',
                'pyksp.service_types.LocArrFloat',
        ):
            del args.arg_types[idx]
            del args.arg_kinds[idx]
            del args.arg_names[idx]
    return ctx.args[0][0].type  # type: ignore


def LocCallback(ctx: mp.AnalyzeTypeContext) -> mt.Type:
    args = ctx.context.args  # type: ignore
    if len(args) == 2:
        # print(str(args[0]))
        if str(args[0]) == 'int?':
            return ctx.api.named_type('pyksp.service_types.LocArrInt', [])
        if str(args[0]) == 'str?':
            return ctx.api.named_type('pyksp.service_types.LocArrStr', [])
        if str(args[0]) == 'float?':
            return ctx.api.named_type('pyksp.service_types.LocArrFloat', [])
    elif len(args) == 1:
        if str(args[0]) == 'int?':
            return ctx.api.named_type('pyksp.service_types.LocInt', [])
        if str(args[0]) == 'str?':
            return ctx.api.named_type('pyksp.service_types.LocStr', [])
        if str(args[0]) == 'float?':
            return ctx.api.named_type('pyksp.service_types.LocFloat', [])
    return ctx.api.named_type('pyksp.service_types.Loc', [])


class KspPlugin(mp.Plugin):
    """Plugin"""

    def get_function_hook(
            self, fullname: str
    ) -> ty.Optional[ty.Callable[[mp.FunctionContext], mt.Type]]:
        # print(fullname)
        if fullname == 'pyksp.simple_test.vrs':
            # print('vrs')
            return vars_callback
        return None

    def get_type_analyze_hook(
            self, fullname: str
    ) -> ty.Optional[ty.Callable[[mp.AnalyzeTypeContext], mt.Type]]:
        # print(fullname)
        if fullname == 'pyksp.service_types.Loc':
            return LocCallback
        return None


def plugin(version: str) -> ty.Type[KspPlugin]:
    return KspPlugin
