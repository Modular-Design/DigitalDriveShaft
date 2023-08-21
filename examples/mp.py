from concurrent.futures import ProcessPoolExecutor
from time import sleep


def square(x):
    """Function to return the square of the argument"""
    if x == 3:
        sleep(2)
    return (x * x, x**3, x**4)


if __name__ == "__main__":
    r = [1, 2, 3, 4, 5]

    # create a pool of workers
    with ProcessPoolExecutor() as pool:
        result, _ = zip(*pool.map(square, r))

    print(list(result))
