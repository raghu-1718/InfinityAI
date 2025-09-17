import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import io, { type Socket } from 'socket.io-client';
import { Typography } from '@mui/material';

const socket: Socket = io('https://www.infinityai.pro', {
  path: '/ws/socket.io',
  transports: ['websocket']
});

const LiveAnalytics = () => {
  const [data, setData] = useState<Array<{ time: string, pnl: number }>>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    socket.on('connect', () => setLoading(false));
    socket.on('connect_error', () => {
      setError('Could not connect to live analytics server.');
      setLoading(false);
    });
    socket.on('portfolio_update', (update: any) => {
      setData(current => [...current.slice(-49), { time: update.time, pnl: update.pnl }]);
    });
    return () => {
      socket.off('portfolio_update');
      socket.off('connect');
      socket.off('connect_error');
    };
  }, []);

  return (
    <>
      <Typography variant="h6" gutterBottom>Live Portfolio Analytics</Typography>
      {loading ? (
        <Typography color="textSecondary">Connecting to live data...</Typography>
      ) : error ? (
        <Typography color="error">{error}</Typography>
      ) : (
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" tickFormatter={v => v.slice(11,19)} />
            <YAxis domain={['auto', 'auto']} />
            <Tooltip />
            <Line type="monotone" dataKey="pnl" stroke="#4A90E2" strokeWidth={3} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      )}
    </>
  );
};

export default LiveAnalytics;
