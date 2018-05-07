from hypothesis.strategies import integers


uint8s = integers(0, 2 ** 8 - 1)

int32s = integers(-2 ** 15, 2 ** 15 - 1)
