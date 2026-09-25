from unittest.mock import MagicMock, patch

from kernel.kernel import createKernel


def test_createKernel_wiresOllamaAndPlugin():
    with (
        patch("kernel.kernel.Kernel") as Kernel,
        patch("kernel.kernel.OllamaChatCompletion") as OllamaChatCompletion,
        patch("kernel.kernel.IdiomPlugin") as IdiomPlugin,
    ):
        kernel = MagicMock()
        Kernel.return_value = kernel
        ollama = MagicMock()
        OllamaChatCompletion.return_value = ollama
        plugin = MagicMock()
        IdiomPlugin.return_value = plugin

        result = createKernel()

    assert result is kernel
    kernel.add_service.assert_called_once_with(ollama)
    kernel.add_plugin.assert_called_once_with(plugin, plugin_name="IdiomPlugin")
