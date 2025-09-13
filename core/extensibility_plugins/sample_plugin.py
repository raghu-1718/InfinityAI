from core.extensibility import InfinityAIPlugin

class SamplePlugin(InfinityAIPlugin):
    def run(self, *args, **kwargs):
        return "Sample plugin executed successfully!"
