"""Verify the passive boost and Maxwell signs used in Volume II."""
from collections import Counter
from itertools import combinations, permutations
from pathlib import Path
import unittest

import numpy as np

from check_english_editions import DISPLAY, INLINE, commands, math_blocks


ETA = np.diag([-1.0, 1.0, 1.0, 1.0])
EPSILON = np.zeros((4, 4, 4, 4))
for indices in permutations(range(4)):
    inversions = sum(indices[i] > indices[j] for i in range(4) for j in range(i + 1, 4))
    EPSILON[indices] = (-1.0)**inversions


def boost(v):
    gamma = 1.0/np.sqrt(1.0-v*v)
    return np.array([[gamma, -gamma*v, 0, 0],
                     [-gamma*v, gamma, 0, 0],
                     [0, 0, 1, 0], [0, 0, 0, 1]])


def field_tensor(electric, magnetic):
    ex, ey, ez = electric
    bx, by, bz = magnetic
    return np.array([[0, -ex, -ey, -ez], [ex, 0, bz, -by],
                     [ey, -bz, 0, bx], [ez, by, -bx, 0]], dtype=float)


def fields(tensor):
    return -tensor[0, 1:], np.array([tensor[2, 3], tensor[3, 1], tensor[1, 2]])


def hodge(tensor):
    return 0.5*np.einsum("mnab,ab->mn", EPSILON, ETA@tensor@ETA)


def exterior_derivative(derivatives):
    return {indices: (derivatives[indices]
                      + derivatives[indices[1], indices[2], indices[0]]
                      + derivatives[indices[2], indices[0], indices[1]])
            for indices in combinations(range(4), 3)}


def source_vector(derivatives):
    raised = np.einsum("ma,dab,bn->dmn", ETA, derivatives, ETA)
    return np.einsum("mnm->n", raised)


