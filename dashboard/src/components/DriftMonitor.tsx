import React, { useEffect, useState } from 'react';
import { Paper, Typography, Box, LinearProgress } from '@mui/material';


export default function DriftMonitor() {
  const [drift, setDrift] = useState<Array<any>>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetch('https://www.infinityai.pro/api/ai/models/drift')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch drift data');
        return res.json();
      })
      .then(json => {
        setDrift(json.drift || []);
        setLoading(false);
      })
      .catch(e => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  return (
    <Paper elevation={4} sx={{ p: 2, mb: 3 }}>
      <Typography variant="h6" gutterBottom>Model Drift Monitor</Typography>
      <Box>
        {loading ? (
          <Typography color="textSecondary">Loading...</Typography>
        ) : error ? (
          <Typography color="error">{error}</Typography>
        ) : (
          drift.map((d: any) => (
            <Box key={d.model} mb={2}>
              <Typography variant="body2">{d.model} ({(d.drift * 100).toFixed(1)}% drift)</Typography>
              <LinearProgress variant="determinate" value={Math.min(d.drift * 100, 100)} sx={{ height: 8, borderRadius: 4, background: '#232B3E', '& .MuiLinearProgress-bar': { background: d.drift > 0.15 ? '#FF6F61' : '#4A90E2' } }} />
            </Box>
          ))
        )}
      </Box>
    </Paper>
  );
}
