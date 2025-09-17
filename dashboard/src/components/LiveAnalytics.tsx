import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import io from 'socket.io-client';
import { Typography } from '@mui/material';

const socket = io('https://your-api-server.com'); // Use your backend URL

const LiveAnalytics = () => {
  const [data, setData] = useState<Array<{ time: string, pnl: number }>>([]);

  useEffect(() => {
    socket.on('portfolio_update', (update: any) => {
      setData(current => [...current.slice(-49), { time: update.time, pnl: update.pnl }]);
    });
    return () => { socket.off('portfolio_update'); };
  }, []);

  return (
    <>
      <Typography variant="h6" gutterBottom>Live Portfolio Analytics</Typography>
      <ResponsiveContainer width="100%" height={240}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" tickFormatter={v => v.slice(11,19)} />
          <YAxis domain={['auto', 'auto']} />
          <Tooltip />
          <Line type="monotone" dataKey="pnl" stroke="#4A90E2" strokeWidth={3} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </>
  );
};

export default LiveAnalytics;
