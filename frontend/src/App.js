import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Schedule from './pages/Schedule';
import Classes from './pages/Classes';
import Homework from './pages/Homework';
import './index.css';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Schedule />} />
          <Route path="/classes" element={<Classes />} />
          <Route path="/homework" element={<Homework />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;