import React, { useState, useEffect } from 'react';
import { Box, Button, Typography, TextField, Paper, CircularProgress, Alert, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/ai';

const AIModelManager: React.FC = () => {
  const [models, setModels] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [versions, setVersions] = useState<any[]>([]);
  const [trainData, setTrainData] = useState('');
  const [trainLabels, setTrainLabels] = useState('');
  const [trainResult, setTrainResult] = useState<any>(null);
  const [predictInput, setPredictInput] = useState('');
  const [predictResult, setPredictResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/models`);
      const data = await res.json();
      setModels(data.models || []);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchVersions = async (modelName: string) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/models/${modelName}/versions`);
      const data = await res.json();
      setVersions(data.versions || []);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTrain = async () => {
    setLoading(true);
    setTrainResult(null);
    setError(null);
    try {
      const X = JSON.parse(trainData);
      const y = JSON.parse(trainLabels);
      const res = await fetch(`${API_BASE}/train`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ X, y, model_name: selectedModel })
      });
      const data = await res.json();
      setTrainResult(data.result);
      fetchModels();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handlePredict = async () => {
    setLoading(true);
    setPredictResult(null);
    setError(null);
    try {
      const X = JSON.parse(predictInput);
      const res = await fetch(`${API_BASE}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ X, model_uri: selectedModel })
      });
      const data = await res.json();
      setPredictResult(data.predictions);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" sx={{ mb: 2 }}>AI Model Manager</Typography>
      {error && <Alert severity="error">{error}</Alert>}
      <Box sx={{ mb: 2 }}>
        <Button variant="contained" onClick={fetchModels} disabled={loading}>Refresh Models</Button>
      </Box>
      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle1">Available Models:</Typography>
        <TableContainer component={Paper} sx={{ maxWidth: 500 }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Model Name</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {models.map((model) => (
                <TableRow key={model} selected={selectedModel === model}>
                  <TableCell>{model}</TableCell>
                  <TableCell>
                    <Button size="small" onClick={() => { setSelectedModel(model); fetchVersions(model); }}>Select</Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
      {selectedModel && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle1">Selected Model: {selectedModel}</Typography>
          <Typography variant="subtitle2">Versions:</Typography>
          <ul>
            {versions.map((v) => (
              <li key={v}>{v}</li>
            ))}
          </ul>
        </Box>
      )}
      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle1">Train Model</Typography>
        <TextField
          label="Training Data (X as JSON)"
          multiline
          minRows={2}
          fullWidth
          value={trainData}
          onChange={e => setTrainData(e.target.value)}
          sx={{ mb: 1 }}
        />
        <TextField
          label="Training Labels (y as JSON)"
          multiline
          minRows={1}
          fullWidth
          value={trainLabels}
          onChange={e => setTrainLabels(e.target.value)}
          sx={{ mb: 1 }}
        />
        <Button variant="contained" onClick={handleTrain} disabled={loading || !selectedModel}>Train</Button>
        {trainResult && <Alert severity="success" sx={{ mt: 1 }}>Trained! {JSON.stringify(trainResult)}</Alert>}
      </Box>
      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle1">Predict</Typography>
        <TextField
          label="Input Data (X as JSON)"
          multiline
          minRows={1}
          fullWidth
          value={predictInput}
          onChange={e => setPredictInput(e.target.value)}
          sx={{ mb: 1 }}
        />
        <Button variant="contained" onClick={handlePredict} disabled={loading || !selectedModel}>Predict</Button>
        {predictResult && <Alert severity="info" sx={{ mt: 1 }}>Prediction: {JSON.stringify(predictResult)}</Alert>}
      </Box>
      {loading && <CircularProgress />}
    </Box>
  );
};

export default AIModelManager;
