import React, { useState } from 'react'
import axios from 'axios'

const UserRegistration = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    barcode_id: ''
  })
  const [file, setFile] = useState(null)
  const [message, setMessage] = useState({ type: '', text: '' })
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage({ type: '', text: '' })

    try {
      const formDataToSend = new FormData()
      formDataToSend.append('name', formData.name)
      formDataToSend.append('email', formData.email)
      formDataToSend.append('barcode_id', formData.barcode_id)
      formDataToSend.append('face_image', file)

      const response = await axios.post('/api/users/register', formDataToSend, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      setMessage({ type: 'success', text: 'User registered successfully!' })
      setFormData({ name: '', email: '', barcode_id: '' })
      setFile(null)
      document.getElementById('file-input').value = ''
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Registration failed'
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1>Register New User</h1>
      <div className="card">
        {message.text && (
          <div className={`alert alert-${message.type === 'success' ? 'success' : 'error'}`}>
            {message.text}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Full Name</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Barcode ID</label>
            <input
              type="text"
              name="barcode_id"
              value={formData.barcode_id}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Face Image</label>
            <input
              id="file-input"
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              required
            />
            <small>Upload a clear face image (JPG, PNG)</small>
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Registering...' : 'Register User'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default UserRegistration
