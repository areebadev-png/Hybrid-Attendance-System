import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import Dashboard from './components/Dashboard'
import UserRegistration from './components/UserRegistration'
import AttendanceMarking from './components/AttendanceMarking'
import AttendanceReports from './components/AttendanceReports'
import './App.css'

function App() {
  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <h1>Hybrid Attendance System</h1>
          <Link to="/">Dashboard</Link>
          <Link to="/register">Register User</Link>
          <Link to="/mark">Mark Attendance</Link>
          <Link to="/reports">Reports</Link>
        </nav>
        <div className="container">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/register" element={<UserRegistration />} />
            <Route path="/mark" element={<AttendanceMarking />} />
            <Route path="/reports" element={<AttendanceReports />} />
          </Routes>
        </div>
      </div>
    </Router>
  )
}

export default App
