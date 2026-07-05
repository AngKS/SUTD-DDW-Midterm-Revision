import random


def gen_random_int(num_items: int, seed: int, max_num) -> list[int]:
    random.seed(seed)
    nums = []
    for i in range(num_items):
        nums.append(random.randint(0, max_num))
    random.shuffle(nums)
    return nums


def create_string(array: list[int]) -> str:
    return ", ".join(str(x) for x in array) + "."
