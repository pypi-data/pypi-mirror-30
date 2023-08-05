from .error import *


# 获取指定文件所在的目录
def xpath(file=__file__, relative_path=None):
    import os
    if relative_path is None:
        return os.path.split(os.path.realpath(file))[0]
    return os.path.join(os.path.split(os.path.realpath(file))[0], relative_path)


# https://www.python.org/dev/peps/pep-0484/
# python的type hints用法，类似typescript的语法

# 查询配置信息(通过环境变量得到ACM的基本信息，一个应用的所有配置只能隶属于一个ACM命名空间中)
# 配置字段的命名规范：data_id.x1.x2
#   对应于 data_id的ACM配置内容，base下的配置信息，并且根据运行环境自动修改正确属性。
#   命名规范data_id不能含有分隔符.  在命名空间下增加配置数据全部以默认分组进行定义
#   在ACM上的配置信息全部使用yaml语法进行编辑配置管理
__config__: dict = None


def xconfig(path: str, default_value=None):
    import os
    import acm
    import yaml
    import dpath.util

    # 解析配置路径
    lst = path.split('.')
    xassert(len(lst) >= 2, path)
    data_id = lst[0]
    del lst[0]

    # TODO 性能优化在当前请求过程中保存一次静态全局变量避免重复的解析加载确保请求的动态性以及时效性
    global __config__
    if __config__ is None:
        # 获取ACM上的YAML配置文件内容并进行解析为PYTHON字典
        ENDPOINT = os.getenv('ALIYUN_ACM_ENDPOINT')
        NAMESPACE = os.getenv('ALIYUN_ACM_NAMESPACE')
        AK = os.getenv('ALIYUN_ACM_ACCESS_KEY_ID')
        SK = os.getenv('ALIYUN_ACM_ACCESS_KEY_SECRETE')
        client = acm.ACMClient(ENDPOINT, NAMESPACE, AK, SK)
        cfg = client.get(data_id, "DEFAULT_GROUP", timeout=5000, no_snapshot=True)
        xassert(cfg)
        cfg = yaml.load(cfg)
        xassert(cfg)
        __config__ = cfg

    # 根据环境配置约定base为基准，将env的内容进行覆盖处理，最终得到完整的配置信息
    base = __config__.get('base', None)
    xassert(base, path)
    ENV = os.getenv('ENV')
    xassert(ENV)
    env = __config__.get(ENV, None)
    if env is None:
        path = '/'.join(lst)
        try:
            return dpath.util.get(base, '/%s' % path)
        except KeyError:
            return default_value
    else:
        path = '/'.join(lst)

        try:
            value1 = dpath.util.get(base, '/%s' % path)
        except KeyError:
            # ignore error
            value1 = default_value
            pass

        try:
            value2 = dpath.util.get(env, '/%s' % path)
        except KeyError:
            # ignore error
            value2 = None
            pass

        if value2 is not None:
            # 进行merge处理
            dpath.util.merge(value1, value2, flags=dpath.MERGE_TYPESAFE)
            return value1
        else:
            return value1
