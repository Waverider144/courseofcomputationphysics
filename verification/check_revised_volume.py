"""Check selected mathematical identities in the revised Volume I.

Run from the repository root with Python 3 and NumPy.
"""
from pathlib import Path
import argparse
import itertools
import json
import math
import re
import subprocess
import xml.etree.ElementTree as ET

import numpy as np
from numpy.polynomial.legendre import Legendre, leggauss
from numpy.polynomial.laguerre import laggauss


ROOT = Path(__file__).resolve().parents[1]


def close(actual, expected, atol=3e-10):
    np.testing.assert_allclose(actual, expected, rtol=3e-10, atol=atol)


def modal_matrices(p):
    basis = [Legendre.basis(i) for i in range(p + 1)]
    derivative = np.zeros((p + 1, p + 1))
    for j, phi in enumerate(basis):
        coeff = phi.deriv().coef
        derivative[:len(coeff), j] = coeff
    mass = np.diag(2.0 / (2 * np.arange(p + 1) + 1))
    trace = np.array([[phi(-1) for phi in basis], [phi(1) for phi in basis]])
    return basis, derivative, mass, trace


def check_vcjh():
    cases = 0
    for p in range(1, 6):
        basis, derivative, mass, trace = modal_matrices(p)
        boundary = np.diag([-1.0, 1.0])
        close(mass @ derivative + derivative.T @ mass, trace.T @ boundary @ trace)
        leading = math.factorial(2 * p) / (2**p * math.factorial(p)**2)
        scale = (2 * p + 1) * (leading * math.factorial(p))**2
        lower = -2.0 / scale
        for eta in (0.0, p/(p + 1), (p + 1)/p, -0.5):
            c = 2 * eta / scale
            assert c > lower
            top = np.linalg.matrix_power(derivative, p)
            correction = (c / 2) * top.T @ mass @ top
            energy = mass + correction
            assert np.linalg.eigvalsh(energy).min() > 0
            combination = (eta * Legendre.basis(p - 1) + Legendre.basis(p + 1))/(1 + eta)
            left = ((-1)**p / 2) * (basis[p] - combination)
            right = 0.5 * (basis[p] + combination)
            close([left(-1), left(1), right(-1), right(1)], [1, 0, 0, 1])
            lift = np.column_stack([left.deriv().coef, right.deriv().coef])
            close(energy @ lift, trace.T @ boundary)
            close(correction @ derivative, np.zeros_like(mass))
            close(lift, np.linalg.solve(energy, trace.T @ boundary))
            for speed in (1.3, -0.7):
                rng = np.random.default_rng(100 + p)
                states = rng.normal(size=(4, p + 1))
                traces = states @ trace.T
                left_states = traces[:, 1]
                right_states = np.roll(traces[:, 0], -1)
                jump = right_states - left_states
                flux = speed*(left_states + right_states)/2 - abs(speed)*jump/2
                jacs = np.array([0.3, 0.4, 0.6, 0.7])
                rates = []
                for j, u in enumerate(states):
                    face_flux = np.array([flux[(j-1) % 4], flux[j]])
                    rate = (-speed*derivative @ u - lift @ (face_flux - speed*trace @ u))/jacs[j]
                    rates.append(rate)
                    if eta == 0:
                        stiffness = derivative.T @ mass
                        weak_rate = np.linalg.solve(mass, speed*stiffness @ u
                                                    - trace.T @ boundary @ face_flux)/jacs[j]
                        close(rate, weak_rate)
                change = sum(jac * u @ energy @ rate for jac, u, rate in zip(jacs, states, rates))
                close(change, -abs(speed)*np.sum(jump**2)/2)
            cases += 1
    return cases


