import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { format } from 'date-fns'

const AttendanceReports = () => {
  const [attendances, setAttendances] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    start_date: '',
    end_date: '',
    user_id: ''
  })

  useEffect(() => {
    fetchAttendances()
  }, [])

  const fetchAttendances = async () => {
    try {
      const params = new URLSearchParams()
      if (filters.start_date) params.append('start_date', filters.start_date)
      if (filters.end_date) params.append('end_date', filters.end_date)
      if (filters.user_id) params.append('user_id', filters.user_id)

      const response = await axios.get(`/api/attendance?${params.toString()}`)
      setAttendances(response.data.attendances)
    } catch (error) {
      console.error('Error fetching attendances:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleFilterChange = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value
    })
  }

  const applyFilters = () => {
    setLoading(true)
    fetchAttendances()
  }

  const exportCSV = async () => {
    try {
      const params = new URLSearchParams()
      if (filters.start_date) params.append('start_date', filters.start_date)
      if (filters.end_date) params.append('end_date', filters.end_date)

      const response = await axios.get(`/api/attendance/export/csv?${params.toString()}`, {
        responseType: 'blob'
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setDownload('attendance_report.csv')
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Error exporting CSV:', error)
    }
  }

  const exportPDF = async () => {
    try {
      const params = new URLSearchParams()
      if (filters.start_date) params.append('start_date', filters.start_date)
      if (filters.end_date) params.append('end_date', filters.end_date)

      const response = await axios.get(`/api/attendance/export/pdf?${params.toString()}`, {
        responseType: 'blob'
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setDownload('attendance_report.pdf')
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Error exporting PDF:', error)
    }
  }

  if (loading) {
    return <div className="loading">Loading...</div>
  }

  return (
    <div>
      <h1>Attendance Reports</h1>
      
      <div className="card">
        <h2>Filters</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
          <div className="form-group">
            <label>Start Date</label>
            <input
              type="date"
              name="start_date"
              value={filters.start_date}
              onChange={handleFilterChange}
            />
          </div>
          <div className="form-group">
            <label>End Date</label>
            <input
              type="date"
              name="end_date"
              value={filters.end_date}
              onChange={handleFilterChange}
            />
          </div>
          <div className="form-group">
            <label>User ID</label>
            <input
              type="number"
              name="user_id"
              value={filters.user_id}
              onChange={handleFilterChange}
              placeholder="Optional"
            />
          </div>
        </div>
        <button onClick={applyFilters} className="btn btn-primary" style={{ marginTop: '10px' }}>
          Apply Filters
        </button>
        <div style={{ marginTop: '15px' }}>
          <button onClick={exportCSV} className="btn btn-success" style={{ marginRight: '10px' }}>
            Export CSV
          </button>
          <button onClick={exportPDF} className="btn btn-success">
            Export PDF
          </button>
        </div>
      </div>

      <div className="card">
        <h2>Attendance Records ({attendances.length})</h2>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Email</th>
              <th>Barcode ID</th>
              <th>Date</th>
              <th>Time</th>
              <th>Confidence</th>
              <th>Method</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {attendances.length === 0 ? (
              <tr>
                <td colSpan="9" style={{ textAlign: 'center' }}>No records found</td>
              </tr>
            ) : (
              attendances.map((att) => (
                <tr key={att.id}>
                  <td>{att.id}</td>
                  <td>{att.user_name}</td>
                  <td>{att.user_email}</td>
                  <td>{att.barcode_id}</td>
                  <td>{format(new Date(att.attendance_date), 'yyyy-MM-dd')}</td>
                  <td>{format(new Date(att.attendance_date), 'HH:mm:ss')}</td>
                  <td>{att.face_match_confidence ? att.face_match_confidence.toFixed(2) : 'N/A'}</td>
                  <td>{att.verification_method}</td>
                  <td>{att.status}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default AttendanceReports
