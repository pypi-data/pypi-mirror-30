"""Contains functions for examining hydrophobicity."""

from atomium.structures import Model, Atom
from .charges import partial_charges

def solvation(model, x, y, z, radius, pc=False, het=True, metal=True):
    """Determines the average solvation within a given sphere of an atomium
    model. By default, all atoms within the radius will be considered, but you
    can opt to exlcude heteroatoms (atoms not part of a chain residue) if you so
    desire.

    :param Model model: The atomium model to examine.
    :param x: The x-coordinate of the centre of the sphere.
    :param y: The y-coordinate of the centre of the sphere.
    :param z: The z-coordinate of the centre of the sphere.
    :param radius: The radius of the sphere.
    :param bool pc: If ``True``, atomic partial charges will be used instead of\
    atomic solvation parameters (squared).
    :param bool het: If ``False``, only atoms that have a residue will be\
    considered.
    :param bool metal: If ``False``, only non-metal atoms will be considered.
    :raises TypeError: if the model is not an atomium model object.
    :raises TypeError: if the coordinates are not numeric.
    :raises TypeError: if the radius is not numeric.
    :raises ValueError: if the radius is negative.
    :rtype: ``float``"""

    if not isinstance(model, Model):
        raise TypeError("{} is not a Model".format(model))
    if any(not isinstance(c, (int, float)) for c in (x, y, z)):
        raise TypeError("({}, {}, {}) not valid coordinate".format(x, y, z))
    if not isinstance(radius, (int, float)):
        raise TypeError("{} is not a valid radius".format(radius))
    if radius < 0:
        raise ValueError("{} is not a valid radius".format(radius))

    sphere = model.atoms_in_sphere(x, y, z, radius, het=het, metal=metal)
    solvations = ([atom_partial_charge(atom) ** 2 for atom in sphere]
     if pc else [atom_solvation(atom) for atom in sphere])
    return sum(solvations) / len(sphere) if len(solvations) else 0


def atom_solvation(atom):
    """Returns the atomic solvation parameter of an atomium atom. The atomic
    solvation parameters are taken from Yamashita et al (1990).

    :param Atom atom: an atomium atom object.
    :rtype: ``float``"""

    specials = {
     "O": {"GLU": ["OE1", "OE2"], "ASP": ["OD1", "OD2"]},
     "N": {"HIS": ["ND1", "NE2"], "ARG": ["NH1", "NH2"]}
    }
    if atom.element == "C": return 18
    if atom.element == "S": return -5
    if atom.element in specials:
        if atom.charge != 0:
            return -37 if atom.element == "O" else -38
        if atom.residue and atom.residue.name in specials[atom.element]:
            if atom.name in specials[atom.element][atom.residue.name]:
                return -23 if atom.element == "O" else -23.5
        return -9
    return 0


def atom_partial_charge(atom):
    """Returns the atomic partial charge of an atomium atom.

    :param Atom atom: an atomium atom object.
    :rtype: ``float``"""

    if atom.charge != 0: return atom.charge
    if atom.residue is not None and atom.residue.name in partial_charges:
        if atom.name in partial_charges[atom.residue.name]:
            return partial_charges[atom.residue.name][atom.name]
    return 0


def hydrophobic_contrast(model, x, y, z, radius, pc=False, het=True, metal=True):
    """Determines the hydrophobic contrast within a sphere - a measure of
    how heterogenous the hydrophobicity is within the sphere.

    A homogeneous sphere will evaluate to zero, a sphere with a region of high
    hydrophilic atoms enclosed within a region of high hydrophobic regions will
    have a high positive value, and the converse will have a high negative
    value.

    :param Model model: The atomium model to examine.
    :param x: The x-coordinate of the centre of the sphere.
    :param y: The y-coordinate of the centre of the sphere.
    :param z: The z-coordinate of the centre of the sphere.
    :param radius: The radius of the sphere.
    :param bool het: If ``False``, only atoms that have a residue will be\
    considered.
    :param bool metal: If ``False``, only non-metal atoms will be considered.
    :raises TypeError: if the model is not an atomium model object.
    :raises TypeError: if the coordinates are not numeric.
    :raises TypeError: if the radius is not numeric.
    :raises ValueError: if the radius is negative.
    :rtype: ``float``"""

    if not isinstance(model, Model):
        raise TypeError("{} is not a Model".format(model))
    if any(not isinstance(c, (int, float)) for c in (x, y, z)):
        raise TypeError("({}, {}, {}) not valid coordinate".format(x, y, z))
    if not isinstance(radius, (int, float)):
        raise TypeError("{} is not a valid radius".format(radius))
    if radius < 0:
        raise ValueError("{} is not a valid radius".format(radius))
    sphere = model.atoms_in_sphere(x, y, z, radius, het=het, metal=metal)
    if len(sphere) == 0: return 0
    average_solvation = solvation(model, x, y, z, radius, pc=pc, het=het, metal=metal)
    sum_, r2 = 0, 0
    for atom in sphere:
        distance = atom.distance_to((x, y, z))
        solv = ((atom_partial_charge(atom)) ** 2) if pc else atom_solvation(atom)
        sum_ += solv * (distance ** 2)
        r2 += (distance ** 2)
    r2 /= len(sphere)
    return sum_ - (len(sphere) * average_solvation * r2)
