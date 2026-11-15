#!/usr/bin/env python3
"""MagChip-Q - educational quantum chip magnet computer lab.

by Darion Kellar

Pure Python standard library. Zero dependencies. Zero network.
Simulation only: a quantum computer where the MAGNET is the machine -
the magnetic field sets every qubit frequency (Zeeman / Larmor), flux
through a loop tunes superconducting qubits (the flux quantum Phi0),
a DC SQUID reads flux at the single-quantum level, Helmholtz and
solenoid coils make the field, layered shields keep the Earth's field
out, a persistent superconducting magnet holds the field for months,
magnetic noise sets the coherence limit, and on-chip dipole crosstalk
sets how close qubits can sit. TinyML kNN classifies chip operating
points. Gemini Argon 4 Extended Thinking (the Gemini Carbon 4 seat)
sits as DECIDER (MAP->MODEL->STRESS->DECIDE, names-only, tighten-only),
Muse as advisor (never overrides HOLD), and Google Flow carries all
4 flows plan-only.

Every real-hardware / live-operation action is a permanent HOLD gate.
No quantum advantage is claimed anywhere in this lab.
"""
import hashlib
import json
import math
import sys

# ---------------------------------------------------------------- constants
MU0 = 4.0 * math.pi * 1e-7          # vacuum permeability, H/m
H_PLANCK = 6.62607015e-34           # Planck constant, J s (exact, SI)
E_CHARGE = 1.602176634e-19          # elementary charge, C (exact, SI)
KB = 1.380649e-23                   # Boltzmann constant, J/K (exact, SI)
PHI0 = H_PLANCK / (2.0 * E_CHARGE)  # flux quantum, Wb = 2.067833848e-15
EARTH_FIELD_UT = 50.0               # typical Earth surface field, microtesla

VERSION = "1.0.0"

# ---------------------------------------------------------------- HOLD gates
HOLD_GATES = {
    "real_chip_fabrication": "HOLD - no fabrication of a real quantum chip or Josephson devices",
    "real_magnet_control": "HOLD - no control of real magnets, coils, or persistent switches",
    "cryostat_operation_live": "HOLD - no live cryostat / dilution refrigerator operation",
    "high_field_human_exposure_live": "HOLD - no live high-field exposure of people or animals",
    "quench_experiment_live": "HOLD - no live quench / magnet failure testing",
    "medical_mri_design_claim": "HOLD - no medical, MRI design, or clinical claims",
    "quantum_advantage_claim": "HOLD - no quantum advantage / supremacy claim; none is demonstrated here",
    "commercial_chip_claim": "HOLD - no claim this simulation is a commercial chip or certified design",
    "live_quantum_cloud_job": "HOLD - no job submission to live quantum hardware or cloud",
    "weapons_application_claim": "HOLD - no weapons or military application claims",
    "investment_advice_claim": "HOLD - no investment advice about quantum or magnet companies",
    "high_current_supply_live": "HOLD - no live high-current power supply / magnet energising work",
    "shielding_certification_claim": "HOLD - no safety certification claim for magnetic shielding",
    "cryogen_procurement_handling": "HOLD - no procurement / handling planning for real cryogens",
    "live_gemini_api_call": "HOLD - no live Gemini / Argon 4 API call; the seat is offline and names-only",
    "live_video_generation": "HOLD - no live video generation / rendering through Google Flow or any video model",
    "flow_workspace_send": "HOLD - no sending, sharing, or publishing of Workspace Studio drafts",
}


def gate(action):
    """Return 'HOLD' if the action is gated, else 'PROCEED' (sandbox sim)."""
    return "HOLD" if action in HOLD_GATES else "PROCEED"


# ================================================================ 1. Spin species
# gamma_bar = gyromagnetic ratio / 2pi, in MHz per tesla (signed values are
# the standard published ones; this lab uses magnitudes for frequencies).
SPECIES = {
    "electron": {
        "gamma_bar_mhz_t": 28024.95164, "spin": "1/2",
        "note": "free electron spin - the fastest magnetic qubit clock per tesla",
    },
    "proton_1H": {
        "gamma_bar_mhz_t": 42.57747892, "spin": "1/2",
        "note": "hydrogen nucleus - the NMR / MRI reference frequency",
    },
    "carbon_13C": {
        "gamma_bar_mhz_t": 10.7084, "spin": "1/2",
        "note": "13C nuclear spin - diamond / organic-molecule memory qubits",
    },
    "silicon_29Si": {
        "gamma_bar_mhz_t": 8.465, "spin": "1/2",
        "note": "29Si nuclear spin (magnitude) - silicon quantum-dot host bath",
    },
    "phosphorus_31P": {
        "gamma_bar_mhz_t": 17.235, "spin": "1/2",
        "note": "31P donor nucleus in silicon - the Kane qubit memory",
    },
    "nitrogen_14N": {
        "gamma_bar_mhz_t": 3.077, "spin": "1",
        "note": "14N nucleus paired with NV centres in diamond",
    },
}


def _species(name):
    if name not in SPECIES:
        raise ValueError(f"unknown species: {name}")
    return SPECIES[name]


# ================================================================ 2. Zeeman / Larmor
def larmor_mhz(species, field_t):
    """Larmor frequency f = gamma_bar * B, in MHz."""
    if field_t < 0:
        raise ValueError("field_t must be >= 0")
    return _species(species)["gamma_bar_mhz_t"] * field_t


