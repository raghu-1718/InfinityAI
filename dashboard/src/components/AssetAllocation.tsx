import React, { useEffect, useState } from 'react';
import { Paper, Typography, Box } from '@mui/material';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

// ...existing code...
const COLORS = ['#4A90E2', '#FFD93D', '#50E3C2', '#B8E986', '#FF6F61'];

export default function AssetAllocation() {
  const [data, setData] = useState<Array<{ name: string, value: number }>>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
  fetch('/api/portfolio/allocation')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch asset allocation');
        return res.json();
      })
      .then(json => {
        setData(json.allocation || []);
        setLoading(false);
      })
      .catch(e => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  return (
    <Paper elevation={4} sx={{ p: 2, mb: 3 }}>
      <Typography variant="h6" gutterBottom>Asset Allocation</Typography>
      <Box height={220}>
        {loading ? (
          <Typography color="textSecondary">Loading...</Typography>
        ) : error ? (
          <Typography color="error">{error}</Typography>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={data} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} label>
                {data.map((entry, idx) => (
                  <Cell key={`cell-${idx}`} fill={COLORS[idx % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        )}
      </Box>
    </Paper>
  );
}
