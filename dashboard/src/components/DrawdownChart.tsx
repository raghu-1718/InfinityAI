import React, { useEffect, useState } from 'react';
import { Paper, Typography, Box } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function DrawdownChart() {
  const [data, setData] = useState<Array<{ date: string, value: number }>>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
  fetch('/api/portfolio/drawdown')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch drawdown data');
        return res.json();
      })
      .then(json => {
        setData(json.drawdown || []);
        setLoading(false);
      })
      .catch(e => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  return (
    <Paper elevation={4} sx={{ p: 2, mb: 3 }}>
      <Typography variant="h6" gutterBottom>Drawdown Chart</Typography>
      <Box height={220}>
        {loading ? (
          <Typography color="textSecondary">Loading...</Typography>
        ) : error ? (
          <Typography color="error">{error}</Typography>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#4A90E2" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </Box>
    </Paper>
  );
}
