import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import Login from './Login';
import reportWebVitals from './reportWebVitals';

const root = ReactDOM.createRoot(document.getElementById('root'));

function Root() {
  const [loggedIn, setLoggedIn] = React.useState(!!localStorage.getItem('token'));
  return (
    <React.StrictMode>
      {loggedIn ? <App /> : <Login onLogin={() => setLoggedIn(true)} />}
    </React.StrictMode>
  );
}

root.render(<Root />);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
