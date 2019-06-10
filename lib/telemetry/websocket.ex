defmodule Telemetry.Websocket do
  @behaviour :cowboy_websocket

  require Logger

  def init(req, :all) do
    {:cowboy_websocket, req, {:pubsub, MapSet.new()}, %{idle_timeout: :infinity}}
  end

  def init(req, :node) do
    id = Map.get(req.bindings, :id)
    {:cowboy_websocket, req, {:node, id}, %{idle_timeout: :infinity}}
  end

  def init(req, :transmitter) do
    id = Map.get(req.bindings, :id)
    {:cowboy_websocket, req, {:transmitter, id}, %{idle_timeout: :infinity}}
  end

  def websocket_init(state) do

    case state do
      {type, id} ->
        :gproc.reg({:p, :l, state})

        result = Telemetry.Database.lookup({type, id})

        if result do
          {:reply, {:text, Poison.encode!(result)}, state}
        else
          {:reply, {:text, "{}"}, state}
        end

      _ ->
        {:ok, state}
    end
  end

  def websocket_handle({:text, message}, state) do
    json = Poison.decode!(message)
    websocket_handle({:json, json}, state)
  end

  def websocket_handle({:json, data}, state) do
    case state do
      {:pubsub, subscribed} ->
        states = Map.get(data, "subscribe", [])
        |> Enum.map(fn call ->
          result = Telemetry.Database.lookup({:transmitter, call})

          if result do
            {:text, Poison.encode!(result)}
          end
        end)
        |> Enum.reject(&is_nil/1)

        subscribed = MapSet.new(Map.get(data, "subscribe", []))
        |> MapSet.difference(subscribed)
        |> Enum.map(fn call ->
          try do
            :gproc.reg({:p, :l, {:transmitter, call}})
            call
          rescue
            ArgumentError -> ()
          end
        end)
        |> MapSet.new()
        |> MapSet.union(subscribed)

        unsubscribed = MapSet.new(Map.get(data, "unsubscribe", []))
        |> MapSet.intersection(subscribed)
        |> Enum.map(fn call ->
          try do
            :gproc.unreg({:p, :l, {:transmitter, call}})
            call
          rescue
            ArgumentError -> ()
          end
        end)
        |> MapSet.new()

        subscribed = MapSet.difference(subscribed, unsubscribed)

        replies = [{:text, Poison.encode!(%{subscribed: subscribed})}] ++ states

        IO.inspect replies

        {:reply, replies, {:pubsub, subscribed}}
      _ ->
        {:reply, {:text, "{}"}, state}
    end
  end

  def websocket_info({:text, data}, state) do
    {:reply, {:text, data}, state}
  end

  def websocket_info(info, state) do
    {:ok, state}
  end

  def terminate(_reason, _req, _state) do
    :ok
  end
end
