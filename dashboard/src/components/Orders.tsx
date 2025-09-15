import React, { useState, useEffect } from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Typography, Box, CircularProgress, Chip } from '@mui/material';

// Interface for a single order based on Dhan API response
interface Order {
    dhanClientId: string;
    orderId: string;
    exchange: string;
    securityId: string; // Using securityId as symbol might not be available directly
    legName: string;
    transactionType: 'BUY' | 'SELL';
    orderType: 'LIMIT' | 'MARKET' | 'STOP_LOSS' | 'STOP_LIMIT';
    quantity: number;
    price: number;
    orderStatus: string;
    tradingTime: string;
    exchangeOrderId: string;
    omsErrorCode: string;
    omsErrorDescription: string;
}

// The API response wraps the list in a 'data' property
interface OrdersApiResponse {
    data: Order[];
}

const getStatusChipColor = (status: string) => {
    switch (status.toUpperCase()) {
        case 'TRADED':
        case 'FILLED':
            return 'success';
        case 'CANCELLED':
        case 'REJECTED':
            return 'error';
        case 'PENDING':
        case 'OPEN':
            return 'primary';
        default:
            return 'default';
    }
};

const Orders: React.FC = () => {
    const [orders, setOrders] = useState<Order[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState<boolean>(true);

    const userId = 'raghu_test_1'; // Using the same hardcoded user for now

    useEffect(() => {
        const fetchOrders = async () => {
            try {
                const response = await fetch(`http://localhost:8000/orders/${userId}`);
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Failed to fetch orders');
                }
                const responseData: OrdersApiResponse = await response.json();
                console.log("Orders received from API:", responseData);
                
                if (responseData && Array.isArray(responseData.data)) {
                    setOrders(responseData.data);
                } else {
                    // Handle cases where data is present but empty
                    if (responseData && responseData.data === null) {
                        setOrders([]);
                    } else {
                        throw new Error("Order data is missing or invalid in the API response.");
                    }
                }

            } catch (err: any) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchOrders(); // Initial fetch
        const interval = setInterval(fetchOrders, 10000); // Poll every 10 seconds

        return () => clearInterval(interval); // Cleanup on component unmount
    }, [userId]);

    if (loading) {
        return <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}><CircularProgress /></Box>;
    }

    if (error) {
        return <Typography color="error" sx={{ my: 2 }}>Error: {error}</Typography>;
    }

    return (
        <Box sx={{ my: 4 }}>
            <Typography variant="h5" gutterBottom>Recent Orders</Typography>
            <TableContainer component={Paper} variant="outlined">
                <Table sx={{ minWidth: 650 }} aria-label="simple table">
                    <TableHead>
                        <TableRow>
                            <TableCell>Order ID</TableCell>
                            <TableCell>Security ID</TableCell>
                            <TableCell>Type</TableCell>
                            <TableCell>Qty</TableCell>
                            <TableCell>Price</TableCell>
                            <TableCell>Status</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {orders.length > 0 ? orders.map((order) => (
                            <TableRow key={order.orderId}>
                                <TableCell>{order.orderId}</TableCell>
                                <TableCell>{order.securityId}</TableCell>
                                <TableCell>
                                    <Typography sx={{ fontWeight: 'bold', color: order.transactionType === 'BUY' ? 'success.main' : 'error.main' }}>
                                        {order.transactionType}
                                    </Typography>
                                </TableCell>
                                <TableCell>{order.quantity}</TableCell>
                                <TableCell>₹{order.price.toFixed(2)}</TableCell>
                                <TableCell>
                                    <Chip label={order.orderStatus} color={getStatusChipColor(order.orderStatus)} size="small" />
                                </TableCell>
                            </TableRow>
                        )) : (
                            <TableRow>
                                <TableCell colSpan={6} align="center">No recent orders found.</TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </TableContainer>
        </Box>
    );
};

export default Orders;