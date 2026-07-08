#這個檔案專門給.SQL close 不必再手動

import threading

_resources = set()
_lock = threading.Lock()

def register(resource):
    with _lock:
        _resources.add(resource)

def close_all():
    with _lock:
        resources = list(_resources)

    print("------------------ Closing Resources ------------------")
    for r in resources:
        try:
            r.close()
            print(r.__class__.__name__)
        except Exception:
            pass
    print("-------------------------------------------------------")
