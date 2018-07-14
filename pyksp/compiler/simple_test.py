FrameVar = 1
kLocal = 1
KSP = 1


def _append_frame_item(self, name, item, frame, count):
    idx = self.idx_arr[self.idx_curr] + count
    if isinstance(item, kLocal):
        var = FrameVar(
            name,
            self.arr,
            length=item.len,
            start_idx=idx)
        frame.append(name, var)
        return count + item.len

    if KSP.is_under_test():
        var = FrameVar(name, item)
        frame.append(name, var)
        return count + var.len

    try:
        length = len(item)
        var = FrameVar(
            name,
            self.arr,
            length=length,
            start_idx=idx)
        frame.append(name, var)
        return count + length
    except TypeError:
        self.arr[idx] = item
        var = FrameVar(name, self.arr[idx], length=1)
        frame.append(name, var)
        return count + 1
