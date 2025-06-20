import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import AdminDashboard from './components/AdminDashboard';
import StudentDashboard from './components/StudentDashboard';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <nav className="navbar navbar-expand-lg navbar-light bg-light">
          <div className="container">
            <a className="navbar-brand" href="/">نظام الاختبارات التفاعلية</a>
            <div className="navbar-nav">
              <a className="nav-link" href="/">الطالب</a>
              <a className="nav-link" href="/admin">المشرف</a>
            </div>
          </div>
        </nav>
        <Routes>
          <Route path="/" element={<StudentDashboard />} />
          <Route path="/admin" element={<AdminDashboard />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
