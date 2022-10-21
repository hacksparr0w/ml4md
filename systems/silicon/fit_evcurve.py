import matplotlib.pyplot as plt
import numpy as np
import scipy.constants
import scipy.optimize


q_0 = scipy.constants.e


def birch_murnaghan(v, e_0, v_0, b_0, b_0_prime):
    return (
        e_0 +
        ((9 / 16) * v_0 * b_0) * (
            ((v_0 / v) ** (2 / 3) - 1) ** 3 * b_0_prime +
            ((v_0 / v) ** (2 / 3) - 1) ** 2 * (6 - 4 * (v_0 / v) ** (2 / 3))
        )
    )


def to_gpa(p):
    return p * q_0 * 1e30 * 1e-9

def main():
    data = np.genfromtxt("./baseline/minimize.csv")
    v, e = data[:,0], data[:,1]
    p0 = [np.min(e), np.min(v), 1, 1]
    args, pcov = scipy.optimize.curve_fit(birch_murnaghan, v, e, p0=p0)
    e_0, v_0, b_0, b_0_p = args

    color = "tab:orange"
    plt.plot(v, e, "o", color=color, label="data")
    plt.plot(
        v,
        birch_murnaghan(v, *args),
        color=color,
        label=(
            f"BM fit: $E_0 = {round(e_0, 4)} \, \mathrm{{eV}}$, \n"
            f"$V_0 = {round(v_0, 4)} \, \mathrm{{Å}}^3$, \n"
            f"$B_0 = {round(to_gpa(b_0), 4)} \, \mathrm{{GPa}}$, \n"
            f"$B_0' = {round(b_0_p, 4)}$"
        )
    )

    plt.grid()
    plt.legend()
    plt.xlabel("$V \; [\mathrm{Å}^3]$")
    plt.ylabel("$E \; [\mathrm{eV}]$")
    plt.tight_layout()

    plt.savefig("./baseline/evcurve.jpg")


if __name__ == "__main__":
    main()
