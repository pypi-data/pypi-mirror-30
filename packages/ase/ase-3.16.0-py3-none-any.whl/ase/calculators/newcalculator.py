from ase.calculators.calculator import compare_atoms
from ase.calculators.emt import EMT


# Steps:
#   1) have atoms, kwargs  ~  enough to generate input
#   2) generate input / initialize, but do not do anything expensive
#   3) do anything expensive, get results

class CalculatorInputs:
    def __init__(self, atoms, **kwargs):
        self.atoms = atoms
        self.kwargs = kwargs

    def get_calculator(self, atoms):
        return self.cls(atoms, self.kwargs)

    def calculate(self, atoms):
        pass


class Engine:
    #caching = True  # Whether to cache atoms/results for this engine.

    def initialize(self, atoms):
        pass

    def validate(self, cache, changes, **kwargs):
        """Validate cache in face of changes."""
        return None


class VeryBasicCalculator:
    def __init__(self, enginecls, **kwargs):
        self.enginecls = enginecls

    def calculate(self, quantities):
        pass

class NewCalculator:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

        self.engine = ...
        self.enginecls = enginecls
        self.kwargs = kwargs

        self._previous_kwargs = None
        self._previous_atoms = None

        self.atoms = None
        self.engine = None
        self.outputs = {}

    #def set(self, **kwargs):
    #    self._previous_kwargs = self.kwargs
    #    self.kwargs = kwargs

    def set(self, atoms=None, **kwargs):
        if self.outputs:
            pass

        self.atoms = atoms
        self.kwargs = kwargs
        if atoms is not None:
            changes = compare_atoms(self.atoms, atoms1)
            self.atoms = atoms.copy()
        self._changes = changes

        #if kwargs:
        #    self.engine.validate(

        #if self.cache is not None:
        #    self.cache = self.engine.validate(changes)
        

    def calculate(self, quantities):
        #self._cached_kwargs = self.kwargs.copy()
        #self._cached_atoms = self.atoms.copy()
        # Check for changes, invalid

        if self.engine is None:
            self.engine = self.engineclass(self.atoms, self.kwargs)

        self.cache.update(self.engine.calculate(quantities))

    def get_property(self, name):
        if self.cache is None:
            self.cache = self.calculate([name])
        #elif 
        
        if name in self.cache:
            return self

    def get_potential_energy(self):
        if self.cache is None:
            self.calculate('energy')
        return self.cache.get('energy')



def main():
    from ase.build import molecule
    atoms = molecule('H2O')
    calc = NewMorse(rho0=0)
    atoms.calc = calc
    e = atoms.get_potential_energy()
    f = atoms.get_forces()
    print(e, f.tolist())

if __name__ == '__main__':
    main()
