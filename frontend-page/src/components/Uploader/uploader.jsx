import React from "react";
import "./uploader.css";
import { BsFillCloudArrowDownFill } from "react-icons/bs";
import { FaFileAlt } from "react-icons/fa";

import { useState } from "react";

function Uploader() {
  const handleFormClick = () => {
    document.querySelector(".input-field").click();
  };

  return (
    <main>
      <nav> </nav>
      <header> Upload Files </header>
      <div>
        <div className="wrapper1">
          <form action="" onClick={handleFormClick}>
            <input
              type="file"
              accept="image/*"
              className="input-field"
              hidden
            />
            <BsFillCloudArrowDownFill color="BEDBE8" size={100} />
            <h3> Drop file your files here. or Browse </h3>
          </form>
        </div>
        <div className="wrapper2">
          <section></section>
        </div>
      </div>
    </main>
  );
  h;
}
export default Uploader;
