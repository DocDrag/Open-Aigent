import React, { useState, useEffect } from 'react';

const FileExplorer = ({ onFileSelect }) => {
    const [files, setFiles] = useState([]);
    const [loading, setLoading] = useState(false);

    const fetchFiles = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://127.0.0.1:8000/api/files');
            if (response.ok) {
                const data = await response.json();
                setFiles(data.files || []);
            }
        } catch (error) {
            console.error("Failed to fetch files", error);
        }
        setLoading(false);
    };

    useEffect(() => {
        fetchFiles();
        const interval = setInterval(fetchFiles, 8000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="file-explorer">
            <div className="explorer-header-row">
                <span>PROJECT FILES</span>
                <button className="refresh-btn" onClick={fetchFiles}>↻</button>
            </div>
            <div className="file-list-container">
                {files.map((file, i) => (
                    <div 
                        key={i} 
                        className={`file-row ${file.isDir ? 'is-dir' : 'is-file'}`}
                        onClick={() => !file.isDir && onFileSelect(file.path)}
                    >
                        <span className="icon">{file.isDir ? '📁' : '📄'}</span>
                        <span className="name">{file.name}</span>
                    </div>
                ))}
                {files.length === 0 && !loading && (
                    <div className="empty-msg">Workspace empty</div>
                )}
            </div>
        </div>
    );
};

export default FileExplorer;
