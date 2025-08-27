// /src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Dashboard } from './pages/Dashboard';
import { CustomerList } from './pages/CustomerList';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/customers" element={<CustomerList />} />
        <Route path="/customers/:id" element={<div>Customer Detail Page (TODO)</div>} />
        <Route path="/customers/:id/edit" element={<div>Customer Edit Page (TODO)</div>} />
        <Route path="/customers/new" element={<div>New Customer Page (TODO)</div>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;