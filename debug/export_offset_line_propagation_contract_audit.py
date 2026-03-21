
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

C0 = 343.0
P_REF = 20.0e-6


@dataclass(frozen=True)
class Convention:
    name: str
    front_from: str
    mouth_from: str
    front_sign: int
    mouth_sign: int


@dataclass(frozen=True)
class MixResult:
    label: str
    crossover_hz: float | None
    front: np.ndarray
    mouth: np.ndarray
    sum: np.ndarray
    matrices: dict[str, np.ndarray]


def _candidate_repo_roots(start: Path) -> list[Path]:
    candidates: list[Path] = []
    for p in [start, *start.parents]:
        if (p / 'src' / 'os_lem').exists():
            candidates.append(p)
    uniq: list[Path] = []
    seen: set[Path] = set()
    for p in candidates:
        rp = p.resolve()
        if rp not in seen:
            uniq.append(rp)
            seen.add(rp)
    return uniq


def _validate_frequency_axis(freq: np.ndarray) -> None:
    if freq.ndim != 1 or freq.size == 0:
        raise ValueError('frequency_hz must be a non-empty 1D column')
    if np.any(~np.isfinite(freq)):
        raise ValueError('frequency_hz contains non-finite values')
    if np.any(freq <= 0.0):
        raise ValueError('frequency_hz must be > 0')
    if np.any(np.diff(freq) <= 0.0):
        raise ValueError('frequency_hz must be strictly increasing')


def _phase_wrap_deg(diff: np.ndarray) -> np.ndarray:
    return ((diff + 180.0) % 360.0) - 180.0


def _phase_deg(series: np.ndarray) -> np.ndarray:
    return np.angle(series, deg=True)


def _spl_db(series: np.ndarray) -> np.ndarray:
    return 20.0 * np.log10(np.maximum(np.abs(series), 1.0e-30) / P_REF)


def _phase_metrics(sim_deg: np.ndarray, ref_deg: np.ndarray) -> dict[str, float]:
    mask = np.isfinite(sim_deg) & np.isfinite(ref_deg)
    if not np.any(mask):
        return {'count': 0, 'mae': float('nan'), 'rmse': float('nan'), 'max_abs_error': float('nan')}
    diff = _phase_wrap_deg(sim_deg[mask] - ref_deg[mask])
    return {
        'count': int(mask.sum()),
        'mae': float(np.mean(np.abs(diff))),
        'rmse': float(np.sqrt(np.mean(diff * diff))),
        'max_abs_error': float(np.max(np.abs(diff))),
    }


def _metrics(sim: np.ndarray, ref: np.ndarray) -> dict[str, float]:
    mask = np.isfinite(sim) & np.isfinite(ref)
    if not np.any(mask):
        return {'count': 0, 'mae': float('nan'), 'rmse': float('nan'), 'max_abs_error': float('nan')}
    diff = sim[mask] - ref[mask]
    return {
        'count': int(mask.sum()),
        'mae': float(np.mean(np.abs(diff))),
        'rmse': float(np.sqrt(np.mean(diff * diff))),
        'max_abs_error': float(np.max(np.abs(diff))),
    }


def _complex_rel_rmse(sim: np.ndarray, ref: np.ndarray) -> float:
    mask = np.isfinite(sim) & np.isfinite(ref)
    if not np.any(mask):
        return float('nan')
    num = np.sqrt(np.mean(np.abs(sim[mask] - ref[mask]) ** 2))
    den = np.sqrt(np.mean(np.abs(ref[mask]) ** 2))
    if den <= 0.0:
        return float('nan')
    return float(num / den)


def _load_frd(path: Path) -> dict[str, np.ndarray]:
    lines = path.read_text(encoding='utf-8', errors='replace').splitlines()
    header_idx = None
    header = None
    for i, line in enumerate(lines):
        if 'Freq' in line and 'SPL' in line and 'WPhase' in line:
            header_idx = i
            header = [c.strip() for c in re.split(r'\t+', line.strip()) if c.strip()]
            break
    if header_idx is None or header is None:
        raise ValueError(f'Could not find FRD header in {path}')
    cols = {name: [] for name in header}
    for line in lines[header_idx + 1 :]:
        raw = line.strip()
        if not raw:
            continue
        parts = [c.strip() for c in re.split(r'\t+', raw) if c.strip()]
        if len(parts) != len(header):
            continue
        try:
            vals = [float(p) for p in parts]
        except ValueError:
            continue
        for key, val in zip(header, vals):
            cols[key].append(val)
    freq = np.asarray(cols['Freq (hertz)'], dtype=float)
    spl_db = np.asarray(cols['SPL (dB)'], dtype=float)
    phase_deg = np.asarray(cols['WPhase (deg)'], dtype=float)
    _validate_frequency_axis(freq)
    mag_pa = P_REF * np.power(10.0, spl_db / 20.0)
    complex_pa = mag_pa * np.exp(1j * np.deg2rad(phase_deg))
    return {'frequency_hz': freq, 'spl_db': spl_db, 'phase_deg': phase_deg, 'complex_pa': complex_pa}