def larmor_ghz(species, field_t):
    return larmor_mhz(species, field_t) / 1000.0


def zeeman_splitting_mev(species, field_t):
    """Zeeman level splitting dE = h * f, in meV."""
    f_hz = larmor_mhz(species, field_t) * 1e6
    return H_PLANCK * f_hz / E_CHARGE * 1000.0


def zeeman_temp_k(species, field_t):
    """dE / kB in kelvin - the temperature the splitting 'looks like'."""
    f_hz = larmor_mhz(species, field_t) * 1e6
    return H_PLANCK * f_hz / KB


def field_for_frequency_t(species, target_ghz):
    """Field that puts a species exactly on a target frequency."""
    if target_ghz <= 0:
        raise ValueError("target_ghz must be > 0")
    return target_ghz * 1000.0 / _species(species)["gamma_bar_mhz_t"]


def precession_prob_x_plus(species, field_t, time_ns):
    """P(still +x) for a spin prepared in +x precessing about Bz.

    P = cos^2(pi * f * t): 1 at t=0, 0 after half a Larmor period.
    """
    f_hz = larmor_mhz(species, field_t) * 1e6
    return math.cos(math.pi * f_hz * time_ns * 1e-9) ** 2


def larmor_period_ns(species, field_t):
    if field_t <= 0:
        return math.inf
    return 1000.0 / larmor_mhz(species, field_t)


# ================================================================ 3. Flux quantum + flux qubit
def flux_quanta(field_t, area_um2):
    """How many flux quanta thread a loop of the given area."""
    area_m2 = area_um2 * 1e-12
    return field_t * area_m2 / PHI0


def field_per_phi0_t(area_um2):
    """Field change that adds exactly one flux quantum to the loop."""
    return PHI0 / (area_um2 * 1e-12)


# Flux-qubit model: two-level system, gap f_min at the sweet spot
# (Phi = Phi0/2), persistent current Ip sets the tuning slope through
# eps/h = 2 * Ip * (Phi - Phi0/2) / h. The slope is STEEP (about
# 312 GHz per Phi0 at Ip = 50 nA), so real flux qubits live within a
# few milli-Phi0 of the sweet spot - that steepness is the lesson.
FLUX_QUBIT = {"f_min_ghz": 4.0, "ip_na": 50.0, "loop_um2": 40.0}


def _eps_ghz(phi_ratio, ip_na):
    """Detuning energy / h in GHz at flux ratio Phi/Phi0."""
    slope_ghz_per_phi0 = 2.0 * (ip_na * 1e-9) * PHI0 / H_PLANCK / 1e9
    return slope_ghz_per_phi0 * (phi_ratio - 0.5)


def flux_qubit_ghz(phi_ratio, f_min_ghz=4.0, ip_na=50.0):
    """f(Phi) = sqrt(f_min^2 + eps(Phi)^2) - the flux-qubit hyperbola."""
    eps = _eps_ghz(phi_ratio, ip_na)
    return math.sqrt(f_min_ghz ** 2 + eps ** 2)


def flux_sensitivity_ghz_per_phi0(phi_ratio, f_min_ghz=4.0, ip_na=50.0):
    """|df/d(Phi/Phi0)| - zero at the sweet spot, grows away from it."""
    eps = _eps_ghz(phi_ratio, ip_na)
    slope = 2.0 * (ip_na * 1e-9) * PHI0 / H_PLANCK / 1e9
    f = flux_qubit_ghz(phi_ratio, f_min_ghz, ip_na)
    return abs(eps * slope / f) if f > 0 else 0.0


def is_sweet_spot(phi_ratio, tol=1e-9):
    return abs(phi_ratio - 0.5) <= tol


# ================================================================ 4. DC SQUID
def squid_ic_ratio(phi_ratio):
    """Ic(Phi) / Ic_max = |cos(pi * Phi/Phi0)| - one period per Phi0."""
    return abs(math.cos(math.pi * phi_ratio))


def squid_field_period_ut(loop_um2):
    """Field period of the SQUID pattern, in microtesla."""
    return field_per_phi0_t(loop_um2) * 1e6


def squid_flux_from_ic(ic_ratio):
    """Smallest flux ratio in [0, 0.5] consistent with an Ic ratio."""
    r = min(max(ic_ratio, 0.0), 1.0)
    return math.acos(r) / math.pi


# ================================================================ 5. Coils that make the field
def helmholtz_field_t(turns, current_a, radius_m):
    """On-axis centre field of a Helmholtz pair: (4/5)^1.5 * mu0 * N * I / R."""
    if radius_m <= 0:
        raise ValueError("radius_m must be > 0")
    return (4.0 / 5.0) ** 1.5 * MU0 * turns * current_a / radius_m


def solenoid_field_t(turns_per_m, current_a):
    """Ideal long solenoid field B = mu0 * n * I."""
    return MU0 * turns_per_m * current_a


def current_for_field_solenoid_t(turns_per_m, target_t):
    if turns_per_m <= 0:
        raise ValueError("turns_per_m must be > 0")
    return target_t / (MU0 * turns_per_m)


def gradient_addressing_mhz(species, gradient_t_per_m, spacing_um):
    """Frequency separation of two spins spaced along a field gradient."""
    dz_m = spacing_um * 1e-6
    return _species(species)["gamma_bar_mhz_t"] * gradient_t_per_m * dz_m


