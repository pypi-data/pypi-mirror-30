import os
from bem import BEMModel, AerofoilDatabase, Blade


def load_blade(s, basepath):
    blade_filename = s['blade']['definition']
    if basepath:
        blade_filename = os.path.join(basepath, blade_filename)
    blade = Blade.from_yaml(blade_filename)

    min_spacing = s['blade'].get('minimum station spacing')
    if min_spacing:
        new_x = [blade.x[0]]
        for xi in blade.x[1:]:
            if xi - new_x[-1] > min_spacing:
                new_x.append(xi)
        blade = blade.resample(new_x)

    return blade


def load_bem(c, blade, root_length, basepath):

    # Load aerofoil database
    aerofoil_database = AerofoilDatabase(
        os.path.join(basepath, c['aerofoil database']))

    # Create BEM model
    model = BEMModel(blade, root_length, num_blades=3,
                     aerofoil_database=aerofoil_database)

    return model
