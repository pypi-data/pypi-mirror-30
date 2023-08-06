import numpy as np
from gameanalysis import rsgame

from egta import profsched


class NormScheduler(profsched.Scheduler):
    """A scheduler that removes single strategy roles

    Parameters
    ----------
    sched : Scheduler
        The base scheduler that generates payoffs.
    """

    def __init__(self, sched):
        self._sched = sched
        role_mask = sched.game().num_role_strats > 1
        self._game = rsgame.emptygame_names(
            [r for r, m in zip(sched.game().role_names, role_mask) if m],
            sched.game().num_role_players[role_mask],
            [s for s, m in zip(sched.game().strat_names, role_mask) if m])
        self._players = sched.game().num_role_players[~role_mask]
        self._inds = np.cumsum(
            role_mask * sched.game().num_role_strats)[~role_mask]
        self._mask = role_mask.repeat(sched.game().num_role_strats)

    def schedule(self, profile):
        full_prof = np.insert(profile, self._inds, self._players)
        return _NormPromise(self._mask, self._sched.schedule(full_prof))

    def game(self):
        return self._game

    def __enter__(self):
        self._sched.__enter__()
        return self

    def __exit__(self, *args):
        return self._sched.__exit__(*args)


class _NormPromise(profsched.Promise):
    def __init__(self, mask, prom):
        self._mask = mask
        self._prom = prom

    def get(self):
        return self._prom.get()[self._mask]
