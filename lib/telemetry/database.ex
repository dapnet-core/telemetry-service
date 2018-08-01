defmodule Telemetry.Database do
  use GenServer

  def start_link do
    GenServer.start_link(__MODULE__, :ok, [name: __MODULE__])
  end

  def init(_) do
    :ets.new(:telemetry, [:set, :public, :named_table])
    {:ok, nil}
  end

  def lookup({type, id}) do
    case :ets.lookup(:telemetry, {type, id}) do
      [{_, result}] -> result
      _ -> nil
    end
  end

  def update({type, id, data}) do
    current = lookup({type, id})

    updated = if current do
      Map.merge(current, data)
    else
      data
    end

    :ets.insert(:telemetry, {{type, id}, updated})
  end
end
