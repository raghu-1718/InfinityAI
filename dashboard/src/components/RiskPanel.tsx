import React from 'react';
import { Typography, List, ListItem, ListItemText } from '@mui/material';

const RISK = [
  { type: 'VaR (99%)', value: '₹25,000' },
  { type: 'Sharpe Ratio', value: '2.11' },
  { type: 'Max Drawdown', value: '-8.7%' },
  { type: 'Position Risk', value: 'Low' }
];

export default function RiskPanel() {
  return (
    <>
      <Typography variant="h6" gutterBottom>Risk Dashboard</Typography>
      <List>
        {RISK.map(r => (
          <ListItem key={r.type}>
            <ListItemText primary={r.type} secondary={r.value} />
          </ListItem>
        ))}
      </List>
    </>
  );
}
