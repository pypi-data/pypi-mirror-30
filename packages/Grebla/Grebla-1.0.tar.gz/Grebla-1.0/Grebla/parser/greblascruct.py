

class GreblaStruct:
    run_list = []

    def __setitem__(self, key, value):
        run_list = getattr(GreblaStruct, "run_list")
        run_list.append({
            key: value
        })
        setattr(GreblaStruct, "run_list", run_list)
