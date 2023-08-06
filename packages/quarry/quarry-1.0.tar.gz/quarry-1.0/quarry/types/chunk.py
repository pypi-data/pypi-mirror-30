from collections import Sequence
import math


try:
    xrange
except NameError:
    xrange = range


class _Array(Sequence):
    def __len__(self):
        return 4096


class BlockArray(_Array):
    def __init__(self, data, bits, palette=None):
        self.data = data
        self.bits = bits
        self.palette = palette

    @classmethod
    def empty(cls):
        return cls([0] * 256, 4, [0])

    def is_empty(self):
        if self.palette is not None:
            return self.palette == [0]
        else:
            return not any(self.data)

    def __getitem__(self, n):
        if isinstance(n, slice):
            return [self[o] for o in xrange(*n.indices(4096))]

        idx0 = (self.bits * n) // 64
        idx1 = (self.bits * (n + 1) - 1) // 64

        off0 = (self.bits * n) % 64
        off1 = 64 - off0

        if idx0 == idx1:
            val = self.data[idx0] >> off0
        else:
            val = (self.data[idx0] >> off0) | (self.data[idx1] << off1)

        val &= (1 << self.bits) - 1

        if self.palette is not None:
            val = self.palette[val]

        return int(val)

    def __setitem__(self, n, val):
        if isinstance(n, slice):
            for o in xrange(*n.indices(4096)):
                self[o] = val[o]
            return

        if self.palette is not None:
            try:
                val = self.palette.index(val)
            except ValueError:
                self.repack(reserve=1)

                if self.palette is not None:
                    self.palette.append(val)
                    val = len(self.palette) - 1

        idx0 = (self.bits * n) // 64
        idx1 = (self.bits * (n + 1) - 1) // 64

        off0 = (self.bits * n) % 64
        off1 = 64 - off0

        mask0 = ((1 << self.bits) - 1) << off0
        mask1 = ((1 << self.bits) - 1) >> off1

        self.data[idx0] &= (2 ** 64 - 1) & ~mask0
        self.data[idx0] |= (2 ** 64 - 1) & mask0 & (val << off0)

        if idx0 != idx1:
            self.data[idx1] &= ~mask1
            self.data[idx1] |= mask1 & (val >> off1)

    def repack(self, reserve=None):
        if reserve is None:
            # Recompute the palette by walking all blocks
            palette = list(set(self))
            palette_len = len(palette)
        else:
            if self.palette is None:
                # Reserving space in an unpaletted array is a no-op.
                return

            palette = self.palette
            palette_len = len(palette) + reserve

        # Compute new bits
        bits = int(math.ceil(math.log(palette_len, 2)))
        if bits <= 8:
            if bits < 4:
                bits = 4
        else:
            bits = 13
            palette = None

        if self.bits == bits:
            # Nothing to do.
            return

        # Save contents
        values = self[:]

        # Update internals
        self.data[:] = [0] * (64 * bits)
        self.bits = bits
        self.palette = palette

        # Load contents
        self[:] = values


class LightArray(_Array):
    def __init__(self, data):
        self.data = data

    @classmethod
    def empty(cls):
        return cls([0] * 2048)

    def __getitem__(self, n):
        if isinstance(n, slice):
            return [self[o] for o in xrange(*n.indices(4096))]
        assert isinstance(n, int)
        idx, off = divmod(n, 2)
        if off == 0:
            return self.data[idx] & 0x0F
        else:
            return self.data[idx] >> 4

    def __setitem__(self, n, val):
        assert isinstance(n, int)
        idx, off = divmod(n, 2)
        if off == 0:
            self.data[idx] = (self.data[idx] & 0xF0) | val
        else:
            self.data[idx] = (self.data[idx] & 0x0F) | (val << 4)