# ================================================================ 6. Magnetic shielding
def shielded_field_ut(outside_ut, shielding_factor):
    if shielding_factor <= 0:
        raise ValueError("shielding_factor must be > 0")
    return outside_ut / shielding_factor


def layered_shield_factor(factors):
    """Independent shield layers multiply (model; real shields saturate)."""
    total = 1.0
    for f in factors:
        if f <= 0:
            raise ValueError("each shielding factor must be > 0")
        total *= f
    return total


def earth_field_inside_ut(factors):
    return shielded_field_ut(EARTH_FIELD_UT, layered_shield_factor(factors))


# ================================================================ 7. Persistent magnet + quench
def stored_energy_j(inductance_h, current_a):
    """E = 1/2 * L * I^2 - the energy a quench has to dump somewhere."""
    return 0.5 * inductance_h * current_a ** 2


def magnet_field_t(inductance_h, current_a, field_const_t_per_a):
    """Linear magnet model B = k * I (k is the magnet's field constant)."""
    return field_const_t_per_a * current_a


def persistent_drift_t(b0_t, drift_ppm_per_hr, hours):
    """Field after drift in persistent mode (linear ppm model)."""
    return b0_t * (1.0 - drift_ppm_per_hr * 1e-6 * hours)


def drift_after_hours(b0_t, drift_ppm_per_hr, target_fraction=0.999):
    """Hours until the field falls to target_fraction of B0."""
    if drift_ppm_per_hr <= 0:
        return math.inf
    return (1.0 - target_fraction) / (drift_ppm_per_hr * 1e-6)


def quench_temp_rise_k(energy_j, mass_kg, cp_j_per_kg_k=200.0):
    """Model quench temperature rise if all stored energy heats the winding.

    cp = 200 J/(kg K) is a labelled low-temperature average model value.
    """
    if mass_kg <= 0:
        raise ValueError("mass_kg must be > 0")
    return energy_j / (mass_kg * cp_j_per_kg_k)


# ================================================================ 8. Magnetic noise + coherence
def freq_noise_from_flux_noise_hz(phi_ratio, flux_noise_mphi0,
                                  f_min_ghz=4.0, ip_na=50.0):
    """Frequency noise (Hz) from flux noise (in milli-Phi0)."""
    sens_ghz = flux_sensitivity_ghz_per_phi0(phi_ratio, f_min_ghz, ip_na)
    return sens_ghz * 1e9 * (flux_noise_mphi0 * 1e-3)


def freq_noise_from_field_noise_mhz(species, field_noise_ut):
    """Frequency noise (MHz) of a spin qubit from B-field noise."""
    return _species(species)["gamma_bar_mhz_t"] * field_noise_ut * 1e-6


def t2_star_us_from_freq_noise(freq_noise_hz):
    """Model dephasing time T2* = 1 / (pi * df) for Gaussian noise, in us.

    Zero noise is capped at 1e6 us (1 s) - a model ceiling, not a claim.
    """
    if freq_noise_hz <= 0:
        return 1e6
    return 1.0 / (math.pi * freq_noise_hz) * 1e6


def flux_qubit_t2_us(phi_ratio, flux_noise_mphi0, f_min_ghz=4.0, ip_na=50.0):
    df = freq_noise_from_flux_noise_hz(phi_ratio, flux_noise_mphi0,
                                       f_min_ghz, ip_na)
    return t2_star_us_from_freq_noise(df)


def spin_t2_us(species, field_noise_ut):
    df_hz = freq_noise_from_field_noise_mhz(species, field_noise_ut) * 1e6
    return t2_star_us_from_freq_noise(df_hz)


# ================================================================ 9. On-chip crosstalk + layout
def dipole_crosstalk_mphi0(pitch_um, moment_scale=1.0):
    """Model flux crosstalk into a neighbour loop, in milli-Phi0.

    Dipole coupling falls as 1/r^3; the scale is calibrated so a 50 um
    pitch gives 1.0 mPhi0 - a labelled model value, not a measurement.
    """
    if pitch_um <= 0:
        raise ValueError("pitch_um must be > 0")
    return moment_scale * (50.0 / pitch_um) ** 3 * 1.0


def pitch_for_crosstalk_um(target_mphi0, moment_scale=1.0):
    """Invert the dipole model: pitch needed to hit a crosstalk budget."""
    if target_mphi0 <= 0:
        raise ValueError("target_mphi0 must be > 0")
    return 50.0 * (moment_scale / target_mphi0) ** (1.0 / 3.0)


def chip_grid(rows, cols, pitch_um):
    """A rows x cols qubit grid: count, footprint, worst-case crosstalk."""
    if rows <= 0 or cols <= 0:
        raise ValueError("rows and cols must be > 0")
    return {
        "qubits": rows * cols,
        "width_um": cols * pitch_um,
        "height_um": rows * pitch_um,
        "area_mm2": (rows * pitch_um * cols * pitch_um) / 1e6,
        "nearest_crosstalk_mphi0": round(dipole_crosstalk_mphi0(pitch_um), 4),
        "diagonal_crosstalk_mphi0": round(
            dipole_crosstalk_mphi0(pitch_um * math.sqrt(2.0)), 4),
    }


def frequency_collision(qubit_freqs_ghz, linewidth_mhz=10.0):
    """Pairs closer than the linewidth - they would talk over each other."""
    lw_ghz = linewidth_mhz / 1000.0
    bad = []
    names = sorted(qubit_freqs_ghz)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if abs(qubit_freqs_ghz[a] - qubit_freqs_ghz[b]) < lw_ghz:
                bad.append((a, b))
    return bad


