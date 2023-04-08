import pyarrow as pa

from quiver.tables import TableBase
from quiver.matrix import MatrixExtensionType, MatrixArray


class Position(TableBase):
    schema = pa.schema(
        [
            pa.field("x", pa.float64()),
            pa.field("y", pa.float64()),
            pa.field("cov", MatrixExtensionType((2, 2), pa.float64())),
        ]
    )


class PositionWrapper(TableBase):
    schema = pa.schema(
        [
            Position.as_field("pos"),
            pa.field("id", pa.string()),
        ]
    )


def test_matrix_from_pydict():
    data = {
        "x": [1.0, 2.0, 3.0],
        "y": [4.0, 5.0, 6.0],
        "cov": [
            [[1.0, 1.0], [1.0, 1.0]],
            [[2.0, 2.0], [2.0, 2.0]],
            [[3.0, 3.0], [3.0, 3.0]],
        ],
    }
    have = Position.from_pydict(data)
    assert len(have) == 3

    assert type(have.cov.chunks[0]) == MatrixArray


def test_matrix_from_array():
    xs = pa.array([1, 2, 3], pa.float64())
    ys = pa.array([4, 5, 6], pa.float64())
    cov = pa.array(
        [
            [[1.0, 1.0], [1.0, 1.0]],
            [[2.0, 2.0], [2.0, 2.0]],
            [[3.0, 3.0], [3.0, 3.0]],
        ],
        Position.schema.field("cov").type,
    )
    have = Position.from_arrays([xs, ys, cov])
    assert len(have) == 3

    assert type(have.cov.chunks[0]) == MatrixArray


def test_nested_matrix_from_array():
    xs = pa.array([1, 2, 3], pa.float64())
    ys = pa.array([4, 5, 6], pa.float64())
    cov = pa.array(
        [
            [[1.0, 1.0], [1.0, 1.0]],
            [[2.0, 2.0], [2.0, 2.0]],
            [[3.0, 3.0], [3.0, 3.0]],
        ],
        Position.schema.field("cov").type,
    )
    pos = pa.StructArray.from_arrays([xs, ys, cov], fields=list(Position.schema))
    ids = pa.array(["v1", "v2", "v3"], pa.string())

    have = PositionWrapper.from_arrays([pos, ids])
    assert len(have) == 3
    assert type(have.pos.cov.chunks[0]) == MatrixArray
