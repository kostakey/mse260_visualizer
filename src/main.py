import numpy as np
import pyvista as pv
from pymatgen.core import Structure
from lammps import lammps
from pathlib import Path

# ================= CONFIG =================
# BASE_DIR = Path(__file__).resolve().parent
# CIF_FILE = BASE_DIR / "structures" / "ICSD_CollCode18189.cif"
CIF_FILE = "structures/ICSD_CollCode18189.cif"
SUPERCELL = (2, 2, 2)

CATION_RADII = np.linspace(1.4, 0.6, 40)
ANION_RADIUS = 1.0

BOND_CUTOFF = 2.6


# ================= LOAD STRUCTURE =================
struct = Structure.from_file(CIF_FILE)
struct = struct * SUPERCELL

pos0 = struct.cart_coords
species = np.array([s.symbol for s in struct.species])

unique = sorted(set(species))
type_map = {s: i for i, s in enumerate(unique)}
inv_map = {v: k for k, v in type_map.items()}

types = np.array([type_map[s] for s in species])

# Safer assumption: first = cation, second = anion
CAT = 1 # flipped to test
AN = 0


# ================= LAMMPS RELAXATION =================
def relax(pos, types, r_cat, r_an):

    L = lammps(cmdargs=["-log", "none"])

    L.command("units lj")
    L.command("atom_style atomic")
    L.command("boundary p p p")

    L.command("region box block -20 20 -20 20 -20 20")
    L.command("create_box 2 box")

    for i, p in enumerate(pos):
        L.command(f"create_atoms {types[i] + 1} single {p[0]} {p[1]} {p[2]}")

    L.command("mass * 1.0")

    sig_ca = (r_cat + r_an) / 1.12246
    sig_aa = (2 * r_an) / 1.12246

    L.command("pair_style lj/cut 6.0")
    L.command(f"pair_coeff * * 1.0 {sig_aa}")
    L.command(f"pair_coeff 1 2 1.0 {sig_ca}")

    L.command("min_style fire")
    L.command("minimize 1e-6 1e-8 1000 10000")

    coords = np.array(L.gather_atoms("x", 1, 3)).reshape(-1, 3)

    L.close()
    return coords


# ================= PRECOMPUTE FRAMES =================
print("Running LAMMPS...")
frames = []

for r in CATION_RADII:
    relaxed = relax(pos0, types, r, ANION_RADIUS)
    frames.append((r, relaxed.copy(), types.copy()))


# ================= VISUALIZATION =================
plotter = pv.Plotter()
plotter.set_background("white")

state = {"actors": []}


def clear():
    for a in state["actors"]:
        plotter.remove_actor(a)
    state["actors"].clear()

    plotter.remove_actor("labels")
    plotter.remove_actor("text")


# ================= ATOM RENDERING =================
def add_atoms(x, color, radius):
    pts = pv.PolyData(x)

    # IMPORTANT: explicit scaling per atom type
    pts["scale"] = np.full(len(x), radius)

    glyph = pts.glyph(
        scale="scale",
        geom=pv.Sphere(),
        factor=1.0,
        orient=False
    )

    actor = plotter.add_mesh(glyph, color=color)
    state["actors"].append(actor)


# ================= UPDATE FUNCTION =================
def update(value):

    clear()

    idx = (np.abs(CATION_RADII - value)).argmin()
    r, pos, t = frames[idx]

    # ---- ATOMS ----
    cat_pos = pos[t == CAT]
    an_pos = pos[t == AN]

    add_atoms(cat_pos, "red", r)              # CATION (changes)
    add_atoms(an_pos, "blue", ANION_RADIUS)   # ANION (fixed)

    # ---- LABELS ----
    labels = [inv_map[i] for i in t]

    plotter.add_point_labels(
        pos,
        labels,
        font_size=14,
        text_color="black",
        shape=None,
        shape_opacity=0,
        name="labels"
    )

    # ---- BONDS ----
    for c in cat_pos:
        d = np.linalg.norm(an_pos - c, axis=1)
        for n in an_pos[d < BOND_CUTOFF]:
            line = pv.Line(c, n)
            a = plotter.add_mesh(line, color="black", line_width=1)
            state["actors"].append(a)

    # ---- TEXT ----
    cn = np.mean([
        np.sum(np.linalg.norm(an_pos - c, axis=1) < BOND_CUTOFF)
        for c in cat_pos
    ])

    plotter.add_text(
        f"Cation radius: {r:.2f}\nAvg CN: {cn:.2f}",
        font_size=14,
        name="text"
    )


# ================= SLIDER =================
plotter.add_slider_widget(
    update,
    rng=[CATION_RADII.min(), CATION_RADII.max()],
    value=CATION_RADII.max(),
    title="Cation Radius",
    style="modern"
)

update(CATION_RADII.max())
plotter.show()

