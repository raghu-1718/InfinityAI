import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
    Card, CardContent, Typography, Box, Button, TextField,
    Switch, FormControlLabel, Chip, Alert, Dialog, DialogTitle,
    DialogContent, DialogActions, Table, TableBody, TableCell,
    TableContainer, TableHead, TableRow, Paper, IconButton,
    Badge, CircularProgress, LinearProgress,
    Accordion, AccordionSummary, AccordionDetails, Slider
} from '@mui/material';
import { Grid } from '@mui/system';
import {
    Refresh, Settings, ExpandMore
} from '@mui/icons-material';

interface LiveTrade {
    id: string;
    symbol: string;
    side: 'BUY' | 'SELL';
    quantity: number;
    price: number;
    order_type: 'MARKET' | 'LIMIT' | 'SL' | 'SL-M';
    status: 'PENDING' | 'EXECUTED' | 'CANCELLED' | 'REJECTED';
    timestamp: string;
    ai_confidence?: number;
    ai_reasoning?: string;
}

interface TradingSignal {
    symbol: string;
    signal: 'BUY' | 'SELL' | 'HOLD';
    strength: number;
    price: number;
    target_price: number;
    stop_loss: number;
    reasoning: string;
    timestamp: string;
}

interface AutoTradingConfig {
    enabled: boolean;
    max_position_size: number;
    max_daily_loss: number;
    risk_per_trade: number;
    min_confidence: number;
    symbols: string[];
    strategies: string[];
}

