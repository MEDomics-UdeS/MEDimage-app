import React from "react"
import Node from "../../flow/node"
import { Form, Row, Col } from "react-bootstrap"
import { InputText } from 'primereact/inputtext';
import {useState} from 'react';
import { Dropdown } from 'primereact/dropdown';


/**
 * @param {string} id id of the node
 * @param {object} data data of the node
 * @param {string} type type of the node
 * @returns {JSX.Element} A SegmentationNode node
 *
 * @description
 * This component is used to display a SegmentationNode node.
 * it handles the display of the node and the modal
 */
const Normalization = ({ id, data, type }) => {  
  const [reload, setReload] = useState(false);

  return (
    <>
      <Node
        key={id}
        id={id}
        data={data}
        type={type}
        setupParam={data.setupParam}
        nodeSpecific={
          <>
            <Row className="form-group-box" style={{ textAlign: "center", alignItems: "center", justifyContent: "center" }}>
              {/* Method */}
              <Form.Group controlId="normMethod">
              <Form.Label className="normMethod">Normalization Method</Form.Label>
              <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>Method used to harmonize feature distributions across datasets.</p>
                <Dropdown 
                    style={{width: "300px"}}
                    value={data.setupParam.possibleSettings.defaultSettings.method}
                    options={[{ name: 'combat' }]}
                    optionLabel="name" 
                    placeholder={data.setupParam.possibleSettings.defaultSettings.method}
                    onChange={(event) => {
                      data.setupParam.possibleSettings.defaultSettings.method = event.target.value.name;
                      data.internal.settings.method = event.target.value.name;
                      setReload(!reload);
                    }} 
                />
              </Form.Group>
            </Row>
          </>
        }
      />
    </>
  )
}

export default Normalization
