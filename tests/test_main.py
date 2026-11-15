import math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import main as mq


def test_species_six(): assert len(mq.SPECIES) == 6
def test_phi0(): assert abs(mq.PHI0 - 2.067833848e-15) < 1e-24
def test_electron_larmor(): assert abs(mq.larmor_ghz("electron", 1.0) - 28.02495164) < 1e-9
def test_proton_larmor(): assert abs(mq.larmor_mhz("proton_1H", 1.0) - 42.57747892) < 1e-9
def test_larmor_linear(): assert mq.larmor_mhz("electron", 3.0) == 3 * mq.larmor_mhz("electron", 1.0)
def test_larmor_negative_field_rejected():
    try:
        mq.larmor_mhz("electron", -1.0); assert False
    except ValueError: pass
def test_unknown_species_rejected():
    try:
        mq.larmor_mhz("unobtainium", 1.0); assert False
    except ValueError: pass
def test_zeeman_mev_range(): assert 0.11 < mq.zeeman_splitting_mev("electron", 1.0) < 0.12
def test_zeeman_temp_range(): assert 1.3 < mq.zeeman_temp_k("electron", 1.0) < 1.4
def test_zeeman_zero_field(): assert mq.zeeman_splitting_mev("proton_1H", 0.0) == 0.0
def test_field_for_freq(): assert abs(mq.field_for_frequency_t("electron", 28.02495164) - 1.0) < 1e-9
def test_precession_t0(): assert mq.precession_prob_x_plus("electron", 1.0, 0.0) == 1.0
def test_precession_half_period():
    t = mq.larmor_period_ns("electron", 1.0) / 2.0
    assert mq.precession_prob_x_plus("electron", 1.0, t) < 1e-12
def test_precession_full_period():
    t = mq.larmor_period_ns("electron", 1.0)
    assert abs(mq.precession_prob_x_plus("electron", 1.0, t) - 1.0) < 1e-9
def test_period_zero_field_inf(): assert math.isinf(mq.larmor_period_ns("electron", 0.0))
def test_flux_roundtrip(): assert abs(mq.flux_quanta(mq.field_per_phi0_t(40.0), 40.0) - 1.0) < 1e-9
def test_flux_qubit_sweet(): assert abs(mq.flux_qubit_ghz(0.5) - 4.0) < 1e-12
def test_flux_qubit_symmetric(): assert abs(mq.flux_qubit_ghz(0.3) - mq.flux_qubit_ghz(0.7)) < 1e-9
def test_flux_qubit_monotone_to_sweet(): assert mq.flux_qubit_ghz(0.0) > mq.flux_qubit_ghz(0.25) > mq.flux_qubit_ghz(0.5)
def test_sensitivity_sweet_zero(): assert mq.flux_sensitivity_ghz_per_phi0(0.5) == 0.0
def test_sensitivity_grows(): assert mq.flux_sensitivity_ghz_per_phi0(0.0) > mq.flux_sensitivity_ghz_per_phi0(0.4) > 0.0
def test_sweet_flag(): assert mq.is_sweet_spot(0.5) and not mq.is_sweet_spot(0.49)
def test_squid_max(): assert mq.squid_ic_ratio(0.0) == 1.0
def test_squid_zero_half(): assert mq.squid_ic_ratio(0.5) < 1e-15
def test_squid_periodic(): assert abs(mq.squid_ic_ratio(2.0) - 1.0) < 1e-12
def test_squid_invert(): assert abs(mq.squid_flux_from_ic(0.0) - 0.5) < 1e-12 and mq.squid_flux_from_ic(1.0) == 0.0
def test_squid_clamps(): assert mq.squid_flux_from_ic(2.0) == 0.0
def test_helmholtz_formula(): assert abs(mq.helmholtz_field_t(1, 1.0, 1.0) - (4/5)**1.5 * mq.MU0) < 1e-15
def test_helmholtz_bad_radius():
    try:
        mq.helmholtz_field_t(1, 1.0, 0.0); assert False
    except ValueError: pass
