#!/usr/bin/env python3

import sys
from omada import Omada

def main():

    omada = Omada(verbose=True)
    omada.login()

    try:
        for vg in omada.getVoucherGroups():
            if len(sys.argv) > 1 and not any(arg in vg['name'] for arg in sys.argv[1:]):
                # if arguments are provided, limit the voucher groups searched
                # to those whose names match one of the command line
                # arguments. I.e. if there are arguments and none ("not any")
                # match, then skip this group:
                continue
            unused = omada.getUnusedVouchers(vg['id'], maxnr=10)
            if not unused:
                # no vouchers left in this group, skip it
                continue
            codes = [v['code'] for v in unused]
            print(f"{vg['name']}: {', '.join(codes)}")

    finally:
        omada.logout()

if __name__ == '__main__':
    import warnings
    with warnings.catch_warnings(action="ignore"):
        main()
