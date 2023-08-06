#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `vector_demo` package."""

import pytest
from vector_demo import Vector


import pytest


@pytest.fixture()
def setup_vectors():
    """Returns a list containing three Vector instances"""
    v1 = Vector(1, {1: 3, 2: 0, 5: 1})
    v2 = Vector(2, {1: 2, 3: 6, 5: 4})
    v3 = Vector(3, {1: 2, 3: 6, 8: 'ad'})
    v4 = Vector(4, {})
    v5 = Vector(5, {1: 3, 2: 0, 3: 1})
    v6 = Vector(6, {1: 3, 2: 1, 3: 1})

    return [v1, v2, v3, v4,v5,v6]


def test_magnitude(setup_vectors):
    vectors = setup_vectors
    assert vectors[0].magnitude() == 3.1622776601683795


def test_dot_product(setup_vectors):
    vectors = setup_vectors
    assert vectors[0].dot_product(vectors[1]) == 10


def test_magnitude_type_error(setup_vectors):
    with pytest.raises(TypeError):
        vectors = setup_vectors
        vectors[2].magnitude()


def test_magnitude_empty_vector(setup_vectors):
    with pytest.raises(ValueError):
        vectors = setup_vectors
        vectors[3].magnitude()


def test_dot_product_empty_vector(setup_vectors):
    with pytest.raises(ValueError):
        vectors = setup_vectors
        vectors[3].dot_product(vectors[1])


def test_cosine_angle(setup_vectors):
    vectors = setup_vectors
    assert vectors[4].cosine_of_angle(vectors[5]) == 0.9534625892455924


def test_angle_rad(setup_vectors):
    vectors = setup_vectors
    assert vectors[4].angle(vectors[5]) == 0.30627736916966936


def test_angle_deg(setup_vectors):
    vectors = setup_vectors
    assert vectors[4].angle(vectors[5], 'deg') == 17.548400613792293


def test_angle_exception(setup_vectors):
    with pytest.raises(ValueError):
        vectors = setup_vectors
        vectors[4].angle(vectors[5], 'pasta')