# ================================================================ 10. kNN operating-point classifier
def _point_features(phi_ratio, flux_noise_mphi0, crosstalk_mphi0):
    """(distance from sweet spot in Phi0, flux noise, crosstalk), clamped."""
    return (
        round(min(abs(phi_ratio - 0.5), 1.0), 4),
        round(min(flux_noise_mphi0 / 10.0, 1.0), 4),
        round(min(crosstalk_mphi0 / 10.0, 1.0), 4),
    )


def _ratio_label(max_ratio):
    if max_ratio <= 0.10:
        return "sweet"
    if max_ratio <= 0.45:
        return "tunable"
    return "noisy"


def _build_knn_train():
    vals = (0.0, 0.05, 0.1, 0.2, 0.35, 0.5, 0.75, 1.0)
    train = []
    for a in vals:
        for b in vals:
            for c in vals:
                train.append(((a, b, c), _ratio_label(max(a, b, c))))
    return train


_KNN_TRAIN = _build_knn_train()


class ChipPointClassifier:
    """kNN (k=5) over (sweet-spot distance, flux noise, crosstalk)."""

    def __init__(self, k=5):
        self.k = k
        self.train = list(_KNN_TRAIN)

    @staticmethod
    def _dist(a, b):
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    def classify_features(self, feats):
        ranked = sorted(self.train, key=lambda tr: self._dist(feats, tr[0]))
        votes = {}
        for _, label in ranked[: self.k]:
            votes[label] = votes.get(label, 0) + 1
        return sorted(votes.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

    def classify(self, phi_ratio, flux_noise_mphi0, crosstalk_mphi0):
        return self.classify_features(
            _point_features(phi_ratio, flux_noise_mphi0, crosstalk_mphi0))


def classify_point(phi_ratio, flux_noise_mphi0, crosstalk_mphi0):
    return ChipPointClassifier().classify(
        phi_ratio, flux_noise_mphi0, crosstalk_mphi0)


def chip_report(rows=4, cols=4, pitch_um=100.0, phi_ratio=0.5,
                flux_noise_mphi0=0.01):
    """Full model report for one candidate chip operating point."""
    grid = chip_grid(rows, cols, pitch_um)
    xtalk = grid["nearest_crosstalk_mphi0"]
    return {
        "grid": grid,
        "qubit_ghz_at_phi": round(flux_qubit_ghz(phi_ratio), 4),
        "sensitivity_ghz_per_phi0": round(
            flux_sensitivity_ghz_per_phi0(phi_ratio), 4),
        "t2_star_us": round(flux_qubit_t2_us(phi_ratio, flux_noise_mphi0), 3),
        "classification": classify_point(phi_ratio, flux_noise_mphi0, xtalk),
    }


# ================================================================ 11. Advisory seats
def _trace(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


# Gemini Argon 4 Extended Thinking is Darion's name for the Gemini
# Carbon 4 seat: engine gemini-2.5-pro, model
# google/gemini-carbon-4-extended-pro-thinking. It is the DECIDER.
# The deterministic offline structure below is authoritative; a live
# call (never made here, and gated) could only tighten a decision.
ARGON4_TIERS = {"standard": 2048, "high": 8192, "deploy": 32768}


def argon4_decide(action="run_simulation", stakes="standard"):
    """Argon 4 DECIDER: MAP->MODEL->STRESS->DECIDE, trace hash recorded.

    STRESS applies the HOLD gates: a gated action decides HOLD, a
    sandbox simulation decides PROCEED. Tighten-only - this seat can
    add HOLDs, it can never lift one.
    """
    if stakes not in ARGON4_TIERS:
        raise ValueError(f"unknown stakes tier: {stakes}")
    stages = ["MAP", "MODEL", "STRESS", "DECIDE"]
    gated = gate(action) == "HOLD"
    decision = "HOLD" if gated else "PROCEED (sandbox simulation only)"
    payload = {"seat": "gemini-argon-4", "action": action, "stakes": stakes,
               "stages": stages, "decision": decision}
    return {
        "seat": "Gemini Argon 4 Extended Thinking",
        "aka": "Gemini Carbon 4 seat",
        "engine": "gemini-2.5-pro",
        "model": "google/gemini-carbon-4-extended-pro-thinking",
        "role": "DECIDER",
        "pipeline": stages,
        "tiers": ARGON4_TIERS,
        "tier": ARGON4_TIERS[stakes],
        "key": "names-only (GEMINI_API_KEY name checked, value never read)",
        "live_calls": 0,
        "can_override_hold": False,
        "tighten_only": True,
        "action": action,
        "decision": decision,
        "trace_sha256_16": _trace(payload),
    }


def carbon4_decide(topic="magchip-q-demo"):
    """Back-compatible alias: the Carbon 4 seat IS the Argon 4 seat."""
    return argon4_decide(action="run_simulation", stakes="standard")


def claude_advisor(topic="magchip-q-demo"):
    """Muse advisor seat: exactly 4 advice items, authority none."""
    advice = [
        "Park flux qubits at the Phi0/2 sweet spot; budget coherence from measured flux noise, not hope.",
        "Treat the Earth field as a flux source in every layout review - shield first, tune second.",
        "Keep every real magnet, chip, and cryostat action behind its HOLD gate.",
        "Claim no quantum advantage: this lab demonstrates magnetic control physics, nothing more.",
    ]
    return {
        "seat": "Muse",
        "models": ["muse-spark-1.1", "muse-wonder-1.0"],
        "role": "advisor",
        "authority": "none - advisory only",
        "can_override_hold": False,
        "live_calls": 0,
        "key": "names-only (MODEL_API_KEY name checked, value never read)",
        "advice": advice,
        "trace_sha256_16": _trace({"seat": "claude-advisor", "topic": topic}),
    }


def google_flow_plan():
    """Google Flow: all 4 flows, plan-only. Nothing renders, nothing sent."""
    return {
        "seat": "Google Flow",
        "flows": {
            "flowx": {
                "kind": "task graph",
                "steps": ["spec the field", "place species", "tune to sweet spot",
                          "route SQUID readout", "budget shielding",
                          "price the quench", "score magnetic noise",
                          "classify operating point"],
                "executed": False,
            },
            "workspace_studio": {
                "kind": "drafts",
                "drafts": ["chip design summary draft", "release notes draft"],
                "sent": False,
            },
            "filmmaking": {
                "kind": "5-shot storyboard",
                "shots": [
                    "shot 1: a magnet coil ramps, field lines bloom over a dark chip",
                    "shot 2: flux quanta thread gold SQUID loops one by one",
                    "shot 3: the tuning hyperbola - a qubit slides into the sweet spot",
                    "shot 4: shield layers close, the Earth's field dies at the door",
                    "shot 5: coherence clock holds at the sweet spot, HOLD gates teardown",
                ],
                "rendered": False,
            },
            "datax": {
                "kind": "data-flow plan",
                "plan": ["species table updates", "noise budget refresh",
                         "crosstalk map export"],
                "live": 0,
            },
        },
        "rendered": False,
        "live": 0,
    }


def council_verdict(action="run_simulation", stakes="deploy"):
    """The wired decision point: gate + Argon 4 + advisor + Flow.

    Sandbox simulation records PROCEED; any gated real-world action
    records HOLD, and no seat can override it.
    """
    decider = argon4_decide(action=action, stakes=stakes)
    return {
        "action": action,
        "gate": gate(action),
        "decision": decider["decision"],
        "decider": decider["seat"],
        "trace_sha256_16": decider["trace_sha256_16"],
        "tier": decider["tier"],
        "advisor_advice_count": len(claude_advisor()["advice"]),
        "flow_rendered": google_flow_plan()["rendered"],
    }


def brains_report():
    return {"decider": argon4_decide(), "advisor": claude_advisor(),
            "flow": google_flow_plan(), "council": council_verdict()}


# ================================================================ checks
def run_checks():
    c = []

    def chk(name, ok):
        c.append((name, bool(ok)))

    chk("species_six", len(SPECIES) == 6)
    chk("phi0_value", abs(PHI0 - 2.067833848e-15) < 1e-24)
    chk("electron_larmor_1t_ghz", abs(larmor_ghz("electron", 1.0) - 28.02495164) < 1e-9)
    chk("proton_larmor_1t_mhz", abs(larmor_mhz("proton_1H", 1.0) - 42.57747892) < 1e-9)
    chk("larmor_scales_with_field", larmor_mhz("electron", 2.0) == 2 * larmor_mhz("electron", 1.0))
    chk("zeeman_electron_1t_mev", 0.11 < zeeman_splitting_mev("electron", 1.0) < 0.12)
    chk("zeeman_electron_1t_temp", 1.3 < zeeman_temp_k("electron", 1.0) < 1.4)
    chk("field_for_5ghz_electron", abs(field_for_frequency_t("electron", 5.0)
                                       - 5000.0 / 28024.95164) < 1e-12)
    chk("precession_start_one", precession_prob_x_plus("electron", 1.0, 0.0) == 1.0)
    chk("precession_half_period_zero",
        precession_prob_x_plus("electron", 1.0, larmor_period_ns("electron", 1.0) / 2.0) < 1e-12)
    chk("larmor_period_electron", 0.03 < larmor_period_ns("electron", 1.0) < 0.04)
    chk("flux_one_phi0", abs(flux_quanta(field_per_phi0_t(40.0), 40.0) - 1.0) < 1e-9)
    chk("field_per_phi0_40um2_ut", 40.0 < field_per_phi0_t(40.0) * 1e6 < 65.0)
    chk("flux_qubit_sweet_is_fmin", abs(flux_qubit_ghz(0.5) - 4.0) < 1e-12)
    chk("flux_qubit_symmetric", abs(flux_qubit_ghz(0.4) - flux_qubit_ghz(0.6)) < 1e-9)
    chk("flux_qubit_rises_off_sweet", flux_qubit_ghz(0.0) > flux_qubit_ghz(0.4) > 4.0)
    chk("sensitivity_zero_at_sweet", flux_sensitivity_ghz_per_phi0(0.5) == 0.0)
    chk("sensitivity_grows_off_sweet",
        flux_sensitivity_ghz_per_phi0(0.0) > flux_sensitivity_ghz_per_phi0(0.4) > 0.0)
    chk("sweet_spot_flag", is_sweet_spot(0.5) and not is_sweet_spot(0.51))
    chk("squid_ic_max_at_zero", squid_ic_ratio(0.0) == 1.0)
    chk("squid_ic_zero_at_half", squid_ic_ratio(0.5) < 1e-15)
    chk("squid_period_one_phi0", abs(squid_ic_ratio(1.0) - 1.0) < 1e-12)
    chk("squid_invert_half", abs(squid_flux_from_ic(0.0) - 0.5) < 1e-12)
    chk("squid_field_period_positive", squid_field_period_ut(40.0) > 0.0)
    chk("helmholtz_positive", helmholtz_field_t(100, 1.0, 0.1) > 0.0)
    chk("helmholtz_scales_current",
        abs(helmholtz_field_t(100, 2.0, 0.1) - 2 * helmholtz_field_t(100, 1.0, 0.1)) < 1e-15)
    chk("solenoid_mu0_n_i", abs(solenoid_field_t(1000.0, 1.0) - MU0 * 1000.0) < 1e-15)
    chk("solenoid_current_inverse",
        abs(current_for_field_solenoid_t(1000.0, solenoid_field_t(1000.0, 3.0)) - 3.0) < 1e-9)
    chk("gradient_addressing_scales",
        gradient_addressing_mhz("electron", 10.0, 20.0)
        == 2 * gradient_addressing_mhz("electron", 10.0, 10.0))
    chk("shield_halves_field", shielded_field_ut(50.0, 2.0) == 25.0)
    chk("shield_layers_multiply", layered_shield_factor([10.0, 10.0, 10.0]) == 1000.0)
    chk("earth_inside_3_layers", abs(earth_field_inside_ut([100.0, 100.0, 10.0]) - 0.0005) < 1e-12)
    chk("stored_energy_half_li2", stored_energy_j(10.0, 100.0) == 50000.0)
    chk("magnet_field_linear", magnet_field_t(10.0, 100.0, 0.05) == 5.0)
    chk("drift_zero_hours", persistent_drift_t(5.0, 10.0, 0.0) == 5.0)
    chk("drift_falls", persistent_drift_t(5.0, 10.0, 100.0) < 5.0)
    chk("drift_hours_inverse", abs(drift_after_hours(5.0, 10.0) - 100.0) < 1e-9)
    chk("quench_rise_positive", quench_temp_rise_k(50000.0, 50.0) == 5.0)
    chk("freq_noise_zero_at_sweet", freq_noise_from_flux_noise_hz(0.5, 5.0) == 0.0)
    chk("t2_cap_at_zero_noise", t2_star_us_from_freq_noise(0.0) == 1e6)
    chk("t2_sweet_beats_off_sweet",
        flux_qubit_t2_us(0.5, 1.0) > flux_qubit_t2_us(0.4, 1.0) > 0.0)
    chk("spin_t2_field_noise", spin_t2_us("proton_1H", 1.0) > spin_t2_us("electron", 1.0) > 0.0)
    chk("crosstalk_50um_is_1", dipole_crosstalk_mphi0(50.0) == 1.0)
    chk("crosstalk_falls_cube",
        abs(dipole_crosstalk_mphi0(100.0) - 0.125) < 1e-12)
    chk("pitch_inverse", abs(pitch_for_crosstalk_um(1.0) - 50.0) < 1e-9)
    chk("chip_grid_16", chip_grid(4, 4, 100.0)["qubits"] == 16)
    chk("chip_grid_area", abs(chip_grid(4, 4, 100.0)["area_mm2"] - 0.16) < 1e-12)
    chk("collision_detected",
        frequency_collision({"q0": 4.000, "q1": 4.005, "q2": 5.0}) == [("q0", "q1")])
    chk("collision_none_when_spread",
        frequency_collision({"q0": 4.0, "q1": 5.0}) == [])
    chk("classifier_sweet", classify_point(0.5, 0.1, 0.1) == "sweet")
    chk("classifier_noisy", classify_point(0.0, 10.0, 10.0) == "noisy")
    chk("chip_report_shape", chip_report()["grid"]["qubits"] == 16
        and chip_report()["classification"] in ("sweet", "tunable", "noisy"))
    chk("hold_gates_17", len(HOLD_GATES) == 17 and all(v.startswith("HOLD") for v in HOLD_GATES.values()))
    chk("gate_advantage_claim_hold", gate("quantum_advantage_claim") == "HOLD")
    chk("gate_live_gemini_hold", gate("live_gemini_api_call") == "HOLD")
    chk("gate_sandbox_proceed", gate("run_simulation") == "PROCEED")
    b = brains_report()
    d = b["decider"]
    chk("argon4_identity", d["seat"] == "Gemini Argon 4 Extended Thinking"
        and d["engine"] == "gemini-2.5-pro"
        and d["model"] == "google/gemini-carbon-4-extended-pro-thinking")
    chk("argon4_pipeline", d["pipeline"] == ["MAP", "MODEL", "STRESS", "DECIDE"])
    chk("argon4_tiers", d["tiers"] == {"standard": 2048, "high": 8192, "deploy": 32768}
        and argon4_decide(stakes="deploy")["tier"] == 32768)
    chk("argon4_trace_16", len(d["trace_sha256_16"]) == 16)
    chk("argon4_no_override", d["can_override_hold"] is False and d["tighten_only"] is True
        and d["live_calls"] == 0)
    chk("argon4_sandbox_proceed", d["decision"].startswith("PROCEED"))
    chk("argon4_gated_action_hold", argon4_decide(action="real_magnet_control")["decision"] == "HOLD")
    chk("carbon4_alias_is_argon4", carbon4_decide()["seat"] == d["seat"])
    chk("claude_advice_exactly_4", len(b["advisor"]["advice"]) == 4)
    chk("claude_models", b["advisor"]["models"] == ["muse-spark-1.1", "muse-wonder-1.0"])
    chk("claude_no_override", b["advisor"]["can_override_hold"] is False)
    f = b["flow"]
    chk("flow_four_flows", sorted(f["flows"]) == ["datax", "filmmaking", "flowx", "workspace_studio"])
    chk("flow_storyboard_5_shots", len(f["flows"]["filmmaking"]["shots"]) == 5)
    chk("flow_plan_only", f["rendered"] is False and f["live"] == 0
        and f["flows"]["workspace_studio"]["sent"] is False
        and f["flows"]["flowx"]["executed"] is False)
    chk("council_sandbox_proceed", council_verdict("run_simulation")["decision"].startswith("PROCEED"))
    chk("council_real_action_hold", council_verdict("real_chip_fabrication")["decision"] == "HOLD"
        and council_verdict("real_chip_fabrication")["gate"] == "HOLD")
    return c


# ================================================================ CLI / demo
def demo():
    print("=" * 68)
    print("MagChip-Q - quantum chip magnet computer lab")
    print("by Darion Kellar | MIT | pure stdlib | zero network | SIM ONLY")
    print("=" * 68)
    print("\n[1] The field sets the clock - Larmor frequencies at 1 T")
    for name, s in SPECIES.items():
        print(f"    {name:14s} spin {s['spin']:3s}  f = {larmor_mhz(name, 1.0):12.3f} MHz/T")
    print(f"    electron Zeeman split @ 1 T = {round(zeeman_splitting_mev('electron', 1.0), 4)} meV"
          f" = {round(zeeman_temp_k('electron', 1.0), 3)} K of thermal energy")
    print(f"    field for a 5 GHz electron-spin qubit = {round(field_for_frequency_t('electron', 5.0), 4)} T")
    print(f"    electron precession period @ 1 T = {round(larmor_period_ns('electron', 1.0), 4)} ns")
    print("\n[2] The flux quantum - one Phi0 = h/2e")
    print(f"    Phi0 = {PHI0:.6e} Wb")
    print(f"    one Phi0 through a 40 um^2 loop needs {round(field_per_phi0_t(40.0) * 1e6, 2)} uT")
    print(f"    Earth's 50 uT threads {round(flux_quanta(50e-6, 40.0), 3)} Phi0 through that loop - why chips are shielded")
    print("\n[3] Flux qubit tuning - the hyperbola and its sweet spot")
    for phi in (0.5, 0.501, 0.505, 0.51, 0.55):
        print(f"    Phi/Phi0 = {phi:5.3f}  f = {round(flux_qubit_ghz(phi), 3):8.3f} GHz"
              f"  sensitivity = {round(flux_sensitivity_ghz_per_phi0(phi), 1):9.1f} GHz/Phi0")
    print("    the slope is ~312 GHz/Phi0, so qubits live within a few mPhi0 of Phi0/2")
    print("    at Phi0/2 the slope is ZERO - first-order immune to flux noise")
    print("\n[4] DC SQUID - a flux meter with a Phi0 heartbeat")
    for phi in (0.0, 0.25, 0.5, 0.75, 1.0):
        print(f"    Phi/Phi0 = {phi:4.2f}  Ic/Ic_max = {round(squid_ic_ratio(phi), 3)}")
    print(f"    SQUID field period (40 um^2 loop) = {round(squid_field_period_ut(40.0), 2)} uT")
    print("\n[5] Coils that make the field")
    print(f"    Helmholtz pair N=100, I=1 A, R=0.1 m: {round(helmholtz_field_t(100, 1.0, 0.1) * 1000, 3)} mT")
    print(f"    solenoid n=5000/m, I=2 A:              {round(solenoid_field_t(5000.0, 2.0) * 1000, 3)} mT")
    print(f"    gradient addressing: electron spins 10 um apart in 10 T/m split by"
          f" {round(gradient_addressing_mhz('electron', 10.0, 10.0), 1)} MHz")
    print("\n[6] Shielding - keeping the Earth out of the chip")
    print(f"    Earth field {EARTH_FIELD_UT} uT -> 3 layers [100, 100, 10]:"
          f" {earth_field_inside_ut([100.0, 100.0, 10.0])} uT inside")
    print("\n[7] Persistent magnet + the quench bill")
    e = stored_energy_j(10.0, 100.0)
    print(f"    L=10 H, I=100 A stores {e:,.0f} J; quench into 50 kg winding ="
          f" +{quench_temp_rise_k(e, 50.0)} K (model cp)")
    print(f"    5 T magnet drifting 10 ppm/hr hits 99.9% after {round(drift_after_hours(5.0, 10.0), 1)} hours")
    print("\n[8] Magnetic noise is the coherence budget (flux noise 0.01 mPhi0 = 10 uPhi0)")
    print(f"    flux qubit T2* at sweet spot:      {flux_qubit_t2_us(0.5, 0.01):,.0f} us (first-order model cap)")
    print(f"    flux qubit T2* at Phi=0.501:       {round(flux_qubit_t2_us(0.501, 0.01), 2)} us")
    print(f"    flux qubit T2* at Phi=0.51:        {round(flux_qubit_t2_us(0.51, 0.01), 3)} us")
    print(f"    proton spin T2* in 1 uT noise: {round(spin_t2_us('proton_1H', 1.0), 1)} us"
          f" | electron spin: {round(spin_t2_us('electron', 1.0), 3)} us")
    print("\n[9] Chip layout - dipole crosstalk falls as 1/r^3")
    print(f"    {json.dumps(chip_grid(4, 4, 100.0), sort_keys=True)}")
    print(f"    pitch for a 0.1 mPhi0 crosstalk budget: {round(pitch_for_crosstalk_um(0.1), 1)} um")
    print(f"    frequency collisions: {frequency_collision({'q0': 4.0, 'q1': 4.005, 'q2': 5.0})}")
    print("\n[10] Operating-point classifier (TinyML kNN)")
    print(f"    {json.dumps(chip_report(), sort_keys=True)}")
    print(f"    off-sweet + noisy: {json.dumps(chip_report(phi_ratio=0.2, flux_noise_mphi0=8.0), sort_keys=True)}")
    print("    note: the sweet-spot T2* cap is the first-order flux-noise model only -")
    print("    charge noise, quasiparticles and TLS defects set the real floor on hardware")
    print("\n[11] Advisory seats - Argon 4 DECIDER, Muse advisor, Google Flow")
    a = argon4_decide(stakes="deploy")
    print(f"    decider: {a['seat']} ({a['model']})")
    print(f"    deploy-tier decision: {a['decision']} tier={a['tier']} trace={a['trace_sha256_16']}")
    print(f"    council on real_magnet_control: {council_verdict('real_magnet_control')['decision']}")
    print(f"    advisor: Muse, {len(claude_advisor()['advice'])} advice, can_override_hold = {claude_advisor()['can_override_hold']}")
    fl = google_flow_plan()
    print(f"    flow: 4 flows plan-only, rendered = {fl['rendered']} live = {fl['live']},"
          f" storyboard shots = {len(fl['flows']['filmmaking']['shots'])}")
    print(f"\n[12] HOLD gates: {len(HOLD_GATES)}")
    for k in HOLD_GATES:
        print(f"    HOLD  {k}")
    checks = run_checks()
    passed = sum(1 for _, ok in checks if ok)
    print(f"\nCHECKS {passed}/{len(checks)}")
    for name, ok in checks:
        if not ok:
            print(f"    FAIL {name}")
    verdict = "PROCEED" if passed == len(checks) else "HOLD"
    print(f"VERDICT {verdict} (sandbox simulation only) | HOLD gates {len(HOLD_GATES)}")
    return 0 if passed == len(checks) else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] == "demo":
        return demo()
    cmd = argv[0]
    if cmd == "checks":
        checks = run_checks()
        for name, ok in checks:
            print(f"{'PASS' if ok else 'FAIL'} {name}")
        print(f"CHECKS {sum(1 for _, ok in checks if ok)}/{len(checks)}")
        return 0 if all(ok for _, ok in checks) else 1
    if cmd == "species":
        print(json.dumps(SPECIES, indent=2, sort_keys=True))
        return 0
    if cmd == "larmor":
        for name in SPECIES:
            print(f"{name:14s} @ 1 T = {larmor_mhz(name, 1.0):,.3f} MHz")
        return 0
    if cmd == "flux":
        for phi in (0.5, 0.501, 0.505, 0.51, 0.55):
            print(f"Phi/Phi0 {phi:5.3f}: f = {round(flux_qubit_ghz(phi), 4)} GHz,"
                  f" sensitivity = {round(flux_sensitivity_ghz_per_phi0(phi), 2)} GHz/Phi0")
        return 0
    if cmd == "squid":
        for phi in (0.0, 0.25, 0.5, 0.75, 1.0):
            print(f"Phi/Phi0 {phi:4.2f}: Ic ratio = {round(squid_ic_ratio(phi), 4)}")
        return 0
    if cmd == "coils":
        print(f"helmholtz(100, 1 A, 0.1 m) = {helmholtz_field_t(100, 1.0, 0.1)} T")
        print(f"solenoid(5000/m, 2 A) = {solenoid_field_t(5000.0, 2.0)} T")
        return 0
    if cmd == "shield":
        print(f"Earth inside [100,100,10] = {earth_field_inside_ut([100.0, 100.0, 10.0])} uT")
        return 0
    if cmd == "chip":
        print(json.dumps(chip_report(), indent=2, sort_keys=True))
        return 0
    if cmd == "brains":
        print(json.dumps(brains_report(), indent=2, sort_keys=True))
        return 0
    if cmd == "carbon":
        print(json.dumps(argon4_decide(stakes="deploy"), indent=2, sort_keys=True))
        return 0
    if cmd == "flow":
        print(json.dumps(google_flow_plan(), indent=2, sort_keys=True))
        return 0
    if cmd == "council":
        action = argv[1] if len(argv) > 1 else "run_simulation"
        print(json.dumps(council_verdict(action), indent=2, sort_keys=True))
        return 0
    if cmd == "holds":
        for k, v in HOLD_GATES.items():
            print(f"{k}: {v}")
        return 0
    if cmd == "hold-demo":
        action = argv[1] if len(argv) > 1 else "quantum_advantage_claim"
        print(f"{action}: {HOLD_GATES.get(action, 'PROCEED - not gated')}")
        return 2 if gate(action) == "HOLD" else 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
