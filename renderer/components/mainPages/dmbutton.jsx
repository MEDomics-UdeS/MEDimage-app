import React from "react"
import { Button } from "react-bootstrap";

const DataManagerButton = ({ reload, setReload }) => {

    const handleClick = () => {
        setReload(!reload);
    };

  return (
    <>
      <Button className="box-button" onClick={handleClick}>DataManager</Button>
    </>
  )
}

export default DataManagerButton