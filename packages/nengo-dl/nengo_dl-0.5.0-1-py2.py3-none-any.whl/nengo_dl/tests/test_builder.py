from nengo.exceptions import BuildError
import pytest

from nengo_dl.builder import Builder, OpBuilder


def test_custom_builder():
    class TestOp(object):
        sets = None
        incs = None
        reads = None
        updates = None

    ops = (TestOp(),)

    # error if no builder registered
    with pytest.raises(BuildError):
        Builder.pre_build(ops, None, None, None)

    # error if no pre-built object
    with pytest.raises(BuildError):
        Builder.build(ops, None, {})

    # warning if builder doesn't subclass OpBuilder
    with pytest.warns(UserWarning):
        @Builder.register(TestOp)
        class TestOpBuilder0:
            pass

    # warning when overwriting a registered builder
    with pytest.warns(UserWarning):
        @Builder.register(TestOp)
        class TestOpBuilder(OpBuilder):
            pre_built = False
            pass_rng = True

            def __init__(self, ops, signals, rng=None):
                self.pre_built = True
                assert rng is not None

            def build_step(self, signals):
                assert self.pre_built

                return 0, 1

    op_builds = {}
    Builder.pre_build(ops, None, True, op_builds)

    result = Builder.build(ops, None, op_builds)

    assert len(result) == 2
    assert result[0] == 0
    assert result[1] == 1
