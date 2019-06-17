defmodule Telemetry.Websocket do
  @behaviour :cowboy_websocket

  require Logger

  def init(req, :all) do
    {:cowboy_websocket, req, {:pubsub, MapSet.new(), MapSet.new()}, %{idle_timeout: :infinity}}
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
      {:pubsub, transmitters, nodes} ->
        {subscribed_transmitters, transmitter_states} =
          pubsub(:transmitter,
            transmitters,
            Map.get(data, "subscribe_transmitters", []),
            Map.get(data, "unsubscribe_transmitters", [])
          )

        {subscribed_nodes, node_states} =
          pubsub(:node,
            nodes,
            Map.get(data, "subscribe_nodes", []),
            Map.get(data, "unsubscribe_nodes", [])
          )

        replies = [{:text, Poison.encode!(%{
                           transmitters: subscribed_transmitters,
                           nodes: subscribed_nodes,
                           "_type": "subscription"})}] ++ transmitter_states ++ node_states

        {:reply, replies, {:pubsub, subscribed_transmitters, subscribed_nodes}}
      _ ->
        {:reply, {:text, "{}"}, state}
    end
  end

  defp pubsub(mtype, subscribed, to_subscribe, to_unsubscribe) do
        states = to_subscribe
        |> Enum.map(fn id ->
          result = Telemetry.Database.lookup({mtype, id})

          if result do
            {:text, Poison.encode!(result)}
          end
        end)
        |> Enum.reject(&is_nil/1)

        subscribed = MapSet.new(to_subscribe)
        |> MapSet.difference(subscribed)
        |> Enum.map(fn id ->
          try do
            :gproc.reg({:p, :l, {mtype, id}})
            id
          rescue
            ArgumentError -> ()
          end
        end)
        |> MapSet.new()
        |> MapSet.union(subscribed)

        unsubscribed = MapSet.new(to_unsubscribe)
        |> MapSet.intersection(subscribed)
        |> Enum.map(fn id ->
          try do
            :gproc.unreg({:p, :l, {mtype, id}})
            id
          rescue
            ArgumentError -> ()
          end
        end)
        |> MapSet.new()

        subscribed = MapSet.difference(subscribed, unsubscribed)
        {subscribed, states}
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
