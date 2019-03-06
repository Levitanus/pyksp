import typing as ty
import mypy.plugin as mp
import mypy.types as mt


def check(arg: ty.Any) -> ty.NoReturn:
    raise Exception(arg)


def vars_callback(ctx: mp.FunctionContext) -> mt.Type:
    args = ctx.args[0][0].type  # type: ignore
    indicies: ty.List[int] = list()
    for idx, arg in enumerate(args.arg_types):
        if str(arg) in (
            'pyksp.service_types.LocInt',
            'pyksp.service_types.LocStr',
            'pyksp.service_types.LocFloat',
            'pyksp.service_types.LocArrInt',
            'pyksp.service_types.LocArrStr',
            'pyksp.service_types.LocArrFloat',
        ):
            indicies.append(idx)
    for idx in reversed(indicies):
        del args.arg_types[idx]
        del args.arg_kinds[idx]
        del args.arg_names[idx]
    return ctx.args[0][0].type  # type: ignore


def func_callback(ctx: mp.FunctionContext) -> mt.Type:
    args = ctx.args[0][0].type  # type: ignore
    indicies: ty.List[int] = list()
    types: ty.Dict[str,
                   ty.List[str]] = {
                       'pyksp.base_types.ArrInt':
                           ['pyksp.base_types.ArrInt'],
                       'pyksp.base_types.ArrStr':
                           ['pyksp.base_types.ArrStr'],
                       'pyksp.base_types.ArrFloat':
                           ['pyksp.base_types.ArrFloat'],
                       'pyksp.service_types.InInt':
                           [
                               'pyksp.base_types.ProcessInt',
                               'builtins.int'
                           ],
                       'pyksp.service_types.InStr':
                           [
                               'pyksp.base_types.ConcatsStrings',
                               'builtins.str'
                           ],
                       'pyksp.service_types.InFloat':
                           [
                               'pyksp.base_types.ProcessFloat',
                               'builtins.float'
                           ],
                       'pyksp.service_types.InArrInt':
                           ['pyksp.base_types.ArrInt'],
                       'pyksp.service_types.InArrStr':
                           ['pyksp.base_types.ArrStr'],
                       'pyksp.service_types.InArrFloat':
                           ['pyksp.base_types.ArrFloat'],
                       'pyksp.service_types.OutInt':
                           ['pyksp.base_types.VarInt'],
                       'pyksp.service_types.OutStr':
                           ['pyksp.base_types.VarStr'],
                       'pyksp.service_types.OutFloat':
                           ['pyksp.base_types.VarFloat'],
                       'pyksp.service_types.OutArrInt':
                           ['pyksp.base_types.ArrInt'],
                       'pyksp.service_types.OutArrStr':
                           ['pyksp.base_types.ArrStr'],
                       'pyksp.service_types.OutArrFloat':
                           ['pyksp.base_types.ArrFloat'],
                   }
    for idx, arg in enumerate(args.arg_types):
        if str(arg) in (
            'pyksp.service_types.LocInt',
            'pyksp.service_types.LocStr',
            'pyksp.service_types.LocFloat',
            'pyksp.service_types.LocArrInt',
            'pyksp.service_types.LocArrStr',
            'pyksp.service_types.LocArrFloat',
            'pyksp.base_types.VarInt',
            'pyksp.base_types.VarStr',
            'pyksp.base_types.VarFloat',
            'pyksp.base_types.ArrInt',
            'pyksp.base_types.ArrStr',
            'pyksp.base_types.ArrFloat',
        ):
            indicies.append(idx)
            continue
        if str(arg) in types:
            args.arg_types[idx] = mt.UnionType(
                [
                    ctx.api.named_type(i)  # type: ignore
                    for i in types[str(arg)]
                ]
            )
    for idx in reversed(indicies):
        del args.arg_types[idx]
        del args.arg_kinds[idx]
        del args.arg_names[idx]
    return ctx.args[0][0].type  # type: ignore


