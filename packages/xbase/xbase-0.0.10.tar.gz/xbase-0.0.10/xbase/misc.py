# 获取指定文件所在的目录
def xpath(file=__file__, relative_path=None):
    import os
    if relative_path is None:
        return os.path.split(os.path.realpath(file))[0]
    return os.path.join(os.path.split(os.path.realpath(file))[0], relative_path)
