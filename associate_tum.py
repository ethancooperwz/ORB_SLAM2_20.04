#!/usr/bin/env python3

import sys
import os

def read_file_list(filename):
    """ reads file with lines: timestamp path """
    lines = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            ts = float(parts[0])
            path = parts[1]
            lines.append((ts, path))
    return lines

def associate(rgb_list, depth_list, max_difference=0.02):
    """ For each rgb, find closest depth within max_difference """
    output = []
    depth_idx = 0
    nd = len(depth_list)

    for ts_rgb, rgb_path in rgb_list:
        # advance depth_idx until depth timestamp >= rgb timestamp - max_difference
        while depth_idx < nd and depth_list[depth_idx][0] < ts_rgb - max_difference:
            depth_idx += 1

        if depth_idx == nd:
            break

        # candidate 1: depth_idx
        best = None
        best_diff = float('inf')

        # check depth_idx
        ts_d, dp = depth_list[depth_idx]
        diff = abs(ts_rgb - ts_d)
        if diff < best_diff:
            best = (ts_d, dp)
            best_diff = diff

        # also check previous one
        if depth_idx > 0:
            ts_d2, dp2 = depth_list[depth_idx - 1]
            diff2 = abs(ts_rgb - ts_d2)
            if diff2 < best_diff:
                best = (ts_d2, dp2)
                best_diff = diff2

        # if best match is good enough, record it
        if best_diff <= max_difference:
            output.append((ts_rgb, rgb_path, best[0], best[1]))

    return output

def main():
    if len(sys.argv) != 4:
        print("Usage: associate_tum.py rgb.txt depth.txt associate.txt")
        return

    rgb_fn = sys.argv[1]
    depth_fn = sys.argv[2]
    out_fn = sys.argv[3]

    if not os.path.exists(rgb_fn):
        print("RGB file not found:", rgb_fn)
        return
    if not os.path.exists(depth_fn):
        print("Depth file not found:", depth_fn)
        return

    rgb_list = read_file_list(rgb_fn)
    depth_list = read_file_list(depth_fn)

    associations = associate(rgb_list, depth_list)

    with open(out_fn, 'w') as f:
        for ts_rgb, rgb_path, ts_d, dp in associations:
            f.write("{:.6f} {} {:.6f} {}\n".format(ts_rgb, rgb_path, ts_d, dp))

    print("Done. Wrote {} associations".format(len(associations)))

if __name__ == "__main__":
    main()
