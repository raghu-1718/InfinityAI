import React, { useEffect, useState } from 'react';
import { Paper, Typography, Box, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';

export default function ModelLeaderboard() {
  const [models, setModels] = useState<Array<any>>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
  fetch('/api/ai/models/leaderboard')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch model leaderboard');
        return res.json();
      })
      .then(json => {
        setModels(json.leaderboard || []);
        setLoading(false);
      })
      .catch(e => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  return (
    <Paper elevation={4} sx={{ p: 2, mb: 3 }}>
      <Typography variant="h6" gutterBottom>Model Leaderboard</Typography>
      <Box>
        {loading ? (
          <Typography color="textSecondary">Loading...</Typography>
        ) : error ? (
          <Typography color="error">{error}</Typography>
        ) : (
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Model</TableCell>
                  <TableCell>Version</TableCell>
                  <TableCell>Accuracy</TableCell>
                  <TableCell>Drift</TableCell>
                  <TableCell>Last Trained</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {models.map((m: any) => (
                  <TableRow key={m.name}>
                    <TableCell>{m.name}</TableCell>
                    <TableCell>{m.version}</TableCell>
                    <TableCell>{(m.accuracy * 100).toFixed(1)}%</TableCell>
                    <TableCell>{m.drift}</TableCell>
                    <TableCell>{m.lastTrained}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Box>
    </Paper>
  );
}