def test_solenoid(): assert abs(mq.solenoid_field_t(1000.0, 2.0) - mq.MU0 * 2000.0) < 1e-15
def test_solenoid_inverse(): assert abs(mq.current_for_field_solenoid_t(1000.0, mq.solenoid_field_t(1000.0, 3.0)) - 3.0) < 1e-9
def test_gradient_scales(): assert abs(mq.gradient_addressing_mhz("proton_1H", 5.0, 30.0) - 3 * mq.gradient_addressing_mhz("proton_1H", 5.0, 10.0)) < 1e-12
def test_shield_divides(): assert mq.shielded_field_ut(50.0, 100.0) == 0.5
def test_shield_layers(): assert mq.layered_shield_factor([10.0, 100.0]) == 1000.0
def test_earth_inside(): assert abs(mq.earth_field_inside_ut([100.0, 100.0, 10.0]) - 0.0005) < 1e-12
def test_stored_energy(): assert mq.stored_energy_j(10.0, 100.0) == 50000.0
def test_magnet_linear(): assert mq.magnet_field_t(0, 250.0, 0.02) == 5.0
def test_drift(): assert mq.persistent_drift_t(5.0, 10.0, 0.0) == 5.0 and mq.persistent_drift_t(5.0, 10.0, 10.0) < 5.0
def test_drift_hours(): assert abs(mq.drift_after_hours(5.0, 10.0) - 100.0) < 1e-9
def test_drift_no_drift_inf(): assert math.isinf(mq.drift_after_hours(5.0, 0.0))
def test_quench(): assert mq.quench_temp_rise_k(50000.0, 50.0) == 5.0
def test_freq_noise_sweet_zero(): assert mq.freq_noise_from_flux_noise_hz(0.5, 5.0) == 0.0
def test_field_noise_proton(): assert abs(mq.freq_noise_from_field_noise_mhz("proton_1H", 1.0) - 42.57747892e-6) < 1e-15
def test_t2_cap(): assert mq.t2_star_us_from_freq_noise(0.0) == 1e6
def test_t2_sweet_longest(): assert mq.flux_qubit_t2_us(0.5, 1.0) > mq.flux_qubit_t2_us(0.45, 1.0) > mq.flux_qubit_t2_us(0.0, 1.0)
def test_spin_t2_species(): assert mq.spin_t2_us("proton_1H", 1.0) > mq.spin_t2_us("electron", 1.0)
def test_crosstalk_calibration(): assert mq.dipole_crosstalk_mphi0(50.0) == 1.0
def test_crosstalk_cube_law(): assert abs(mq.dipole_crosstalk_mphi0(100.0) - 0.125) < 1e-12
def test_pitch_inverse(): assert abs(mq.pitch_for_crosstalk_um(0.125) - 100.0) < 1e-9
def test_chip_grid(): g = mq.chip_grid(4, 4, 100.0); assert g["qubits"] == 16 and abs(g["area_mm2"] - 0.16) < 1e-12
def test_chip_grid_bad():
    try:
        mq.chip_grid(0, 4, 100.0); assert False
    except ValueError: pass
def test_collision(): assert mq.frequency_collision({"q0": 4.0, "q1": 4.005}) == [("q0", "q1")]
def test_collision_none(): assert mq.frequency_collision({"q0": 4.0, "q1": 4.1}) == []
def test_classifier_sweet(): assert mq.classify_point(0.5, 0.1, 0.1) == "sweet"
def test_classifier_noisy(): assert mq.classify_point(0.0, 10.0, 10.0) == "noisy"
def test_chip_report(): r = mq.chip_report(); assert r["grid"]["qubits"] == 16 and r["qubit_ghz_at_phi"] == 4.0
def test_hold_gates_17(): assert len(mq.HOLD_GATES) == 17 and all(v.startswith("HOLD") for v in mq.HOLD_GATES.values())
def test_gate_hold(): assert mq.gate("live_quantum_cloud_job") == "HOLD"
def test_gate_live_gemini_hold(): assert mq.gate("live_gemini_api_call") == "HOLD"
def test_gate_proceed(): assert mq.gate("run_simulation") == "PROCEED"
def test_argon4_identity():
    d = mq.argon4_decide()
    assert d["seat"] == "Gemini Argon 4 Extended Thinking"
    assert d["engine"] == "gemini-2.5-pro"
    assert d["model"] == "google/gemini-carbon-4-extended-pro-thinking"
    assert d["pipeline"] == ["MAP", "MODEL", "STRESS", "DECIDE"]
def test_argon4_tiers():
    assert mq.argon4_decide(stakes="standard")["tier"] == 2048
    assert mq.argon4_decide(stakes="high")["tier"] == 8192
    assert mq.argon4_decide(stakes="deploy")["tier"] == 32768
def test_argon4_bad_tier():
    try:
        mq.argon4_decide(stakes="ultra"); assert False
    except ValueError: pass
def test_argon4_decisions():
    assert mq.argon4_decide("run_simulation")["decision"].startswith("PROCEED")
    assert mq.argon4_decide("real_magnet_control")["decision"] == "HOLD"
    assert mq.argon4_decide()["can_override_hold"] is False and mq.argon4_decide()["live_calls"] == 0
    assert len(mq.argon4_decide()["trace_sha256_16"]) == 16
def test_carbon4_alias(): assert mq.carbon4_decide()["seat"] == "Gemini Argon 4 Extended Thinking"
def test_claude_advisor_full():
    a = mq.claude_advisor()
    assert len(a["advice"]) == 4 and a["models"] == ["muse-spark-1.1", "muse-wonder-1.0"]
    assert a["can_override_hold"] is False and a["authority"].startswith("none")
def test_flow_four_flows():
    f = mq.google_flow_plan()
    assert sorted(f["flows"]) == ["datax", "filmmaking", "flowx", "workspace_studio"]
    assert len(f["flows"]["filmmaking"]["shots"]) == 5 and len(f["flows"]["flowx"]["steps"]) == 8
    assert f["rendered"] is False and f["live"] == 0
    assert f["flows"]["workspace_studio"]["sent"] is False and f["flows"]["flowx"]["executed"] is False
def test_council_verdicts():
    assert mq.council_verdict("run_simulation")["decision"].startswith("PROCEED")
    v = mq.council_verdict("real_chip_fabrication")
    assert v["decision"] == "HOLD" and v["gate"] == "HOLD" and v["tier"] == 32768
    assert v["advisor_advice_count"] == 4 and v["flow_rendered"] is False
def test_brains_no_override():
    b = mq.brains_report()
    assert b["decider"]["can_override_hold"] is False and b["advisor"]["can_override_hold"] is False
    assert b["flow"]["rendered"] is False and b["flow"]["live"] == 0
def test_checks_all_pass():
    checks = mq.run_checks()
    assert all(ok for _, ok in checks) and len(checks) == 72
