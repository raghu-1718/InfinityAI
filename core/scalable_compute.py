# Distributed training example with Ray
import ray
import numpy as np

ray.init()

@ray.remote
def train_model(data):
    # Simulate training
    return np.mean(data)

data_chunks = [np.random.rand(1000) for _ in range(4)]
results = ray.get([train_model.remote(chunk) for chunk in data_chunks])
print("Distributed training results:", results)

# GPU/TPU support example (PyTorch)
import torch

def train_on_gpu():
    if torch.cuda.is_available():
        device = torch.device('cuda')
        x = torch.rand(5, 5).to(device)
        print("Tensor on GPU:", x)
    else:
        print("GPU not available")

train_on_gpu()

# Auto-scaling clusters (Kubernetes manifest example)
# Save as k8s_autoscale.yaml
'''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: infinityai-trainer
spec:
  replicas: 2
  selector:
    matchLabels:
      app: trainer
  template:
    metadata:
      labels:
        app: trainer
    spec:
      containers:
      - name: trainer
        image: infinityai/trainer:latest
        resources:
          limits:
            cpu: "2"
            memory: "4Gi"
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: trainer-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: infinityai-trainer
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
'''
