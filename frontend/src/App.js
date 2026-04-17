import './App.css';
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

import ReactGA from 'react-ga4';
const TRACKING_ID = 'G-GRRHPDLTTM'; 
ReactGA.initialize(TRACKING_ID);

import ProductManagement from './database/ProductManagement';
import Container from 'react-bootstrap/Container';

function App() {
  return (
      <Router>
        <Container className='d-flex w-100 h-100 mx-auto flex-column align-items-center'>
          <Routes>
            <Route exact path='/' element={<ProductManagement />} />
            <Route path='/database' element={<ProductManagement />} />
            {/* Redirect any other unknown routes to home */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
         </Container>
      </Router>
  );
}

export default App;
