defmodule Telemetry.Websocket do
  @behaviour :cowboy_websocket

  require Logger

  def init(req, :all) do
    {:cowboy_websocket, req, :telemetry}
  end

  def init(req, :node) do
    id = Map.get(req.bindings, :id)
    {:cowboy_websocket, req, {:node, id}}
  end

  def init(req, :transmitter) do
    id = Map.get(req.bindings, :id)
    {:cowboy_websocket, req, {:transmitter, id}}
  end

  def websocket_init(state) do
    :gproc.reg({:p, :l, state})

    case state do
      {type, id} ->
        result = Telemetry.Database.lookup({type, id})
        if result do
          {:reply, {:text, Poison.encode!(result)}, state}
        else
          {:reply, {:text, "{}"}, state}
        end
      _ -> {:ok, state}
    end
  end

  def websocket_handle({:text, message}, state) do
    json = Poison.decode!(message)
    websocket_handle({:json, json}, state)
  end

  def websocket_handle({:json, _}, state) do
    {:reply, {:text, "{}"}, state}
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
