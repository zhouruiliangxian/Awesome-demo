import React, { useState } from 'react';
import './App.css';

function App() {
    const [selectedFile, setSelectedFile] = useState(null);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleFileChange = (event) => {
        setSelectedFile(event.target.files[0]);
        setMessage('');
        setError('');
    };

    const handleUpload = async () => {
        if (!selectedFile) {
            setError('Please select a PDF file first.');
            return;
        }

        setIsLoading(true);
        setError('');
        setMessage('');

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const response = await fetch('http://localhost:5001/api/upload', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Something went wrong');
            }

            setMessage(`Success! File '${data.file_name}' uploaded to MinIO at ${data.minio_path}.`);
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="App">
            <header className="App-header">
                <h1>PDF Upload and Search Service</h1>
                <p>Upload a PDF to store it in MinIO and index its content in OpenSearch.</p>
                
                <div className="upload-container">
                    <input type="file" accept=".pdf" onChange={handleFileChange} />
                    <button onClick={handleUpload} disabled={isLoading}>
                        {isLoading ? 'Uploading...' : 'Upload PDF'}
                    </button>
                </div>

                {message && <p className="message success">{message}</p>}
                {error && <p className="message error">{error}</p>}

            </header>
        </div>
    );
}

export default App;