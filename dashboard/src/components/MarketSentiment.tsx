import React from 'react';
import { Typography, Chip } from '@mui/material';

const sentiment = [
  { label: "News Sentiment", value: "Positive", color: "primary" },
  { label: "Social Sentiment", value: "Bullish", color: "secondary" }
];

export default function MarketSentiment() {
  return (
    <>
      <Typography variant="h6" gutterBottom>Market Sentiment & AI Insights</Typography>
      {sentiment.map(s => (
        <Chip key={s.label} label={`${s.label}: ${s.value}`} color={s.color as any} sx={{ mr: 1, mb: 1 }} />
      ))}
      <Typography variant="body2" sx={{ mt: 1 }}>
        “AI Engine: High confidence for multi-asset uptrend today. Risk-adjusted positions held.”
      </Typography>
    </>
  );
}
