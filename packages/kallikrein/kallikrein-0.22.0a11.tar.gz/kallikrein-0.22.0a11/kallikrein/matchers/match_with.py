from typing import TypeVar, Generic, Callable

from amino import List

from kallikrein.matcher import Matcher, BoundMatcher
from kallikrein.match_result import MatchResult, BadNestedMatch
from kallikrein import Expectation

A = TypeVar('A')
B = TypeVar('B')
success_tmpl = '`{}` matches with `{}`'
failure_tmpl = '`{}` does not match with `{}`'


class MatchWith(Generic[A, B], Matcher[B]):

    def match(self, exp: A, target: Callable[[A], Expectation[B]]) -> MatchResult[B]:
        bound = target(exp)
        return bound.match.evaluate(bound.value)

    def match_nested(self, exp: A, target: BoundMatcher) -> MatchResult[B]:
        return BadNestedMatch(target)


match_with = MatchWith()

__all__ = ('match_with',)
