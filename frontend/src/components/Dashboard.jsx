import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const Dashboard = () => {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await axios.get('/api/attendance/stats')
      setStats(response.data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading">Loading...</div>
  }

  return (
    <div>
      <h1>Dashboard</h1>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '30px' }}>
        <div className="card">
          <h3>Total Users</h3>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#007bff' }}>
            {stats?.total_users || 0}
          </p>
        </div>
        <div className="card">
          <h3>Total Records</h3>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#28a745' }}>
            {stats?.total_records || 0}
          </p>
        </div>
      </div>

      {stats?.daily_stats && stats.daily_stats.length > 0 && (
        <div className="card">
          <h2>Daily Attendance Trend</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stats.daily_stats}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#007bff" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}

export default Dashboard
