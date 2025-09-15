import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography, Box, CircularProgress, Stack, Divider } from '@mui/material';

interface FundData {
    dhanClientId: string;
    availabelBalance: number;
    withdrawableBalance: number;
    utilizedAmount: number;
}

interface ApiResponse {
    data: FundData;
}

const FundBalance: React.FC = () => {
    const [funds, setFunds] = useState<FundData | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState<boolean>(true);

    const userId = 'raghu_test_1'; 

    useEffect(() => {
        const fetchFunds = async () => {
            setLoading(true);
            try {
                const response = await fetch(`http://localhost:8000/funds/${userId}`);
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Failed to fetch funds');
                }
                
                const responseData: ApiResponse = await response.json();
                
                if (responseData && responseData.data) {
                    setFunds(responseData.data);
                    setError(null);
                } else {
                    throw new Error("Fund data is missing or invalid in API response.");
                }

            } catch (err: any) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchFunds();
        const interval = setInterval(fetchFunds, 10000); 

        return () => clearInterval(interval);
    }, [userId]);

    if (loading && !funds) {
        return <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}><CircularProgress /></Box>;
    }

    if (error) {
        return <Typography color="error" sx={{ my: 2 }}>Error: {error}</Typography>;
    }

    return (
        <Box sx={{ my: 2 }}>
            <Typography variant="h5" gutterBottom>Fund Balance</Typography>
            <Card variant="outlined">
                <CardContent>
                    <Stack 
                        direction={{ xs: 'column', sm: 'row' }}
                        divider={<Divider orientation="vertical" flexItem />}
                        spacing={{ xs: 1, sm: 2 }}
                        justifyContent="space-around"
                    >
                        <Box sx={{ flexGrow: 1, textAlign: 'center' }}>
                            <Typography variant="body2" color="text.secondary">Client ID</Typography>
                            <Typography variant="h6">{funds?.dhanClientId}</Typography>
                        </Box>
                        <Box sx={{ flexGrow: 1, textAlign: 'center' }}>
                            <Typography variant="body2" color="text.secondary">Available Balance</Typography>
                            <Typography variant="h6" color="green">₹{funds?.availabelBalance.toFixed(2)}</Typography>
                        </Box>
                        <Box sx={{ flexGrow: 1, textAlign: 'center' }}>
                            <Typography variant="body2" color="text.secondary">Utilized Amount</Typography>
                            <Typography variant="h6" color="orange">₹{funds?.utilizedAmount.toFixed(2)}</Typography>
                        </Box>
                        <Box sx={{ flexGrow: 1, textAlign: 'center' }}>
                            <Typography variant="body2" color="text.secondary">Withdrawable Balance</Typography>
                            <Typography variant="h6">₹{funds?.withdrawableBalance.toFixed(2)}</Typography>
                        </Box>
                    </Stack>
                </CardContent>
            </Card>
        </Box>
    );
};

export default FundBalance;