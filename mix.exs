defmodule Telemetry.MixProject do
  use Mix.Project

  def project do
    [
      app: :telemetry,
      version: "0.1.0",
      elixir: "~> 1.6",
      start_permanent: Mix.env() == :prod,
      deps: deps()
    ]
  end

  # Run "mix help compile.app" to learn about applications.
  def application do
    [
      applications: [:cowboy, :plug, :amqp, :gproc],
      extra_applications: [:logger],
      mod: {Telemetry.Application, []}
    ]
  end

  # Run "mix help deps" to learn about dependencies.
  defp deps do
    [
      {:poison, "~> 3.1"},
      {:amqp, "~> 1.0"},
      {:cowboy, "~> 2.4"},
      {:plug, "~> 1.6"},
      {:gproc, "~> 0.8.0"}
    ]
  end
end
