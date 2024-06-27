#!/usr/bin/env python3

import sys
from omada import Omada

def main():

    omada = Omada(verbose=True)
    omada.login()

    try:
        for vg in omada.getVoucherGroups():
            if len(sys.argv) > 1 and not any(arg in vg['name'] for arg in sys.argv):
                continue
            unused = omada.getUnusedVouchers(vg['id'], maxnr=10)
            codes = [v['code'] for v in unused]
            print(f"{vg['name']}: {', '.join(codes)}")

    finally:
        omada.logout()

if __name__ == '__main__':
    import warnings
    with warnings.catch_warnings(action="ignore"):
        main()
