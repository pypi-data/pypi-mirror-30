from numpy import pi, sin, cos

def transform_to_canonical_range_of_spherical_coordinate(rho, theta, phi):
    """Transform given spherical coordinates into canonical range

    ## NOTE: Canonical range of spherical coordinate
    #
    # Definition
    The canonical range of spherical coodrinate depends on the definition.
    In this funtion, the canoncial range is defined by the following:
    - 0 <= rho
    - 0 <= theta <= pi
    - 0 <= phi < 2.0*pi
    #
    # (OBSOLATE) On 'thate' range:
    Since coordinates associated with 'theta = 0' and 'theta = pi' are differnet,
    theta = pi should not be transformed to theta = 0 in order to be distinguished.
    """
    ## Argument check is omitted for accumulative performance

    ## Perform pre-processing
    # (180319, OBSOLATE) Move 'theta' to range of -pi <= thata < pi
    #theta = ((theta + pi) % (2.0*pi)) - pi
    # Move 'theta' to range of 0 <= thata < 2*pi
    theta %= 2.0 * pi

    ## Identify current range
    rho_is_negative = (rho < 0)
    # '(theta < 2.0) * pi' is assured by 'tehta %= 2.0 * pi' statement
    theta_is_between_phi_and_2phi = (pi < theta)
    #theta_is_negative = (theta < 0)

    ## Transform depending on the identified range
    if not rho_is_negative and not theta_is_between_phi_and_2phi:
        pass
    elif rho_is_negative and not theta_is_between_phi_and_2phi:
        rho *= -1.0
        # the range of phi will be shifted to canonical range in the end
        # .. so adding pi here is expected to raise no problem.
        phi += pi
        # (180319, OBSOLATE) [NOTE] if theta was exacly 0.0, then theta would be pi,
        # .. which isn't in the canonical range.
        # .. this effect will be compensated at the end of thie function (post-processing)
        # => (corrected NOTE) since theta is in range of '0 <= theta <= pi'
        # .. '0 <= pi - theta <= pi', thus, there's no need for rearranging
        # .. 'theta' into canonical range since it is already in there.
        theta = pi - theta
    elif not rho_is_negative and theta_is_between_phi_and_2phi:
        #theta *= -1.0  # (180319, OBSOLATE)
        theta = 2.0 * pi - theta
        phi += pi  # the range of phi will be shifted to canonical range in the end
    else: # rho_is_negative and theta_is_between_phi_and_2phi
        rho *= -1.0
        # (180319, OBSOLATE) adding pi into theta doesn't matter in terms of range,
        # .. since theta was negative and was in range -pi <= theta < pi
        # => (corrected NOTE) since 'theta_is_between_phi_and_2phi',
        # .. 'theta - pi' is in range '0 < theta += pi < pi',
        # .. which belongs to the canoncial range.
        #theta += pi
        theta -= pi

    ## Perform post-processing
    # [180317 NOTE] I should consider setting divider of this modulo operation
    # .. slightly smaller than actual divdier (e.g. 2.0*pi) to prevent strange out-of-range-effect
    phi %= 2.0 * pi  #- small_amount
    # [180319, NOTE] there's no need for this. Actually, it should be prohibited
    # .. since 'theta = pi' will be moved to '0' if this statement remains.
    #theta %= pi  #- small_amount

    return rho, theta, phi


def spherical_to_cartesian(rho, theta, phi):
    """Convert spherical coordinate vector to Cartesian coordinate vector"""
    x = rho * sin(theta) * cos(phi)
    y = rho * sin(theta) * sin(phi)
    z = rho * cos(theta)
    return x, y, z