class LorentzCovarianceTests(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(1401)
        self.electric, self.magnetic = rng.normal(size=(2, 3))
        self.de, self.db = rng.normal(size=(2, 4, 3))
        self.tensor = field_tensor(self.electric, self.magnetic)
        self.derivatives = np.array([field_tensor(e, b)
                                     for e, b in zip(self.de, self.db)])

    def test_metric_inverse_and_passive_jacobian(self):
        for v in (-0.9, -0.6, 0.0, 0.6, 0.9):
            transform, inverse = boost(v), boost(-v)
            np.testing.assert_allclose(transform.T@ETA@transform, ETA, atol=1e-14)
            np.testing.assert_allclose(transform@inverse, np.eye(4), atol=1e-14)
            self.assertAlmostEqual(np.linalg.det(transform), 1.0)

    def test_all_six_field_components_and_inverse(self):
        ex, ey, ez = self.electric
        bx, by, bz = self.magnetic
        for v in (-0.9, -0.6, 0.0, 0.6, 0.9):
            gamma = 1.0/np.sqrt(1.0-v*v)
            inverse = boost(-v)
            transformed = inverse.T@self.tensor@inverse
            electric, magnetic = fields(transformed)
            np.testing.assert_allclose(electric, [ex, gamma*(ey-v*bz), gamma*(ez+v*by)])
            np.testing.assert_allclose(magnetic, [bx, gamma*(by+v*ez), gamma*(bz-v*ey)])
            np.testing.assert_allclose(boost(v).T@transformed@boost(v), self.tensor,
                                       atol=1e-14)

    def test_component_signs_and_index_raising(self):
        np.testing.assert_array_equal(self.tensor.T, -self.tensor)
        np.testing.assert_array_equal(self.tensor[0, 1:], -self.electric)
        raised = ETA@self.tensor@ETA
        np.testing.assert_array_equal(raised[0, 1:], self.electric)
        np.testing.assert_array_equal(raised[1:, 0], -self.electric)
        np.testing.assert_array_equal(raised[1:, 1:], self.tensor[1:, 1:])

    def test_recovery_of_all_three_dimensional_equations(self):
        curl_e = np.array([self.de[2, 2]-self.de[3, 1],
                           self.de[3, 0]-self.de[1, 2],
                           self.de[1, 1]-self.de[2, 0]])
        curl_b = np.array([self.db[2, 2]-self.db[3, 1],
                           self.db[3, 0]-self.db[1, 2],
                           self.db[1, 1]-self.db[2, 0]])
        faraday = self.db[0]+curl_e
        homogeneous = exterior_derivative(self.derivatives)
        np.testing.assert_allclose([homogeneous[0, 2, 3], -homogeneous[0, 1, 3],
                                   homogeneous[0, 1, 2]], faraday)
        self.assertAlmostEqual(homogeneous[1, 2, 3], np.trace(self.db[1:]))
        expected_source = np.r_[np.trace(self.de[1:]), curl_b-self.de[0]]
        np.testing.assert_allclose(source_vector(self.derivatives), expected_source)

    def test_covariance_of_source_equation(self):
        source = source_vector(self.derivatives)
        for v in (-0.8, 0.0, 0.8):
            inverse = boost(-v)
            transformed = np.einsum("ra,sm,tn,rst->amn", inverse, inverse, inverse,
                                    self.derivatives)
            np.testing.assert_allclose(source_vector(transformed), boost(v)@source,
                                       atol=1e-13)

    def test_covariance_of_homogeneous_equations(self):
        independent = exterior_derivative(self.derivatives)
        three_form = np.zeros((4, 4, 4))
        for indices, value in independent.items():
            for order in permutations(range(3)):
                inversions = sum(order[i] > order[j] for i in range(3)
                                 for j in range(i + 1, 3))
                three_form[tuple(indices[i] for i in order)] = (-1)**inversions*value
        for v in (-0.8, 0.8):
            inverse = boost(-v)
            transformed_derivatives = np.einsum("ra,sm,tn,rst->amn",
                                                inverse, inverse, inverse, self.derivatives)
            expected = np.einsum("ra,sb,tc,rst->abc", inverse, inverse, inverse, three_form)
            actual = exterior_derivative(transformed_derivatives)
            for indices, value in actual.items():
                self.assertAlmostEqual(value, expected[indices])

    def test_hodge_and_current_three_form_signs(self):
        star = hodge(self.tensor)
        expected_star = field_tensor(-self.magnetic, self.electric)
        np.testing.assert_array_equal(star, expected_star)
        np.testing.assert_array_equal(hodge(star), -self.tensor)
        dstar = exterior_derivative(np.array([hodge(d) for d in self.derivatives]))
        rho, jx, jy, jz = source_vector(self.derivatives)
        np.testing.assert_allclose([dstar[1, 2, 3], dstar[0, 2, 3],
                                   dstar[0, 1, 3], dstar[0, 1, 2]],
                                  [rho, -jx, jy, -jz])
        for v in (-0.8, 0.8):
            inverse = boost(-v)
            np.testing.assert_allclose(hodge(inverse.T@self.tensor@inverse),
                                       inverse.T@star@inverse, atol=1e-13)

    def test_faraday_component_under_coordinate_chain_rule(self):
        for v in (-0.8, 0.8):
            gamma = 1.0/np.sqrt(1.0-v*v)
            # Arbitrary derivatives in primed coordinates of the unprimed components.
            bz, ey, ex = self.db[:, 2], self.de[:, 1], self.de[:, 0]
            by_chain_rule = gamma*(bz[0]-v*bz[1]+ey[1]-v*ey[0])-ex[2]
            by_mixed_fields = gamma*(bz[0]-v*ey[0])+gamma*(ey[1]-v*bz[1])-ex[2]
            self.assertAlmostEqual(by_chain_rule, by_mixed_fields)

    def test_bilingual_chapter_mathematics_and_references(self):
        root = Path(__file__).resolve().parents[1]
        chapters = []
        for language in ("CN", "EN"):
            source = (root/f"CourseofComputationPhysics_Vol2_{language}.tex").read_text()
            chapters.append(source.split(r"\label{ch:lorentz}", 1)[1]
                            .split(r"\label{ch:31}", 1)[0])
        chinese, english = chapters
        self.assertEqual(math_blocks(chinese, DISPLAY), math_blocks(english, DISPLAY))
        self.assertEqual(Counter(math_blocks(chinese, INLINE)),
                         Counter(math_blocks(english, INLINE)))
        for command in ("label", "ref", "eqref", "begin", "end"):
            self.assertEqual(Counter(commands(chinese, command)),
                             Counter(commands(english, command)), command)
        self.assertEqual(chinese.count(r"\section{"), 5)
        self.assertEqual(english.count(r"\section{"), 5)


if __name__ == "__main__":
    unittest.main()
