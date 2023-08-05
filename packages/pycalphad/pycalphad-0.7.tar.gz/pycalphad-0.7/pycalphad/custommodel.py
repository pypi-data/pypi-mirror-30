from pycalphad import Database, Model, equilibrium, eqplot, variables as v

# subclass of pycalphad's Model.
# This way we keep all of the functionality that we would expect.
# Energy contributions must return SymPy expressions, so we will import the necessary objects from SymPy
from sympy import exp, log, Abs, Add, Mul, Piecewise, Pow, S, sin, Symbol, zoo, oo
from pycalphad.core.constants import MIN_SITE_FRACTION

class MyCustomModel(Model):

    # We want to override the ideal mixing contribution
    # We can keep everything else the same
    # Below is the standard implementation of the ideal_mixing_energy
    # Change this to whatever you want, it just has to return some energy as SymPy expressions
    def ideal_mixing_energy(self, dbe):
        """
        Returns the ideal mixing energy in symbolic form.
        """
        phase = dbe.phases[self.phase_name]
        # Normalize site ratios
        site_ratio_normalization = self._site_ratio_normalization(phase)
        site_ratios = phase.sublattices
        site_ratios = [c / site_ratio_normalization for c in site_ratios]
        ideal_mixing_term = S.Zero
        for subl_index, sublattice in enumerate(phase.constituents):
            active_comps = set(sublattice).intersection(self.components)
            ratio = site_ratios[subl_index]
            for comp in active_comps:
                sitefrac = v.SiteFraction(phase.name, subl_index, comp)
                # We lose some precision here, but this makes the limit behave nicely
                # We're okay until fractions of about 1e-12 (platform-dependent)
                mixing_term = Piecewise((sitefrac * log(sitefrac), sitefrac > MIN_SITE_FRACTION / 10.), (0, True))
                ideal_mixing_term += (mixing_term * ratio)
        ideal_mixing_term *= (v.R * v.T)
        return ideal_mixing_term

# create your database from your TDB
dbf = Database('path/to/my/tdb')

# define components and phases
components = ['AL', 'NI', 'VA']
my_phases = ['LIQUID', 'FCC_A1', 'FCC_L12', 'BCC_A2', 'BCC_B2']  # ... and everything else

# instantiate the models
my_phase_models = {phase_name: MyCustomModel(dbf, components, phase_name) for phase_name in my_phases}

# calculate equilibrium with those models, e.g. for a binary phase diagram:
conditions = {v.P: 101325, v.T: (600, 2000, 10), v.X('AL'): (0, 1, 0.01)}
eq_result = equilibrium(dbf, components, my_phases, conditions, model=my_phase_models)

# finally, plot the phase diagram from the equilibrium result
import matplotlib.pyplot as plt
plt.figure()
eqplot(eq_result)
plt.show()
