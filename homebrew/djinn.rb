class Djinn < Formula
  include Language::Python::Virtualenv

  desc "AI-powered CLI that converts natural language to shell commands"
  homepage "https://github.com/boubli/djinn"
  url "https://github.com/boubli/djinn/archive/v2.1.1.tar.gz"
  sha256 "PLACEHOLDER_SHA256" # Users or CI would update this, or use head
  head "https://github.com/boubli/djinn.git", branch: "master"

  depends_on "python@3.10"

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/djinn", "--version"
  end
end
