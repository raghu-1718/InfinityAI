import React from 'react';

function FundBalance({ balance }) {
  return (
    <div style={{ marginTop: '20px' }}>
      <h3>Fund Balance</h3>
      <p>{balance !== undefined ? `$${balance.toFixed(2)}` : 'Balance not available'}</p>
    </div>
  );
}

export default FundBalance;