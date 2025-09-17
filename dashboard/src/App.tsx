import React from 'react';
import './App.css';
import Dashboard from './components/Dashboard';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={process.env.PUBLIC_URL + '/logo.svg'} alt="InfinityAI Logo" className="App-logo-fade" />
        <h1 className="App-title-fade">InfinityAI Trading Dashboard</h1>
      </header>
      <main>
        <Dashboard />
      </main>
    </div>
  );
}

export default App;

