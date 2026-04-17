import './App.css';
import React, {useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route}
  from 'react-router-dom';

import ReactGA from 'react-ga4';
const TRACKING_ID = 'G-GRRHPDLTTM'; 
ReactGA.initialize(TRACKING_ID);

import Home from './home/home';
import Events from './events/events';
import Weddings from './weddings/weddings';
import WeddingPricing from './weddings/wedding_pricing';
import Overnighting from './overnighting/overnighting';
import Store from './store/store';
import Trails from './trails/trails';
import Winery from './winery/winery';
import ProductManagement from './database/ProductManagement';
import Container from 'react-bootstrap/Container';
import { PhotoGallery } from './gallery/PhotoGallery';



function App() {
  return (
      <Router>
        <Container className='d-flex w-100 h-100 mx-auto flex-column align-items-center'>
          <Routes>
            <Route exact path='/' element={<Home />} />
            <Route path='/events' element={<Events />} />
            <Route path='/weddings' element={<Weddings />} />
            <Route path='/wedding-pricing' element={<WeddingPricing />} />
            <Route path='/overnighting' element={<Overnighting />} />
            <Route path='/store' element={<Store />} />
            <Route path='/trails' element={<Trails />} />
            <Route path='/gallery' element={<PhotoGallery/>} />
            <Route path='/winery' element={<Winery />} />
            <Route path='/database' element={<ProductManagement />} />
          </Routes>
         </Container>
      </Router>
  );
}


export default App;
