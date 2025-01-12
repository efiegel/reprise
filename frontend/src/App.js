import React, { useEffect, useState } from 'react';
import './App.css';

function App() {
  const [motifs, setMotifs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetch('http://127.0.0.1:5000/motifs')
      .then(response => response.json())
      .then(data => {
        setMotifs(data);
        setIsLoading(false);
      })
      .catch(error => {
        console.error('Error fetching motifs:', error);
        setIsLoading(false);
      });
  }, []);

  const handleChange = (uuid, content) => {
    setMotifs(motifs.map(motif => (motif.uuid === uuid ? { ...motif, content } : motif)));
  };

  const handleSave = (uuid, content) => {
    fetch(`http://127.0.0.1:5000/motifs/${uuid}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content }),
    })
      .then(response => response.json())
      .then(data => {
        console.log('Motif updated:', data);
      })
      .catch(error => {
        console.error('Error updating motif:', error);
      });
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Reprise</h1>
        <ul>
          {motifs.map(motif => (
            <li key={motif.uuid}>
              <input
                type="text"
                value={motif.content}
                onChange={e => handleChange(motif.uuid, e.target.value)}
              />
              <button onClick={() => handleSave(motif.uuid, motif.content)}>Save</button>
            </li>
          ))}
        </ul>
      </header>
    </div>
  );
}

export default App;