const LiveTrading: React.FC = () => {
    const [liveTrades, setLiveTrades] = useState<LiveTrade[]>([]);
    const [signals, setSignals] = useState<TradingSignal[]>([]);
    const [autoTrading, setAutoTrading] = useState<AutoTradingConfig>({
        enabled: false,
        max_position_size: 100000,
        max_daily_loss: 50000,
        risk_per_trade: 0.02,
        min_confidence: 0.7,
        symbols: ['NSE_EQ|1333', 'NSE_EQ|1594'],
        strategies: ['momentum', 'mean_reversion']
    });
    const [isConnected, setIsConnected] = useState<boolean>(false);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [showSettings, setShowSettings] = useState<boolean>(false);
    const [manualOrder, setManualOrder] = useState({
        symbol: '',
        side: 'BUY' as 'BUY' | 'SELL',
        quantity: 0,
        price: 0,
        order_type: 'MARKET' as 'MARKET' | 'LIMIT' | 'SL' | 'SL-M'
    });

    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

    const userId = 'raghu_test_1';

    const connectWebSocket = useCallback(() => {
        try {
            wsRef.current = new WebSocket('ws://localhost:8000/ws/trading');

            wsRef.current.onopen = () => {
                console.log('WebSocket connected');
                setIsConnected(true);
                setError(null);
            };

            wsRef.current.onmessage = (event) => {
                const data = JSON.parse(event.data);
                handleWebSocketMessage(data);
            };

            wsRef.current.onclose = () => {
                console.log('WebSocket disconnected');
                setIsConnected(false);
                // Auto-reconnect after 5 seconds
                reconnectTimeoutRef.current = setTimeout(connectWebSocket, 5000);
            };

            wsRef.current.onerror = (error) => {
                console.error('WebSocket error:', error);
                setError('WebSocket connection failed');
            };

        } catch (err) {
            console.error('Failed to connect WebSocket:', err);
            setError('Failed to establish WebSocket connection');
        }
    }, []);

    useEffect(() => {
        connectWebSocket();
        fetchInitialData();

        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
        };
    }, [connectWebSocket]);

    const handleWebSocketMessage = (data: any) => {
        switch (data.type) {
            case 'TRADE_UPDATE':
                setLiveTrades(prev => [data.trade, ...prev.slice(0, 49)]); // Keep last 50 trades
                break;
            case 'SIGNAL_UPDATE':
                setSignals(prev => [data.signal, ...prev.slice(0, 19)]); // Keep last 20 signals
                break;
            case 'CONNECTION_STATUS':
                setIsConnected(data.connected);
                break;
            default:
                console.log('Unknown message type:', data.type);
        }
    };

    const fetchInitialData = async () => {
        try {
            setLoading(true);

            // Fetch recent trades
            const tradesResponse = await fetch(`http://localhost:8000/trading/recent-trades/${userId}`);
            if (tradesResponse.ok) {
                const tradesData = await tradesResponse.json();
                setLiveTrades(tradesData.trades || []);
            }

            // Fetch current signals
            const signalsResponse = await fetch(`http://localhost:8000/trading/signals`);
            if (signalsResponse.ok) {
                const signalsData = await signalsResponse.json();
                setSignals(signalsData.signals || []);
            }

        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const executeManualOrder = async () => {
        try {
            setLoading(true);

            const orderData = {
                ...manualOrder,
                user_id: userId,
                timestamp: new Date().toISOString()
            };

            const response = await fetch('http://localhost:8000/trading/execute-order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(orderData)
            });

            if (!response.ok) {
                throw new Error('Failed to execute order');
            }

            const result = await response.json();
            alert(`Order executed successfully! Order ID: ${result.order_id}`);

            // Reset form
            setManualOrder({
                symbol: '',
                side: 'BUY',
                quantity: 0,
                price: 0,
                order_type: 'MARKET'
            });

        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const toggleAutoTrading = async () => {
        try {
            const newState = !autoTrading.enabled;

            const response = await fetch('http://localhost:8000/trading/auto-trading', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    enabled: newState,
                    config: autoTrading
                })
            });

            if (!response.ok) {
                throw new Error('Failed to toggle auto trading');
            }

            setAutoTrading(prev => ({ ...prev, enabled: newState }));

        } catch (err: any) {
            setError(err.message);
        }
    };

    const updateAutoTradingConfig = (field: keyof AutoTradingConfig, value: any) => {
        setAutoTrading(prev => ({ ...prev, [field]: value }));
    };

    const getSignalColor = (signal: string) => {
        switch (signal) {
            case 'BUY': return 'success';
            case 'SELL': return 'error';
            case 'HOLD': return 'warning';
            default: return 'primary';
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'EXECUTED': return 'success';
            case 'PENDING': return 'warning';
            case 'CANCELLED': return 'error';
            case 'REJECTED': return 'error';
            default: return 'primary';
        }
    };

    return (
        <Box sx={{ width: '100%', p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold' }}>
                    ⚡ Live Trading Dashboard
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Badge
                        variant="dot"
                        color={isConnected ? 'success' : 'error'}
                        sx={{ mr: 1 }}
                    >
                        <Typography variant="body2">
                            {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
                        </Typography>
                    </Badge>
                    <IconButton onClick={fetchInitialData}>
                        <Refresh />
                    </IconButton>
                    <IconButton onClick={() => setShowSettings(true)}>
                        <Settings />
                    </IconButton>
                </Box>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
            )}

            {/* Auto Trading Status */}
            <Card sx={{ mb: 3, background: autoTrading.enabled ?
                'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)' :
                'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
            }}>
                <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Box>
                            <Typography variant="h6" sx={{ color: 'white', fontWeight: 'bold' }}>
                                🤖 Auto Trading {autoTrading.enabled ? 'Active' : 'Inactive'}
                            </Typography>
                            <Typography sx={{ color: 'white', opacity: 0.9 }}>
                                AI-powered automated trading system
                            </Typography>
                        </Box>
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={autoTrading.enabled}
                                    onChange={toggleAutoTrading}
                                    color="primary"
                                />
                            }
                            label=""
                        />
                    </Box>
                </CardContent>
            </Card>

            <Grid container spacing={3}>
                {/* Manual Order Panel */}
                <Grid size={{ xs: 12, md: 4 }}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" sx={{ mb: 2 }}>📝 Manual Order</Typography>

                            <Box component="form" sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                                <TextField
                                    label="Symbol"
                                    value={manualOrder.symbol}
                                    onChange={(e) => setManualOrder(prev => ({ ...prev, symbol: e.target.value }))}
                                    placeholder="e.g., NSE_EQ|1333"
                                    size="small"
                                />

                                <Box sx={{ display: 'flex', gap: 1 }}>
                                    <Button
                                        variant={manualOrder.side === 'BUY' ? 'contained' : 'outlined'}
                                        color="success"
                                        onClick={() => setManualOrder(prev => ({ ...prev, side: 'BUY' }))}
                                        sx={{ flex: 1 }}
                                    >
                                        BUY
                                    </Button>
                                    <Button
                                        variant={manualOrder.side === 'SELL' ? 'contained' : 'outlined'}
                                        color="error"
                                        onClick={() => setManualOrder(prev => ({ ...prev, side: 'SELL' }))}
                                        sx={{ flex: 1 }}
                                    >
                                        SELL
                                    </Button>
                                </Box>

                                <TextField
                                    label="Quantity"
                                    type="number"
                                    value={manualOrder.quantity}
                                    onChange={(e) => setManualOrder(prev => ({ ...prev, quantity: parseInt(e.target.value) || 0 }))}
                                    size="small"
                                />

                                <TextField
                                    label="Price (for Limit orders)"
                                    type="number"
                                    value={manualOrder.price}
                                    onChange={(e) => setManualOrder(prev => ({ ...prev, price: parseFloat(e.target.value) || 0 }))}
                                    size="small"
                                    disabled={manualOrder.order_type === 'MARKET'}
                                />

                                <TextField
                                    select
                                    label="Order Type"
                                    value={manualOrder.order_type}
                                    onChange={(e) => setManualOrder(prev => ({ ...prev, order_type: e.target.value as any }))}
                                    size="small"
                                    SelectProps={{
                                        native: true,
                                        inputProps: {
                                            title: 'Order Type',
                                            'aria-label': 'Order Type'
                                        }
                                    }}
                                    aria-label="Order Type"
                                >
                                    <option value="MARKET" title="Market">Market</option>
                                    <option value="LIMIT" title="Limit">Limit</option>
                                    <option value="SL" title="Stop Loss">Stop Loss</option>
                                    <option value="SL-M" title="Stop Loss Market">Stop Loss Market</option>
                                </TextField>

                                <Button
                                    variant="contained"
                                    onClick={executeManualOrder}
                                    disabled={loading || !manualOrder.symbol || manualOrder.quantity <= 0}
                                    sx={{ mt: 1 }}
                                >
                                    {loading ? <CircularProgress size={20} /> : 'Execute Order'}
                                </Button>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                {/* AI Signals Panel */}
                <Grid size={{ xs: 12, md: 4 }}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" sx={{ mb: 2 }}>🎯 AI Trading Signals</Typography>

                            {signals.length === 0 ? (
                                <Typography color="text.secondary">No active signals</Typography>
                            ) : (
                                <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
                                    {signals.map((signal, index) => (
                                        <Card key={index} sx={{ mb: 1, border: 1, borderColor: 'divider' }}>
                                            <CardContent sx={{ py: 1 }}>
                                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                                                    <Typography variant="h6" sx={{ fontSize: '1rem' }}>
                                                        {signal.symbol}
                                                    </Typography>
                                                    <Chip
                                                        label={signal.signal}
                                                        color={getSignalColor(signal.signal)}
                                                        size="small"
                                                    />
                                                </Box>

                                                <Typography variant="body2" sx={{ mb: 1 }}>
                                                    Strength: {(signal.strength * 100).toFixed(1)}%
                                                </Typography>

                                                <LinearProgress
                                                    variant="determinate"
                                                    value={signal.strength * 100}
                                                    color={getSignalColor(signal.signal)}
                                                    sx={{ mb: 1, height: 6 }}
                                                />

                                                <Typography variant="body2" sx={{ fontSize: '0.8rem', color: 'text.secondary' }}>
                                                    Target: ₹{signal.target_price.toFixed(2)} | SL: ₹{signal.stop_loss.toFixed(2)}
                                                </Typography>

                                                <Typography variant="body2" sx={{ fontSize: '0.8rem', fontStyle: 'italic', mt: 1 }}>
                                                    {signal.reasoning}
                                                </Typography>
                                            </CardContent>
                                        </Card>
                                    ))}
                                </Box>
                            )}
                        </CardContent>
                    </Card>
                </Grid>

                {/* Recent Trades Panel */}
                <Grid size={{ xs: 12, md: 4 }}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" sx={{ mb: 2 }}>📊 Recent Trades</Typography>

                            {liveTrades.length === 0 ? (
                                <Typography color="text.secondary">No recent trades</Typography>
                            ) : (
                                <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
                                    <Table size="small">
                                        <TableHead>
                                            <TableRow>
                                                <TableCell>Symbol</TableCell>
                                                <TableCell>Side</TableCell>
                                                <TableCell>Qty</TableCell>
                                                <TableCell>Price</TableCell>
                                                <TableCell>Status</TableCell>
                                            </TableRow>
                                        </TableHead>
                                        <TableBody>
                                            {liveTrades.slice(0, 10).map((trade) => (
                                                <TableRow key={trade.id}>
                                                    <TableCell>{trade.symbol}</TableCell>
                                                    <TableCell>
                                                        <Chip
                                                            label={trade.side}
                                                            color={trade.side === 'BUY' ? 'success' : 'error'}
                                                            size="small"
                                                        />
                                                    </TableCell>
                                                    <TableCell>{trade.quantity}</TableCell>
                                                    <TableCell>₹{trade.price.toFixed(2)}</TableCell>
                                                    <TableCell>
                                                        <Chip
                                                            label={trade.status}
                                                            color={getStatusColor(trade.status)}
                                                            size="small"
                                                        />
                                                    </TableCell>
                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    </Table>
                                </TableContainer>
                            )}
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Auto Trading Settings Dialog */}
            <Dialog open={showSettings} onClose={() => setShowSettings(false)} maxWidth="md" fullWidth>
                <DialogTitle>
                    <Typography variant="h6">⚙️ Auto Trading Configuration</Typography>
                </DialogTitle>
                <DialogContent>
                    <Box sx={{ pt: 2 }}>
                        <Accordion>
                            <AccordionSummary expandIcon={<ExpandMore />}>
                                <Typography variant="h6">🎯 Risk Management</Typography>
                            </AccordionSummary>
                            <AccordionDetails>
                                <Grid container spacing={2}>
                                    <Grid size={{ xs: 12, md: 6 }}>
                                        <Typography gutterBottom>Max Position Size (₹)</Typography>
                                        <Slider
                                            value={autoTrading.max_position_size}
                                            onChange={(_, value) => updateAutoTradingConfig('max_position_size', value)}
                                            min={10000}
                                            max={500000}
                                            step={10000}
                                            valueLabelDisplay="auto"
                                        />
                                        <Typography variant="body2" color="text.secondary">
                                            ₹{autoTrading.max_position_size.toLocaleString()}
                                        </Typography>
                                    </Grid>

                                    <Grid size={{ xs: 12, md: 6 }}>
                                        <Typography gutterBottom>Max Daily Loss (₹)</Typography>
                                        <Slider
                                            value={autoTrading.max_daily_loss}
                                            onChange={(_, value) => updateAutoTradingConfig('max_daily_loss', value)}
                                            min={5000}
                                            max={200000}
                                            step={5000}
                                            valueLabelDisplay="auto"
                                        />
                                        <Typography variant="body2" color="text.secondary">
                                            ₹{autoTrading.max_daily_loss.toLocaleString()}
                                        </Typography>
                                    </Grid>

                                    <Grid size={{ xs: 12, md: 6 }}>
                                        <Typography gutterBottom>Risk per Trade (%)</Typography>
                                        <Slider
                                            value={autoTrading.risk_per_trade * 100}
                                            onChange={(_, value) => updateAutoTradingConfig('risk_per_trade', (value as number) / 100)}
                                            min={0.5}
                                            max={5}
                                            step={0.1}
                                            valueLabelDisplay="auto"
                                        />
                                        <Typography variant="body2" color="text.secondary">
                                            {(autoTrading.risk_per_trade * 100).toFixed(1)}%
                                        </Typography>
                                    </Grid>

                                    <Grid size={{ xs: 12, md: 6 }}>
                                        <Typography gutterBottom>Min AI Confidence (%)</Typography>
                                        <Slider
                                            value={autoTrading.min_confidence * 100}
                                            onChange={(_, value) => updateAutoTradingConfig('min_confidence', (value as number) / 100)}
                                            min={50}
                                            max={95}
                                            step={5}
                                            valueLabelDisplay="auto"
                                        />
                                        <Typography variant="body2" color="text.secondary">
                                            {(autoTrading.min_confidence * 100).toFixed(1)}%
                                        </Typography>
                                    </Grid>
                                </Grid>
                            </AccordionDetails>
                        </Accordion>

                        <Accordion>
                            <AccordionSummary expandIcon={<ExpandMore />}>
                                <Typography variant="h6">📊 Trading Symbols</Typography>
                            </AccordionSummary>
                            <AccordionDetails>
                                <TextField
                                    fullWidth
                                    multiline
                                    rows={3}
                                    label="Symbols (one per line)"
                                    value={autoTrading.symbols.join('\n')}
                                    onChange={(e) => updateAutoTradingConfig('symbols', e.target.value.split('\n').filter(s => s.trim()))}
                                    placeholder="NSE_EQ|1333&#10;NSE_EQ|1594&#10;NSE_EQ|2885"
                                />
                            </AccordionDetails>
                        </Accordion>

                        <Accordion>
                            <AccordionSummary expandIcon={<ExpandMore />}>
                                <Typography variant="h6">🧠 Trading Strategies</Typography>
                            </AccordionSummary>
                            <AccordionDetails>
                                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                                    {['momentum', 'mean_reversion', 'breakout', 'scalping', 'swing'].map((strategy) => (
                                        <Chip
                                            key={strategy}
                                            label={strategy}
                                            clickable
                                            color={autoTrading.strategies.includes(strategy) ? 'primary' : 'default'}
                                            onClick={() => {
                                                const newStrategies = autoTrading.strategies.includes(strategy)
                                                    ? autoTrading.strategies.filter(s => s !== strategy)
                                                    : [...autoTrading.strategies, strategy];
                                                updateAutoTradingConfig('strategies', newStrategies);
                                            }}
                                        />
                                    ))}
                                </Box>
                            </AccordionDetails>
                        </Accordion>
                    </Box>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setShowSettings(false)}>Cancel</Button>
                    <Button variant="contained" onClick={() => setShowSettings(false)}>
                        Save Configuration
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Trading Option Select (Newly Added) */}
            <Box sx={{ mt: 3, p: 2, borderRadius: 1, border: 1, borderColor: 'divider', backgroundColor: 'background.paper' }}>
                <Typography variant="h6" sx={{ mb: 2 }}>⚙️ Trading Options</Typography>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <label htmlFor="trading-select">Select Trading Option:</label>
                    <select
                         id="trading-select"
                        aria-label="Choose a trading option"
                        title="Select Trading Option"
                    >
                        <option value="buy">Buy</option>
                        <option value="sell">Sell</option>
                        {/* Add more options as needed */}
                    </select>
                </Box>
            </Box>
        </Box>
    );
};

export default LiveTrading;