#!/usr/bin/env python

from abipy import abilab
import sys

ncfile = abilab.abiopen(sys.argv[1])
#print(ncfile)

#data = ncfile.get_dataframe()
#print(data)

r = ncfile.reader

qp = r.read_qp(spin=0, sigma_kpoint=1, band=0)
print(qp)
#qp.plot()

qplist = r.read_qplist_sk(spin=0, sigma_kpoint=0)
print(qplist)
#qplist.plot_vs_e0()
ncfile.plot_qps_vs_e0()

sigma = r.read_sigma_eph(spin=0, sigma_kpoint=0, band=3)
print(sigma)
#sigma.plot_tdep()
