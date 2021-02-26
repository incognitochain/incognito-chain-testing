# breakpoint()
var = None


def setup_module():
    print("setup")
    global var
    var = 100
    print(f'setup var = {var}')
