from hypothesis.stateful import RuleBasedStateMachine, invariant, rule

from hypothesis import given, settings, assume
from hypothesis import HealthCheck

import hypothesis.strategies as st

from onset import onset as S

# specific structure for tests
intset = st.sets(st.integers())


@given(intset)
def test_union_with_empty(s):
    s_ = s.copy()
    S.union(s_, set())

    assert s_ == s


@given(intset)
def test_union_with_self(s):
    s_ = s.copy()
    S.union(s_, s)

    assert s_ == s


@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(intset, intset)
def test_union_with_subset(s, t):
    assume(s.issubset(t))

    s_ = s.copy()
    S.union(s_, t)

    assert s_ == t


@given(intset, intset)
def test_union_is_superset(s, t):
    s_ = s.copy()
    S.union(s_, t)

    assert s_.issuperset(s)


@given(intset, intset)
def test_union_is_commutative(s, t):
    s_ = s.copy()
    t_ = t.copy()
    S.union(s_, t)
    S.union(t_, s)

    assert s_ == t_


@given(intset, intset, intset)
def test_union_is_associative(s, t, r):
    s_ = s.copy()
    t_ = t.copy()

    # (s U t) U r
    S.union(s_, t)
    S.union(s_, r)

    # s U (t U r)
    S.union(t_, r)
    S.union(t_, s)

    assert s_ == t_


@given(intset)
def test_difference_on_empty(s):
    t_ = set()
    S.difference(t_, s)

    assert t_ == set()


@given(intset)
def test_difference_with_empty(s):
    s_ = s.copy()
    S.difference(s_, set())

    assert s_ == s


@given(intset)
def test_difference_with_self(s):
    s_ = s.copy()
    S.difference(s_, s)

    assert s_ == set()


@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(intset, intset)
def test_difference_with_subset(s, t):
    assume(s.issubset(t))

    s_ = s.copy()
    S.difference(s_, t)

    assert s_ == set()


@given(intset, intset)
def test_difference_not_commutative(s, t):
    assume(s != t)

    s_ = s.copy()
    t_ = t.copy()
    S.difference(s_, t)
    S.difference(t_, s)

    assert s_ != t_


@given(intset)
def test_intersection_with_empty(s):
    s_ = s.copy()
    S.intersection(s_, set())

    assert s_ == set()


@given(intset)
def test_intersection_with_self(s):
    s_ = s.copy()
    S.intersection(s_, s)

    assert s_ == s


@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(intset, intset)
def test_intersection_with_subset(s, t):
    assume(s.issubset(t))

    s_ = s.copy()
    S.intersection(s_, t)

    assert s_ == s


@given(intset, intset)
def test_intersection_is_subset(s, t):
    s_ = s.copy()
    S.intersection(s_, t)

    assert s_.issubset(s)


@given(intset, intset)
def test_intersection_is_commutative(s, t):
    s_ = s.copy()
    t_ = t.copy()
    S.intersection(s_, t)
    S.intersection(t_, s)

    assert s_ == t_


@given(intset, intset, intset)
def test_intersection_is_associative(s, t, r):
    s_ = s.copy()
    t_ = t.copy()

    # (s I t) I r
    S.intersection(s_, t)
    S.intersection(s_, r)

    # s I (t I r)
    S.intersection(t_, r)
    S.intersection(t_, s)

    assert s_ == t_


@given(intset)
def test_disjunction_with_empty(s):
    s_ = s.copy()
    S.disjunction(s_, set())

    assert s_ == s


@given(intset)
def test_disjunction_with_self(s):
    s_ = s.copy()
    S.disjunction(s_, s)

    assert s_ == set()


@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(intset, intset)
def test_disjunction_with_subset(s, t):
    assume(s.issubset(t))

    s_ = s.copy()
    t_ = t.copy()
    S.difference(t_, s)
    S.disjunction(s_, t)

    assert s_ == t_


@given(intset, intset)
def test_disjunction_is_commutative(s, t):
    s_ = s.copy()
    t_ = t.copy()
    S.disjunction(s_, t)
    S.disjunction(t_, s)

    assert s_ == t_


@given(intset, intset, intset)
def test_disjunction_is_associative(s, t, r):
    s_ = s.copy()
    t_ = t.copy()

    # (s J t) J r
    S.disjunction(s_, t)
    S.disjunction(s_, r)

    # s J (t J r)
    S.disjunction(t_, r)
    S.disjunction(t_, s)

    assert s_ == t_


class OnSet(RuleBasedStateMachine):
    s = intset.example()

    @invariant()
    def is_set(self):
        assert isinstance(self.s, set)

    @rule(t=intset)
    def union(self, t):
        return S.union(self.s, t)

    @rule(t=intset)
    def difference(self, t):
        return S.difference(self.s, t)

    @rule(t=intset)
    def intersection(self, t):
        return S.intersection(self.s, t)

    @rule(t=intset)
    def disjunction(self, t):
        return S.disjunction(self.s, t)


TestOnSet = OnSet.TestCase
