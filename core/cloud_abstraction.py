# Example cloud abstraction for storage
class CloudStorage:
    def __init__(self, provider):
        self.provider = provider
    def upload(self, file_path):
        if self.provider == 'azure':
            # Azure upload logic
            pass
        elif self.provider == 'aws':
            # AWS upload logic
            pass
        elif self.provider == 'gcp':
            # GCP upload logic
            pass
        else:
            raise ValueError('Unsupported provider')
