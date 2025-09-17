import React from 'react';
import { Typography, Grid, Box } from '@mui/material';

const data = {
  balance: 1203400,
  todayPnL: 3700,
  ytdReturn: 24.5,
  sharpe: 2.11,
  maxDrawdown: -8.7
};

export default function PortfolioOverview() {
  return (
    <>
      <Typography variant="h6" gutterBottom>Portfolio Overview</Typography>
      <Grid container spacing={2}>
        <Box sx={{ flex: '1 1 50%', minWidth: 200, p: 1 }}>
          <Typography>Portfolio Value</Typography>
          <Typography fontWeight={600} color="primary">₹{data.balance.toLocaleString()}</Typography>
        </Box>
        <Box sx={{ flex: '1 1 50%', minWidth: 200, p: 1 }}>
          <Typography>Today's P&L</Typography>
          <Typography color={data.todayPnL > 0 ? "secondary" : "error"} fontWeight={600}>₹{data.todayPnL.toLocaleString()}</Typography>
        </Box>
        <Box sx={{ flex: '1 1 33%', minWidth: 120, p: 1 }}>
          <Typography>YTD Return</Typography>
          <Typography>{data.ytdReturn}%</Typography>
        </Box>
        <Box sx={{ flex: '1 1 33%', minWidth: 120, p: 1 }}>
          <Typography>Sharpe Ratio</Typography>
          <Typography>{data.sharpe}</Typography>
        </Box>
        <Box sx={{ flex: '1 1 33%', minWidth: 120, p: 1 }}>
          <Typography>Max Drawdown</Typography>
          <Typography>{data.maxDrawdown}%</Typography>
        </Box>
      </Grid>
    </>
  );
}
