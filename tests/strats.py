from hypothesis.strategies import floats, integers

uint8s = integers(0, 2**8 - 1)
uint16s = integers(0, 2**16 - 1)
uint32s = integers(0, 2**32 - 1)
uint64s = integers(0, 2**64 - 1)

int8s = integers(-(2**7), (2**7) - 1)
int16s = integers(-(2**15), (2**15) - 1)
int32s = integers(-(2**31), (2**31) - 1)
int64s = integers(-(2**63), (2**63) - 1)

float64s = floats(allow_nan=False)


# width=32 keeps draws inside float32 range; packing an unbounded float64
# into "f" overflows.
float32s = floats(allow_nan=False, width=32)