def check_mortar():
    x, w = leggauss(6)
    bm = np.array([Legendre.basis(k)(x) for k in range(3)]).T
    mass_m = bm.T @ (w[:, None]*bm)
    left = bm.copy()
    right = bm[:, :2]
    projections = [np.linalg.solve(mass_m, bm.T @ (w[:, None]*b)) for b in (left, right)]
    for b, proj in zip((left, right), projections):
        const = np.zeros(b.shape[1]); const[0] = 1
        close(proj @ const, [1, 0, 0])
        close(proj.T @ mass_m @ proj, b.T @ (w[:, None]*b))
    u_l, u_r = np.array([1.0, .3, -.2]), np.array([.8, -.1])
    l_m, r_m = projections[0] @ u_l, projections[1] @ u_r
    jump = r_m - l_m
    speed = 1.4
    flux = speed*(l_m+r_m)/2 - abs(speed)*jump/2
    loads = [projections[0].T @ mass_m @ flux, -projections[1].T @ mass_m @ flux]
    close(loads[0][0] + loads[1][0], 0)
    interface_energy = jump @ mass_m @ flux - speed*(r_m @ mass_m @ r_m-l_m @ mass_m @ l_m)/2
    close(interface_energy, -abs(speed)*jump @ mass_m @ jump/2)
    coarse_integral = 0.0
    coarse_mass = 0.0
    # Two subfaces use their own physical measure, J=1/2.
    for midpoint in (-0.5, 0.5):
        physical = midpoint + 0.5*x
        polynomial = 1 + physical + physical**2
        coarse_integral += np.sum(w*polynomial)*0.5
        coarse_mass += np.sum(w)*0.5
    close(coarse_integral, 8/3)
    close(coarse_mass, 2)


def check_lattice():
    for dimension in (2, 3):
        velocities = np.array(list(itertools.product((-1, 0, 1), repeat=dimension)), dtype=float)
        weights = np.prod(np.where(velocities == 0, 2/3, 1/6), axis=1)
        cs2 = 1/3
        close(weights.sum(), 1)
        close(weights @ velocities, np.zeros(dimension))
        close(np.einsum('i,ia,ib->ab', weights, velocities, velocities), cs2*np.eye(dimension))
        fourth = np.einsum('i,ia,ib,ic,id->abcd', weights, velocities, velocities, velocities, velocities)
        eye = np.eye(dimension)
        expected = cs2**2*(np.einsum('ab,cd->abcd', eye, eye)
                          + np.einsum('ac,bd->abcd', eye, eye)
                          + np.einsum('ad,bc->abcd', eye, eye))
        close(fourth, expected)
        rho = 1.2
        velocity = np.array([.03, -.02, .01][:dimension])
        cu = velocities @ velocity
        equilibrium = weights*rho*(1+cu/cs2+cu**2/(2*cs2**2)-velocity@velocity/(2*cs2))
        close(equilibrium.sum(), rho)
        close(equilibrium @ velocities, rho*velocity)
        close(np.einsum('i,ia,ib->ab', equilibrium, velocities, velocities),
              rho*cs2*np.eye(dimension)+rho*np.outer(velocity, velocity))
        dt, nu = .2, .015
        tau = nu/cs2 + dt/2
        rate = dt/tau
        close(cs2*(tau-dt/2), cs2*dt*(1/rate-.5))


def check_gyroaverage():
    # Integrate the Maxwellian perpendicular speed with x=v_perp^2/(2 theta).
    radial, radial_w = laggauss(64)
    angles = np.arange(256)*2*np.pi/256
    for b in (.1, 1.0, 4.0):
        bessel = np.cos(np.sqrt(2*b*radial)[:, None]*np.cos(angles)).mean(axis=1)
        gyro_factor = radial_w @ (bessel**2)
        close(gyro_factor, np.i0(b)*np.exp(-b), atol=2e-11)
        h_integral, susceptibility, potential = .7, 1.3, .4
        g_integral = h_integral - susceptibility*gyro_factor*potential
        close(susceptibility*potential-h_integral,
              susceptibility*(1-gyro_factor)*potential-g_integral)