def _normalize_series_phase_reference(series: np.ndarray, freqs_hz: np.ndarray, distance_m: float) -> np.ndarray:
    kd = 2.0 * np.pi * freqs_hz * distance_m / C0
    return series * np.exp(1j * kd)


def _conventions() -> dict[str, Convention]:
    items = [
        Convention('direct', 'drv', 'port', +1, +1),
        Convention('direct_drv_flip', 'drv', 'port', -1, +1),
        Convention('direct_port_flip', 'drv', 'port', +1, -1),
        Convention('direct_both_flip', 'drv', 'port', -1, -1),
        Convention('swapped', 'port', 'drv', +1, +1),
        Convention('swapped_drv_flip', 'port', 'drv', -1, +1),
        Convention('swapped_port_flip', 'port', 'drv', +1, -1),
        Convention('swapped_both_flip', 'port', 'drv', -1, -1),
    ]
    return {c.name: c for c in items}


def _apply_convention(convention: Convention, hr_drv: np.ndarray, hr_port: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    src = {'drv': hr_drv, 'port': hr_port}
    front = convention.front_sign * src[convention.front_from]
    mouth = convention.mouth_sign * src[convention.mouth_from]
    return front, mouth, front + mouth


def _fit_complex_matrix(os_front: np.ndarray, os_mouth: np.ndarray, hr_front: np.ndarray, hr_mouth: np.ndarray, mask: np.ndarray) -> np.ndarray:
    sel = mask & np.isfinite(os_front) & np.isfinite(os_mouth) & np.isfinite(hr_front) & np.isfinite(hr_mouth)
    if not np.any(sel):
        raise ValueError('No valid samples available for complex matrix fit')
    x = np.column_stack([os_front[sel], os_mouth[sel]])
    y = np.column_stack([hr_front[sel], hr_mouth[sel]])
    coeffs, *_ = np.linalg.lstsq(x, y, rcond=None)
    return coeffs.T


def _apply_complex_matrix(matrix: np.ndarray, os_front: np.ndarray, os_mouth: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    x = np.vstack([os_front, os_mouth])
    y = matrix @ x
    return y[0, :], y[1, :]


def _matrix_summary(matrix: np.ndarray) -> dict[str, object]:
    entries = {}
    for r, row_name in enumerate(['front', 'mouth']):
        for c, col_name in enumerate(['front', 'mouth']):
            z = matrix[r, c]
            entries[f'{row_name}_from_{col_name}'] = {
                'real': float(np.real(z)),
                'imag': float(np.imag(z)),
                'magnitude': float(np.abs(z)),
                'magnitude_db': float(20.0 * np.log10(max(abs(z), 1.0e-30))),
                'phase_deg': float(np.angle(z, deg=True)),
            }
    s = np.linalg.svd(matrix, compute_uv=False)
    return {'entries': entries, 'singular_values': [float(v) for v in s], 'condition_number': float(s[0] / s[-1]) if s[-1] > 0.0 else float('inf')}


def _band_masks(freqs: np.ndarray, hf_min_hz: float) -> dict[str, np.ndarray]:
    return {'all': np.isfinite(freqs), 'hf': freqs >= hf_min_hz}


def _fit_two_band(os_front: np.ndarray, os_mouth: np.ndarray, hr_front: np.ndarray, hr_mouth: np.ndarray, freqs: np.ndarray, crossover_hz: float) -> MixResult:
    low_mask = freqs < crossover_hz
    high_mask = freqs >= crossover_hz
    if low_mask.sum() < 4 or high_mask.sum() < 4:
        raise ValueError(f'Insufficient points for crossover {crossover_hz}')
    low_matrix = _fit_complex_matrix(os_front, os_mouth, hr_front, hr_mouth, low_mask)
    high_matrix = _fit_complex_matrix(os_front, os_mouth, hr_front, hr_mouth, high_mask)
    fit_front = np.empty_like(os_front)
    fit_mouth = np.empty_like(os_mouth)
    lf, lm = _apply_complex_matrix(low_matrix, os_front[low_mask], os_mouth[low_mask])
    hf, hm = _apply_complex_matrix(high_matrix, os_front[high_mask], os_mouth[high_mask])
    fit_front[low_mask], fit_mouth[low_mask] = lf, lm
    fit_front[high_mask], fit_mouth[high_mask] = hf, hm
    return MixResult(label=f'two_band_{int(round(crossover_hz))}Hz', crossover_hz=float(crossover_hz), front=fit_front, mouth=fit_mouth, sum=fit_front + fit_mouth, matrices={'low': low_matrix, 'high': high_matrix})


def _fit_global_phase_scalar(sim: np.ndarray, ref: np.ndarray, mask: np.ndarray) -> complex:
    sel = mask & np.isfinite(sim) & np.isfinite(ref)
    if not np.any(sel):
        return 1.0 + 0.0j
    z = np.vdot(sim[sel], ref[sel])
    if abs(z) <= 0.0:
        return 1.0 + 0.0j
    return z / abs(z)


def _apply_delay(series: np.ndarray, freqs: np.ndarray, tau_s: float) -> np.ndarray:
    return series * np.exp(-1j * 2.0 * np.pi * freqs * tau_s)


def _plot_residual(path: Path, freqs: np.ndarray, raw_residual: np.ndarray, two_band_residual: np.ndarray, fit_residual: np.ndarray, ylabel: str, title: str) -> None:
    plt.figure(figsize=(10, 6))
    plt.semilogx(freqs, raw_residual, label='raw')
    plt.semilogx(freqs, two_band_residual, label='after best two-band 2x2 complex mix')
    plt.semilogx(freqs, fit_residual, label='after best propagation-contract fit')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True, which='both', alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def main() -> int:
    here = Path(__file__).resolve()
    repo_candidates = _candidate_repo_roots(here.parent)
    if not repo_candidates:
        raise SystemExit('Could not locate repo root containing src/os_lem')
    repo_root = repo_candidates[0]
    if str(repo_root / 'src') not in sys.path:
        sys.path.insert(0, str(repo_root / 'src'))
    from os_lem.assemble import assemble_system
    from os_lem.parser import load_and_normalize
    from os_lem.solve import radiator_observation_pressure, solve_frequency_sweep

    parser = argparse.ArgumentParser(description='Audit whether a physically constrained propagation-distance contract after best two-band basis mixing explains more of the remaining offset-line mismatch.')
    parser.add_argument('--model', default=str(repo_root / 'examples' / 'offset_line_minimal' / 'model.yaml'))
    parser.add_argument('--sum-frd', default=str(repo_root / 'debug' / 'hornresp_offset_line_sum.frd'))
    parser.add_argument('--drv-frd', default=str(repo_root / 'debug' / 'hornresp_offset_line_drv.frd'))
    parser.add_argument('--port-frd', default=str(repo_root / 'debug' / 'hornresp_offset_line_port.frd'))
    parser.add_argument('--outdir', default=str(repo_root / 'debug' / 'offset_line_propagation_contract_audit_out'))
    parser.add_argument('--convention', default='direct_both_flip', choices=sorted(_conventions().keys()))
    parser.add_argument('--radiation-space', default='2pi')
    parser.add_argument('--phase-reference-distance-m', type=float, default=1.0)
    parser.add_argument('--hf-min-hz', type=float, default=1000.0)
    parser.add_argument('--crossovers-hz', default='75,100,150,200,300,500,800,1000,1500,2000')
    args = parser.parse_args()

    candidate_crossovers = [float(x.strip()) for x in args.crossovers_hz.split(',') if x.strip()]
    if not candidate_crossovers:
        raise ValueError('Need at least one crossover candidate')

    sum_frd = _load_frd(Path(args.sum_frd))
    drv_frd = _load_frd(Path(args.drv_frd))
    port_frd = _load_frd(Path(args.port_frd))
    freqs = sum_frd['frequency_hz']
    for name, frd in {'drv': drv_frd, 'port': port_frd}.items():
        if frd['frequency_hz'].shape != freqs.shape or not np.allclose(frd['frequency_hz'], freqs, rtol=0, atol=1e-9):
            raise ValueError(f'{name} FRD frequency axis does not match sum FRD')

    model, warnings = load_and_normalize(Path(args.model))
    system = assemble_system(model)
    sweep = solve_frequency_sweep(model, system, freqs)

    p_front = radiator_observation_pressure(sweep, system, 'front_rad', 1.0, radiation_space=args.radiation_space)
    p_mouth = radiator_observation_pressure(sweep, system, 'mouth_rad', 1.0, radiation_space=args.radiation_space)
    os_front = _normalize_series_phase_reference(p_front, freqs, args.phase_reference_distance_m)
    os_mouth = _normalize_series_phase_reference(p_mouth, freqs, args.phase_reference_distance_m)
    os_sum = os_front + os_mouth

    convention = _conventions()[args.convention]
    hr_front, hr_mouth, hr_sum = _apply_convention(convention, drv_frd['complex_pa'], port_frd['complex_pa'])

    masks = _band_masks(freqs, args.hf_min_hz)
    single_matrix = _fit_complex_matrix(os_front, os_mouth, hr_front, hr_mouth, masks['all'])

    best_mix = None
    best_score = float('inf')
    for crossover in candidate_crossovers:
        mix = _fit_two_band(os_front, os_mouth, hr_front, hr_mouth, freqs, crossover)
        score = (
            _metrics(_spl_db(mix.front[masks['hf']]), _spl_db(hr_front[masks['hf']]))['mae']
            + _metrics(_spl_db(mix.mouth[masks['hf']]), _spl_db(hr_mouth[masks['hf']]))['mae']
            + _metrics(_spl_db(mix.sum[masks['hf']]), _spl_db(hr_sum[masks['hf']]))['mae']
        ) / 3.0
        if score < best_score:
            best_score = score
            best_mix = mix
    assert best_mix is not None

    tau_ref = args.phase_reference_distance_m / C0
    hypotheses = [
        ('none', 0.0, 0.0),
        ('mouth_plus_refdist', 0.0, +tau_ref),
        ('mouth_minus_refdist', 0.0, -tau_ref),
        ('front_plus_refdist', +tau_ref, 0.0),
        ('front_minus_refdist', -tau_ref, 0.0),
        ('both_plus_refdist', +tau_ref, +tau_ref),
        ('both_minus_refdist', -tau_ref, -tau_ref),
    ]

    ranked = []
    best_payload = None
    best_payload_score = float('inf')
    for label, tau_front, tau_mouth in hypotheses:
        fit_front = _apply_delay(best_mix.front.copy(), freqs, tau_front)
        fit_mouth = _apply_delay(best_mix.mouth.copy(), freqs, tau_mouth)
        alpha = _fit_global_phase_scalar(fit_front + fit_mouth, hr_sum, masks['hf'])
        fit_front *= alpha
        fit_mouth *= alpha
        fit_sum = fit_front + fit_mouth
        row = {
            'hypothesis': label,
            'tau_front_ms': float(1e3 * tau_front),
            'tau_mouth_ms': float(1e3 * tau_mouth),
            'front_distance_offset_m': float(tau_front * C0),
            'mouth_distance_offset_m': float(tau_mouth * C0),
            'global_phase_deg': float(np.angle(alpha, deg=True)),
            'front_hf_phase_mae_deg': _phase_metrics(_phase_deg(fit_front[masks['hf']]), _phase_deg(hr_front[masks['hf']]))['mae'],
            'mouth_hf_phase_mae_deg': _phase_metrics(_phase_deg(fit_mouth[masks['hf']]), _phase_deg(hr_mouth[masks['hf']]))['mae'],
            'sum_hf_spl_mae_db': _metrics(_spl_db(fit_sum[masks['hf']]), _spl_db(hr_sum[masks['hf']]))['mae'],
            'sum_hf_phase_mae_deg': _phase_metrics(_phase_deg(fit_sum[masks['hf']]), _phase_deg(hr_sum[masks['hf']]))['mae'],
            'sum_hf_complex_rel_rmse': _complex_rel_rmse(fit_sum[masks['hf']], hr_sum[masks['hf']]),
            'front': fit_front,
            'mouth': fit_mouth,
            'sum': fit_sum,
        }
        ranked.append(row)
        if row['sum_hf_complex_rel_rmse'] < best_payload_score:
            best_payload_score = row['sum_hf_complex_rel_rmse']
            best_payload = row
    assert best_payload is not None

    def align_row(raw, two_band, fit, ref, mask):
        return {
            'raw_spl_mae_db': _metrics(_spl_db(raw[mask]), _spl_db(ref[mask]))['mae'],
            'raw_phase_mae_deg': _phase_metrics(_phase_deg(raw[mask]), _phase_deg(ref[mask]))['mae'],
            'raw_complex_rel_rmse': _complex_rel_rmse(raw[mask], ref[mask]),
            'two_band_spl_mae_db': _metrics(_spl_db(two_band[mask]), _spl_db(ref[mask]))['mae'],
            'two_band_phase_mae_deg': _phase_metrics(_phase_deg(two_band[mask]), _phase_deg(ref[mask]))['mae'],
            'two_band_complex_rel_rmse': _complex_rel_rmse(two_band[mask], ref[mask]),
            'contract_spl_mae_db': _metrics(_spl_db(fit[mask]), _spl_db(ref[mask]))['mae'],
            'contract_phase_mae_deg': _phase_metrics(_phase_deg(fit[mask]), _phase_deg(ref[mask]))['mae'],
            'contract_complex_rel_rmse': _complex_rel_rmse(fit[mask], ref[mask]),
        }

    alignment = {
        'front_all': align_row(os_front, best_mix.front, best_payload['front'], hr_front, masks['all']),
        'front_hf': align_row(os_front, best_mix.front, best_payload['front'], hr_front, masks['hf']),
        'mouth_all': align_row(os_mouth, best_mix.mouth, best_payload['mouth'], hr_mouth, masks['all']),
        'mouth_hf': align_row(os_mouth, best_mix.mouth, best_payload['mouth'], hr_mouth, masks['hf']),
        'sum_all': align_row(os_sum, best_mix.sum, best_payload['sum'], hr_sum, masks['all']),
        'sum_hf': align_row(os_sum, best_mix.sum, best_payload['sum'], hr_sum, masks['hf']),
    }

    summary = {
        'model': str(args.model),
        'sum_frd': str(args.sum_frd),
        'drv_frd': str(args.drv_frd),
        'port_frd': str(args.port_frd),
        'warnings': list(warnings or []),
        'points': int(freqs.size),
        'radiation_space': args.radiation_space,
        'phase_reference_distance_m': float(args.phase_reference_distance_m),
        'hf_min_hz': float(args.hf_min_hz),
        'comparison_convention': {
            'name': convention.name,
            'front_from': convention.front_from,
            'mouth_from': convention.mouth_from,
            'front_sign': convention.front_sign,
            'mouth_sign': convention.mouth_sign,
        },
        'single_band_basis_mix': _matrix_summary(single_matrix),
        'best_two_band_basis_mix': {
            'label': best_mix.label,
            'crossover_hz': best_mix.crossover_hz,
            'low_matrix': _matrix_summary(best_mix.matrices['low']),
            'high_matrix': _matrix_summary(best_mix.matrices['high']),
        },
        'propagation_hypotheses_ranked': [
            {k: v for k, v in row.items() if k not in {'front','mouth','sum'}}
            for row in sorted(ranked, key=lambda r: (r['sum_hf_complex_rel_rmse'], r['sum_hf_spl_mae_db']))
        ],
        'best_propagation_contract': {k: v for k, v in best_payload.items() if k not in {'front','mouth','sum'}},
        'alignment': alignment,
        'pm_interpretation': {
            'purpose': 'test whether a physically meaningful extra propagation-phase contract at the 1 m observation distance explains more of the remaining mismatch than two-band basis mixing alone',
            'decision_rules': {
                'mouth_plus_refdist_best': 'if mouth_plus_refdist wins, Hornresp port/mouth contribution likely carries an extra observer-distance propagation phase relative to os-lem mouth observation',
                'front_plus_refdist_best': 'if front_plus_refdist wins, front observation phase-reference mismatch remains plausible',
                'phase_beats_spl': 'if complex and phase improve more than SPL, remaining error is mainly propagation/reference-position semantics, not amplitude law',
                'little_gain': 'if no constrained propagation hypothesis helps materially, remaining gap is likely a real observable or physics mismatch',
            },
        },
    }

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    summary_json = outdir / 'offset_line_propagation_contract_audit_summary.json'
    csv_path = outdir / 'offset_line_propagation_contract_audit_metrics.csv'
    summary_json.write_text(json.dumps(summary, indent=2), encoding='utf-8')
    with csv_path.open('w', newline='', encoding='utf-8') as f:
        fieldnames = ['path','band','raw_spl_mae_db','raw_phase_mae_deg','raw_complex_rel_rmse','two_band_spl_mae_db','two_band_phase_mae_deg','two_band_complex_rel_rmse','contract_spl_mae_db','contract_phase_mae_deg','contract_complex_rel_rmse']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for key in ['front_all','front_hf','mouth_all','mouth_hf','sum_all','sum_hf']:
            row = alignment[key].copy()
            path, band = key.split('_',1)
            row['path'] = path
            row['band'] = band
            writer.writerow({k: row[k] for k in fieldnames})

    _plot_residual(outdir / 'offset_line_propagation_contract_front_phase_residual.png', freqs, _phase_wrap_deg(_phase_deg(os_front)-_phase_deg(hr_front)), _phase_wrap_deg(_phase_deg(best_mix.front)-_phase_deg(hr_front)), _phase_wrap_deg(_phase_deg(best_payload['front'])-_phase_deg(hr_front)), 'Residual (deg)', 'Offset-line front phase residual vs propagation-contract fit')
    _plot_residual(outdir / 'offset_line_propagation_contract_mouth_phase_residual.png', freqs, _phase_wrap_deg(_phase_deg(os_mouth)-_phase_deg(hr_mouth)), _phase_wrap_deg(_phase_deg(best_mix.mouth)-_phase_deg(hr_mouth)), _phase_wrap_deg(_phase_deg(best_payload['mouth'])-_phase_deg(hr_mouth)), 'Residual (deg)', 'Offset-line mouth phase residual vs propagation-contract fit')
    _plot_residual(outdir / 'offset_line_propagation_contract_sum_phase_residual.png', freqs, _phase_wrap_deg(_phase_deg(os_sum)-_phase_deg(hr_sum)), _phase_wrap_deg(_phase_deg(best_mix.sum)-_phase_deg(hr_sum)), _phase_wrap_deg(_phase_deg(best_payload['sum'])-_phase_deg(hr_sum)), 'Residual (deg)', 'Offset-line sum phase residual vs propagation-contract fit')
    _plot_residual(outdir / 'offset_line_propagation_contract_front_spl_residual.png', freqs, _spl_db(os_front)-_spl_db(hr_front), _spl_db(best_mix.front)-_spl_db(hr_front), _spl_db(best_payload['front'])-_spl_db(hr_front), 'Residual (dB)', 'Offset-line front SPL residual vs propagation-contract fit')
    _plot_residual(outdir / 'offset_line_propagation_contract_mouth_spl_residual.png', freqs, _spl_db(os_mouth)-_spl_db(hr_mouth), _spl_db(best_mix.mouth)-_spl_db(hr_mouth), _spl_db(best_payload['mouth'])-_spl_db(hr_mouth), 'Residual (dB)', 'Offset-line mouth SPL residual vs propagation-contract fit')
    _plot_residual(outdir / 'offset_line_propagation_contract_sum_spl_residual.png', freqs, _spl_db(os_sum)-_spl_db(hr_sum), _spl_db(best_mix.sum)-_spl_db(hr_sum), _spl_db(best_payload['sum'])-_spl_db(hr_sum), 'Residual (dB)', 'Offset-line sum SPL residual vs propagation-contract fit')

    payload = {
        'summary_json': str(summary_json),
        'best_crossover_hz': best_mix.crossover_hz,
        'best_hypothesis': best_payload['hypothesis'],
        'best_front_distance_offset_m': best_payload['front_distance_offset_m'],
        'best_mouth_distance_offset_m': best_payload['mouth_distance_offset_m'],
        'sum_hf_two_band_spl_mae_db': alignment['sum_hf']['two_band_spl_mae_db'],
        'sum_hf_contract_spl_mae_db': alignment['sum_hf']['contract_spl_mae_db'],
        'sum_hf_two_band_phase_mae_deg': alignment['sum_hf']['two_band_phase_mae_deg'],
        'sum_hf_contract_phase_mae_deg': alignment['sum_hf']['contract_phase_mae_deg'],
        'sum_hf_two_band_complex_rel_rmse': alignment['sum_hf']['two_band_complex_rel_rmse'],
        'sum_hf_contract_complex_rel_rmse': alignment['sum_hf']['contract_complex_rel_rmse'],
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
