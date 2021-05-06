from sde_mc.options import *
from sde_mc.sde import Gbm, SdeSolver, Sde, Heston
from sde_mc.mc import mc_simple, mc_control_variate
from sde_mc.regression import *
from sde_mc.vreduction import SdeControlVariate
from sde_mc.approximators import GbmLinear, Mlp, NetApproximator
import torch
import numpy as np
import time
import matplotlib.pyplot as plt
from functools import partial
from abc import ABC, abstractmethod


steps = 600
trials = 100

gbm = Gbm(mu=0.02, sigma=0.2, init_value=torch.tensor([1.0]), dim=1)
solver = SdeSolver(sde=gbm, time=3, num_steps=steps)

mc_stats = mc_simple(num_trials=trials, sde_solver=solver, payoff=BinaryAoN(strike=1.), discount=np.exp(-0.06))
mc_stats.print()
paths = mc_stats.paths
payoffs = mc_stats.payoffs
print(paths)

ts = torch.tensor([t * 3 / steps for t in range(1, steps + 1)])
print(ts)
net_approx = NetApproximator(time_points=ts, layer_sizes=[10, 10])
net_approx.fit(paths, payoffs)

x = torch.linspace(0.5, 2, 100).unsqueeze(-1)
t = torch.tensor(2.)
# t = t.unsqueeze(-1).repeat(x.shape[0]).unsqueeze(-1)
# inputs = torch.cat([t, x], dim=1)
# print(inputs)
outputs = net_approx(0, t, x)
plt.plot(x, outputs.detach())
plt.show()

#
#
# idx = 1
# t = idx*3/steps
# basis = [partial(basis_1, t=t), partial(basis_2, t=t), partial(basis_3, t=t)]
# print(payoffs)
# print(paths[:, idx].squeeze(-1))
# print(fit_basis(paths[:, 1].squeeze(-1), payoffs, basis))


# # Heston example:
# x0 = torch.tensor([np.log(1), np.log(0.2**2)])
# heston = Heston(r=0.02, kappa=0.2, theta=0.2**2, xi=0.1, rho=-0.2, init_value=x0)
# solver = SdeSolver(sde=heston, time=3, num_steps=1000)
# mc_stats = mc_simple(10000, sde_solver=solver, payoff=EuroCall(1., log=True), discount=np.exp(-0.06))
# mc_stats.print()


# # Example which shows control variates 3-4x faster
# steps = 3000
# trials = 70000
#
# gbm = Gbm(mu=0.02, sigma=0.2, init_value=torch.tensor([1.0]), dim=1)
# solver = SdeSolver(sde=gbm, time=3, num_steps=steps)
# paths = solver.euler(2)
#
# mc_stats = mc_simple(num_trials=trials, sde_solver=solver, payoff=BinaryAoN(strike=1.), discount=np.exp(-0.06))
# mc_stats.print()
#
# steps = 600
# ts = torch.tensor([3*i / steps for i in range(1, steps+1)])
# gbm = Gbm(mu=0.02, sigma=0.2, init_value=torch.tensor([1.0]), dim=1)
# solver = SdeSolver(sde=gbm, time=3, num_steps=steps)
# gbm_approx = GbmLinear(basis=[basis_1, basis_2, basis_3], time_points=ts, mu=gbm.mu, sigma=gbm.sigma)
# new_cv_stats = mc_control_variate(num_trials=(500, 5000), simple_solver=solver, approximator=gbm_approx,
#                                   payoff=BinaryAoN(strike=1.), discount=np.exp(-0.06))
# new_cv_stats.print()
