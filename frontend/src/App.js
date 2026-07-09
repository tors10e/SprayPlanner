import './App.css';
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

import ReactGA from 'react-ga4';
const TRACKING_ID = 'G-GRRHPDLTTM'; 
ReactGA.initialize(TRACKING_ID);

import ProductManagement from './database/ProductManagement';
import SprayHistory from './database/SprayHistory';
import SprayPlanner from './database/SprayPlanner';
import SprayReports from './database/SprayReports';
import Container from 'react-bootstrap/Container';

function App() {
  return (
      <Router>
        <Container fluid className='d-flex w-100 h-100 mx-auto flex-column align-items-center px-5'>
          <Routes>
            <Route exact path='/' element={<ProductManagement />} />
            <Route path='/spray-products' element={<ProductManagement />} />
            <Route path='/history' element={<SprayHistory />} />
            <Route path='/planner' element={<SprayPlanner />} />
            <Route path='/reports' element={<SprayReports />} />
            {/* Redirect any other unknown routes to home */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
         </Container>
      </Router>
  );
}

export default App;
