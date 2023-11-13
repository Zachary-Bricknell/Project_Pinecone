import React from "react";
import "./uploader.css";
import { useState } from "react";

function Uploader() {
  const handleFormClick = () => {
    document.querySelector(".input-field").click();
  };

  return (
    <main>
      <form action="" onClick={handleFormClick}>
        <input type="file" accept="image/*" className="input-field" hidden />
      </form>
    </main>
  );
}
export default Uploader;
