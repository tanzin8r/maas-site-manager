"""Tests for database debug utilities."""

import io

from sqlalchemy import text

from msm.apiserver.db._debug import CompiledQuery, print_query


class TestCompiledQuery:
    """Test cases for CompiledQuery class."""

    def test_compiled_query_with_simple_select(self) -> None:
        """Test CompiledQuery with a simple SELECT query."""
        query = text("SELECT * FROM users WHERE id = :user_id")
        query = query.bindparams(user_id=123)

        compiled = CompiledQuery(query)

        assert "SELECT * FROM users WHERE id" in compiled.sql
        assert compiled.params == {"user_id": 123}

    def test_compiled_query_with_no_params(self) -> None:
        """Test CompiledQuery with a query that has no parameters."""
        query = text("SELECT * FROM users")

        compiled = CompiledQuery(query)

        assert "SELECT * FROM users" in compiled.sql
        assert compiled.params == {}

    def test_compiled_query_with_multiple_params(self) -> None:
        """Test CompiledQuery with multiple parameters."""
        query = text(
            "SELECT * FROM users WHERE id = :user_id AND name = :name"
        )
        query = query.bindparams(user_id=123, name="John")

        compiled = CompiledQuery(query)

        assert "SELECT * FROM users WHERE id" in compiled.sql
        assert compiled.params == {"user_id": 123, "name": "John"}


class TestPrintQuery:
    """Test cases for print_query function."""

    def test_print_query_with_params(self) -> None:
        """Test print_query outputs query and parameters."""
        query = text("SELECT * FROM users WHERE id = :user_id")
        query = query.bindparams(user_id=123)

        output = io.StringIO()
        print_query(query, file=output)
        result = output.getvalue()

        assert "---" in result
        assert "SELECT * FROM users WHERE id" in result
        assert "params:" in result
        assert "123" in result

    def test_print_query_without_params(self) -> None:
        """Test print_query outputs query without parameters."""
        query = text("SELECT * FROM users")

        output = io.StringIO()
        print_query(query, file=output)
        result = output.getvalue()

        assert "---" in result
        assert "SELECT * FROM users" in result
        # params should not be printed when there are none
        assert result.count("params:") == 0

    def test_print_query_with_complex_params(self) -> None:
        """Test print_query with complex parameter types."""
        query = text("SELECT * FROM users WHERE id = :id AND active = :active")
        query = query.bindparams(id=456, active=True)

        output = io.StringIO()
        print_query(query, file=output)
        result = output.getvalue()

        assert "---" in result
        assert "SELECT * FROM users" in result
        assert "params:" in result
        assert "456" in result
        assert "True" in result

    def test_print_query_output_format(self) -> None:
        """Test print_query output format has correct structure."""
        query = text("SELECT * FROM test WHERE x = :val")
        query = query.bindparams(val=99)

        output = io.StringIO()
        print_query(query, file=output)
        result = output.getvalue()

        lines = result.strip().split("\n")
        # Should start with ---
        assert lines[0] == "---"
        # Should have SQL query
        assert any("SELECT" in line for line in lines)
        # Should have params line
        assert any(line.startswith("params:") for line in lines)
        # Should end with ---
        assert lines[-1] == "---"
