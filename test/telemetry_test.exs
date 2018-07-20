defmodule TelemetryTest do
  use ExUnit.Case
  doctest Telemetry

  test "greets the world" do
    assert Telemetry.hello() == :world
  end
end
