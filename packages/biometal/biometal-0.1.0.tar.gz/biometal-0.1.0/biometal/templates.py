from atomium.structures.chains import Site
from atomium.structures.molecules import AtomicStructure

def create_site_template(site):
    if not isinstance(site, Site):
        raise TypeError("{} is not a binding site object".format(site))
    atoms = []
    for residue in site.residues():
        atoms.append(residue.atom(name="CA"))
        atoms.append(residue.atom(name="CB"))
    return AtomicStructure(*atoms)
