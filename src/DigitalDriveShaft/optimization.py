
def x_squared(x):
    return x*x


def x_linear(x):
    return x


def find_optimum(func, x=4):
    return func(x)


if __name__ == "__main__":
    def x_3times(x):
        return 3*x

    print(find_optimum(x_squared))  # callables
    print(find_optimum(x_linear))
    print(find_optimum(x_3times, 5))
    print(find_optimum(lambda x: x+10))  # lambda expression
