import React, { useState } from "react";
import "./uploader.css";
import { BsFillCloudArrowDownFill } from "react-icons/bs";
import { FaFileAlt, FaCheck } from "react-icons/fa"; // Import FaCheck icon

function Uploader() {
  const [files, setFiles] = useState([]); // State to keep track of uploaded files
  const [dragging, setDragging] = useState(false); // State to track drag events

  const handleFormClick = () => {
    document.querySelector(".input-field").click();
  };

  const handleUpload = (e) => {
    const uploadedFiles = e.target.files;
    if (uploadedFiles.length === 0) {
      console.log("No file selected");
      return;
    }

    // Update the files state with uploaded files
    setFiles((prevFiles) => [...prevFiles, ...Array.from(uploadedFiles)]);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragging(true);
  };

  const handleDragEnter = (e) => {
    e.preventDefault();
    setDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);

    const droppedFiles = e.dataTransfer.files;

    // Update the files state with dropped files
    setFiles((prevFiles) => [...prevFiles, ...Array.from(droppedFiles)]);
  };

  return (
    <main>
      <nav> </nav>
      <header> Upload Files </header>
      <div>
        <div
          className={`wrapper1 ${dragging ? "dragover" : ""}`}
          onDragOver={handleDragOver}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <form action="" onClick={handleFormClick}>
            <input
              type="file"
              className="input-field"
              multiple // Allow multiple file selection
              onChange={handleUpload}
              hidden
            />
            <BsFillCloudArrowDownFill color="BEDBE8" size={100} />
            <h3> Drop your files here or Browse </h3>
          </form>
        </div>

        <div className="wrapper2">
          <section className="file-section">
            {files.map((uploadedFile, index) => (
              <div className="uploaded-file" key={index}>
                <FaFileAlt color="blue" size={24} />
                <span>{uploadedFile.name}</span>
                <FaCheck color="green" size={18} />
              </div>
            ))}
          </section>
        </div>
      </div>
    </main>
  );
}

export default Uploader;
