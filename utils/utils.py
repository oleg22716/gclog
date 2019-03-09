def kb_formatter(kb):
    kb = int(kb)
    if kb < 1024:
        return kb.__str__() + "KB"
    elif kb < 1048576:
        return (kb/1024).__str__() + "MB"
    elif kb < 1073741824:
        return (kb / 1048576).__str__() + "GB"
    else:
        return (kb / 1073741824).__str__() + "TB"
