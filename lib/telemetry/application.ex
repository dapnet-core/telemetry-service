defmodule Telemetry.Application do
  # See https://hexdocs.pm/elixir/Application.html
  # for more information on OTP Applications
  @moduledoc false

  use Application

  def start(_type, _args) do
    import Supervisor.Spec

    # List all child processes to be supervised
    children = [
      Plug.Adapters.Cowboy2.child_spec(
        scheme: :http,
        plug: {Telemetry.Router, []},
        options: [
          port: 80,
          dispatch: [{:_, [
                         {"/telemetry", Telemetry.Websocket, :all},
                         {"/telemetry/transmitter/:id", Telemetry.Websocket, :transmitter},
                         {"/telemetry/node/:id", Telemetry.Websocket, :node},
                         {:_, Plug.Adapters.Cowboy2.Handler, {Telemetry.Router, []}}
                       ]}]
        ]
      ),
      worker(Telemetry.Consumer, [], restart: :permanent),
      worker(Telemetry.Database, [], restart: :permanent),
    ]

    # See https://hexdocs.pm/elixir/Supervisor.html
    # for other strategies and supported options
    opts = [strategy: :one_for_one, name: Telemetry.Supervisor]
    Supervisor.start_link(children, opts)
  end
end