def LocCallback(ctx: mp.AnalyzeTypeContext, base: str) -> mt.Type:
    args = ctx.context.args  # type: ignore
    type_ = args[0]
    if len(args) == 2:
        # print(str(args[0]))
        if str(args[0]) == 'int?':
            type_ = ctx.api.named_type(
                'pyksp.service_types.%sArrInt' % base,
                []
            )
        if str(args[0]) == 'str?':
            type_ = ctx.api.named_type(
                'pyksp.service_types.%sArrStr' % base,
                []
            )
        if str(args[0]) == 'float?':
            type_ = ctx.api.named_type(
                'pyksp.service_types.%sArrFloat' % base,
                []
            )
    else:
        if str(args[0]) == 'int?':
            type_ = ctx.api.named_type(
                'pyksp.service_types.%sInt' % base,
                []
            )
        if str(args[0]) == 'str?':
            type_ = ctx.api.named_type(
                'pyksp.service_types.%sStr' % base,
                []
            )
        if str(args[0]) == 'float?':
            type_ = ctx.api.named_type(
                'pyksp.service_types.%sFloat' % base,
                []
            )
    return type_


def BaseCallback(ctx: mp.AnalyzeTypeContext, base: str) -> mt.Type:
    args = ctx.context.args  # type: ignore
    # print(str(args[0]))
    if len(args) > 1:
        base = 'Arr'
    if str(args[0]) == 'int?':
        return ctx.api.named_type('pyksp.base_types.%sInt' % base, [])
    if str(args[0]) == 'str?':
        return ctx.api.named_type('pyksp.base_types.%sStr' % base, [])
    if str(args[0]) == 'float?':
        return ctx.api.named_type('pyksp.base_types.%sFloat' % base, [])
    return ctx.api.named_type('pyksp.base_types.%s' % base, [])


def stack_push_callback(ctx: mp.MethodContext) -> mt.Type:
    ret_args: ty.List[mt.Type] = list()
    candidates: ty.Dict[str,
                        str] = {
                            'pyksp.service_types.LocInt':
                                'pyksp.base_types.VarInt',
                            'pyksp.service_types.LocStr':
                                'pyksp.base_types.VarStr',
                            'pyksp.service_types.LocFloat':
                                'pyksp.base_types.VarFloat',
                            'pyksp.service_types.LocArrInt':
                                'pyksp.base_types.ArrInt',
                            'pyksp.service_types.LocArrStr':
                                'pyksp.base_types.ArrStr',
                            'pyksp.service_types.LocArrFloat':
                                'pyksp.base_types.ArrFloat',
                            'builtins.int':
                                'pyksp.base_types.VarInt',
                            'builtins.str':
                                'pyksp.base_types.VarStr',
                            'builtins.float':
                                'pyksp.base_types.VarFloat',
                        }
    for arg in ctx.arg_types[0]:
        replaced = False
        for end_str, repl in zip(candidates, candidates.values()):
            if str(arg).endswith(end_str):
                ret_args.append(
                    ctx.api.named_type(repl)  # type: ignore
                )
                replaced = True
                break
        if not replaced:
            ret_args.append(arg)
    ctx.arg_types[0] = ret_args
    return mt.TupleType(  # type: ignore
        ret_args, ctx.default_return_type
    )


class KspPlugin(mp.Plugin):
    """Plugin"""

    def get_function_hook(
        self,
        fullname: str
    ) -> ty.Optional[ty.Callable[[mp.FunctionContext],
                                 mt.Type]]:
        if fullname == 'pyksp.service_types.vrs':
            return vars_callback
        if fullname == 'pyksp.functions.func':
            return func_callback
        return None

    def get_method_hook(self,
                        fullname: str
                        ) -> ty.Optional[ty.Callable[[mp.MethodContext],
                                                     mp.Type]]:
        if fullname == 'pyksp.stack.Stack.push':
            return stack_push_callback
        return None

    def get_type_analyze_hook(
        self,
        fullname: str
    ) -> ty.Optional[ty.Callable[[mp.AnalyzeTypeContext],
                                 mt.Type]]:
        if fullname == 'pyksp.service_types.Loc':
            return lambda ctx: LocCallback(ctx, 'Loc')
        if fullname == 'pyksp.service_types.In':
            return lambda ctx: LocCallback(ctx, 'In')
        if fullname == 'pyksp.service_types.Out':
            return lambda ctx: LocCallback(ctx, 'Out')
        if fullname == 'pyksp.base_types.Var':
            return lambda ctx: BaseCallback(ctx, 'Var')
        if fullname == 'pyksp.base_types.Arr':
            return lambda ctx: BaseCallback(ctx, 'Arr')
        return None


def plugin(version: str) -> ty.Type[KspPlugin]:
    return KspPlugin
