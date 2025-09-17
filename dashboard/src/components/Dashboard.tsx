import React from 'react';
import { Box, Typography, Paper, Chip } from '@mui/material';
import PortfolioOverview from './PortfolioOverview';
import LiveAnalytics from './LiveAnalytics';
import RiskPanel from './RiskPanel';
import MarketSentiment from './MarketSentiment';

const Dashboard = () => (
  <Box p={3} bgcolor="background.default" minHeight="100vh">
    <Typography variant="h4" mb={2} color="primary">InfinityAI.Pro Dashboard</Typography>
    <Box display="flex" flexWrap="wrap" gap={3}>
      <Box flex={2} minWidth={320}>
        <Paper elevation={4} sx={{ p: 2 }}>
          <PortfolioOverview />
        </Paper>
        <Paper elevation={4} sx={{ mt: 3, p: 2 }}>
          <LiveAnalytics />
        </Paper>
      </Box>
      <Box flex={1} minWidth={240}>
        <Paper elevation={4} sx={{ p: 2 }}>
          <RiskPanel />
        </Paper>
        <Paper elevation={4} sx={{ mt: 3, p: 2 }}>
          <MarketSentiment />
        </Paper>
      </Box>
    </Box>
    <Box mt={4} display="flex" justifyContent="flex-end" gap={2}>
      <Chip label="AI Confidence: 91%" color="secondary" />
      <Chip label="Latency: <1ms" color="primary" />
    </Box>
  </Box>
);

export default Dashboard;