def check_document():
    paths = sorted((ROOT/'vol1_revised/chapters').glob('ch*.tex'))
    assert len(paths) == 22
    docs = [p.read_text() for p in paths]
    report = []
    for i, source in enumerate(docs, 1):
        assert source.count(r'\chapter{') == 1
        for token in (r'\begin{chaptersummary}', r'\learninggoals{', r'\studyroute{'):
            assert token in source, (i, token)
        assert r'\conceptbridge{' in source or r'\begin{authornote}' in source
        assert r'\aiexercise{' in source or r'\begin{askai}' in source
        report.append({'chapter': i, 'author_notes': source.count(r'\begin{authornote}')+source.count(r'\conceptbridge{'),
                       'AI_boxes': source.count(r'\begin{askai}')+source.count(r'\aiexercise{')})
    combined = '\n'.join(docs)
    all_source = combined+(ROOT/'vol1_revised/references.tex').read_text()
    labels = re.findall(r'\\label\{([^}]+)\}', '\n'.join(docs))
    assert len(labels) == len(set(labels))
    refs = re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', '\n'.join(docs))
    assert set(refs) <= set(labels), set(refs)-set(labels)
    bibliography_keys = re.findall(r'\\bibitem\{([^}]+)\}', all_source)
    assert len(bibliography_keys) == len(set(bibliography_keys)), 'duplicate bibliography keys'
    bibliography = set(bibliography_keys)
    cited = set(k for group in re.findall(r'\\cite\{([^}]+)\}', all_source) for k in group.split(','))
    assert cited <= bibliography, cited-bibliography
    return {'chapters': report,
            'revised_author_notes': sum(r['author_notes'] for r in report),
            'revised_AI_boxes': sum(r['AI_boxes'] for r in report)}


def check_pdf(directory):
    result = {}
    for stem in ('Course_of_Computational_Physics_Vol1_Revised',):
        pdf = directory / (stem+'.pdf')
        log = directory / (stem+'.log')
        assert pdf.is_file(), pdf
        if log.is_file():
            problems = [line for line in log.read_text().splitlines()
                        if any(word in line for word in ('Overfull', 'Warning:', 'Missing character', '! '))]
            assert not problems, (stem, problems)
        subprocess.run(['qpdf', '--check', str(pdf)], check=True, capture_output=True)
        trace = subprocess.check_output(['mutool', 'draw', '-F', 'trace', '-o', '-', str(pdf)],
                                        stderr=subprocess.DEVNULL)
        document = ET.fromstring(trace)
        white_titles = 0
        for page in document.findall('page'):
            for fill in page.findall('.//fill_text'):
                glyphs = fill.findall('.//g')
                if min(map(float, fill.get('color').split())) > .95:
                    text = ''.join(g.get('unicode', '') for g in glyphs)
                    assert text in ('本章总结', '潜在认知跳跃', '你应该问AI'), (stem, page.get('number'), text)
                    white_titles += 1
                a, b, c, d, e, f = map(float, fill.get('transform').split())
                for g in glyphs:
                    x, y = float(g.get('x')), float(g.get('y'))
                    px, py = a*x+c*y+e, b*x+d*y+f
                    assert 20 < px < 575 and 20 < py < 822, (stem, page.get('number'), px, py)
        result[stem] = {'pages': len(document.findall('page')), 'white_title_runs': white_titles}
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pdf-dir', type=Path, help='Also inspect compiled PDFs and optional logs; requires qpdf and MuPDF.')
    args = parser.parse_args()
    result = check_document()
    result['VCJH_parameter_cases'] = check_vcjh()
    check_mortar()
    check_lattice()
    check_gyroaverage()
    result['mathematical_checks'] = 'PASS: DG/FR, VCJH, Mortar, LBM, gyroaveraging'
    if args.pdf_dir:
        result['PDF_checks'] = check_pdf(args.pdf_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
