class DjinnCli < Formula
  include Language::Python::Virtualenv

  desc "AI-powered CLI that converts natural language to shell commands"
  homepage "https://github.com/boubli/djinn"
  url "https://files.pythonhosted.org/packages/source/d/djinn-cli/djinn_cli-2.1.0.tar.gz"
  sha256 "1782131aa4cd6f6d616b82f4f6a8b836f2e0f57f4dc1b41a3aff82f0509a6faf"
  license "MIT"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "DJINN", shell_output("#{bin}/djinn --version")
  end
end
