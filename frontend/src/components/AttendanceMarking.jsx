import React, { useState, useRef } from 'react'
import axios from 'axios'

const AttendanceMarking = () => {
  const [barcodeData, setBarcodeData] = useState('')
  const [file, setFile] = useState(null)
  const [message, setMessage] = useState({ type: '', text: '' })
  const [loading, setLoading] = useState(false)
  const [preview, setPreview] = useState(null)
  const fileInputRef = useRef(null)
  const videoRef = useRef(null)
  const [stream, setStream] = useState(null)
  const [capturing, setCapturing] = useState(false)

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      setFile(selectedFile)
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result)
      }
      reader.readAsDataURL(selectedFile)
    }
  }

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true })
      setStream(mediaStream)
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Could not access camera' })
    }
  }

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null
    }
  }

  const capturePhoto = () => {
    if (videoRef.current) {
      const canvas = document.createElement('canvas')
      canvas.width = videoRef.current.videoWidth
      canvas.height = videoRef.current.videoHeight
      const ctx = canvas.getContext('2d')
      ctx.drawImage(videoRef.current, 0, 0)
      canvas.toBlob((blob) => {
        const file = new File([blob], 'capture.jpg', { type: 'image/jpeg' })
        setFile(file)
        setPreview(canvas.toDataURL())
        setCapturing(true)
        stopCamera()
      }, 'image/jpeg')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) {
      setMessage({ type: 'error', text: 'Please select or capture an image' })
      return
    }

    setLoading(true)
    setMessage({ type: '', text: '' })

    try {
      const formDataToSend = new FormData()
      formDataToSend.append('face_image', file)
      if (barcodeData) {
        formDataToSend.append('barcode_data', barcodeData)
      }

      const endpoint = barcodeData 
        ? '/api/attendance/mark-with-barcode'
        : '/api/attendance/mark'

      if (barcodeData) {
        formDataToSend.append('barcode_data', barcodeData)
      }

      const response = await axios.post(endpoint, formDataToSend, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      setMessage({ 
        type: 'success', 
        text: `Attendance marked successfully for ${response.data.attendance.user_name}!` 
      })
      setBarcodeData('')
      setFile(null)
      setPreview(null)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Attendance marking failed'
      })
    } finally {
      setLoading(false)
      setCapturing(false)
    }
  }

  return (
    <div>
      <h1>Mark Attendance</h1>
      <div className="card">
        {message.text && (
          <div className={`alert alert-${message.type === 'success' ? 'success' : 'error'}`}>
            {message.text}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Barcode ID (Optional - for dual verification)</label>
            <input
              type="text"
              value={barcodeData}
              onChange={(e) => setBarcodeData(e.target.value)}
              placeholder="Scan or enter barcode ID"
            />
          </div>

          <div className="form-group">
            <label>Face Image</label>
            <div style={{ marginBottom: '10px' }}>
              {!stream && (
                <button type="button" className="btn btn-primary" onClick={startCamera}>
                  Use Camera
                </button>
              )}
              {stream && (
                <div>
                  <video ref={videoRef} autoPlay style={{ width: '100%', maxWidth: '400px', marginBottom: '10px' }} />
                  <button type="button" className="btn btn-success" onClick={capturePhoto}>
                    Capture Photo
                  </button>
                  <button type="button" className="btn btn-danger" onClick={stopCamera} style={{ marginLeft: '10px' }}>
                    Stop Camera
                  </button>
                </div>
              )}
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileChange}
            />
            {preview && (
              <div style={{ marginTop: '10px' }}>
                <img src={preview} alt="Preview" style={{ maxWidth: '300px', borderRadius: '4px' }} />
              </div>
            )}
          </div>

          <button type="submit" className="btn btn-success" disabled={loading || capturing}>
            {loading ? 'Marking Attendance...' : 'Mark Attendance'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default AttendanceMarking
