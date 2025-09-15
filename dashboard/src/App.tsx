import React from 'react';
import './App.css';
import FundBalance from './components/FundBalance';
// We can import other components here as we build them
import Orders from './components/Orders';
// import LiveTrading from './components/LiveTrading';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>InfinityAI Trading Dashboard</h1>
      </header>
      <main>
        <FundBalance />
        {/* We can add other components below */}
        <Orders />
        {/* <LiveTrading /> */}
      </main>
    </div>
  );
}

export default App;