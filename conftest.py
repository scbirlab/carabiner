import importlib.util
collect_ignore = []
if importlib.util.find_spec("tensorflow") is None:
    collect_ignore.append("carabiner/tf")
