defmodule Telemetry.Consumer do
  require Logger

  use GenServer
  use AMQP

  def start_link do
    GenServer.start_link(__MODULE__, [], [])
  end

  @exchange    "dapnet.telemetry"
  @queue       "telemetry_service"

  def init(_opts) do
    connect
  end

  # Confirmation sent by the broker after registering this process as a consumer
  def handle_info({:basic_consume_ok, %{consumer_tag: consumer_tag}}, chan) do
    {:noreply, chan}
  end

  # Sent by the broker when the consumer is unexpectedly cancelled (such as after a queue deletion)
  def handle_info({:basic_cancel, %{consumer_tag: consumer_tag}}, chan) do
    {:stop, :normal, chan}
  end

  # Confirmation sent by the broker to the consumer process after a Basic.cancel
  def handle_info({:basic_cancel_ok, %{consumer_tag: consumer_tag}}, chan) do
    {:noreply, chan}
  end

  def handle_info({:basic_deliver, payload, %{delivery_tag: tag, routing_key: key}}, chan) do
    :ok = Basic.ack chan, tag

    data = Poison.decode!(payload)

    {type, id} = case key do
      "transmitter." <> call ->
                     :gproc.send({:p, :l, {:transmitter, call}}, {:text, payload})
                     Telemetry.Database.update({:transmitter, call, data})
                     {:transmitter, call}
      "node." <> id ->
                     :gproc.send({:p, :l, {:node, id}}, {:text, payload})
                     Telemetry.Database.update({:node, id, data})
                     {:node, id}
                   _ ->
                     {:unknown, key}
    end

    data = data
    |> Map.put("type", type)
    |> Map.put("id", id)
    |> Poison.encode!

    :gproc.send({:p, :l, :telemetry}, {:text, data})

    {:noreply, chan}
  end

  # Automatic Reconnect
  def handle_info({:DOWN, _, :process, _pid, _reason}, _) do
    Logger.warn("RabbitMQ connection closed.")
    {:ok, chan} = connect
    {:noreply, chan}
  end

  defp connect do
    node_name = System.get_env("NODE_NAME")
    auth_key = System.get_env("NODE_AUTHKEY")

    opts = [
      host: "rabbitmq",
      username: "node-#{node_name}",
      password: auth_key,
      client_properties: [{"connection_name", :longstr, "Telemetry Service"}]
    ]

    case Connection.open(opts) do
      {:ok, conn} ->
        Logger.info("RabbitMQ connection established.")
        Process.monitor(conn.pid)

        {:ok, chan} = Channel.open(conn)
        setup_queue(chan)
        Basic.qos(chan, prefetch_count: 10)
        {:ok, _consumer_tag} = Basic.consume(chan, @queue)
        {:ok, chan}

      {:error, _} ->
        Logger.error("RabbitMQ connection failed.")
        # Reconnection loop
        :timer.sleep(10000)
        connect
    end
  end

  defp setup_queue(chan) do
    # Messages that cannot be delivered to any consumer in the main queue will be routed to the error queue
    {:ok, _} = Queue.declare(chan, @queue, durable: true)
    :ok = Exchange.fanout(chan, @exchange, durable: true)
    :ok = Queue.bind(chan, @queue, @exchange)
  end
end
