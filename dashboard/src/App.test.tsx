import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders dashboard header', () => {
  render(<App />);
  const headerElement = screen.getByText(/InfinityAI Trading Dashboard/i);
  expect(headerElement).toBeInTheDocument();
});
