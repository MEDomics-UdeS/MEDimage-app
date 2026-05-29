import React from "react"
import Node from "../../flow/node"
import { Form, Row } from "react-bootstrap"
import {useState} from 'react';
import { Dropdown } from 'primereact/dropdown';
import { InputNumber } from 'primereact/inputnumber';
import { updateHasWarning } from "../../flow/node";


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
const Cleaning = ({ id, data, type }) => {

  const [reload, setReload] = useState(false);
  const sectionStyle = {
    marginBottom: "16px",
    paddingBottom: "12px",
    borderBottom: "1px solid rgba(0, 0, 0, 0.08)"
  }
  const lastSectionStyle = { marginBottom: "16px" }

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
              {/* missingCutoffps */}
              <Form.Group controlId="missingCutoffps" style={sectionStyle}>
              <Form.Label className="missingCutoffps">Missing Cut Off/Sample</Form.Label>
              <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>Maximum percentage of missing features allowed per sample.</p>
                <InputNumber
                    style={{width: "300px"}}
                    buttonLayout="horizontal"
                    value={data.setupParam.possibleSettings.defaultSettings.default.feature.continuous.missingCutoffps}
                    onValueChange={(event) => {
                      data.setupParam.possibleSettings.defaultSettings.default.feature.continuous.missingCutoffps = event.target.value;
                        updateHasWarning(data);
                        setReload(!reload);
                    }}
                    mode="decimal"
                    showButtons
                    min={0.01}
                    max={0.99}
                    step={0.01}
                    minFractionDigits={2}
                    incrementButtonClassName="p-button-info"
                    decrementButtonClassName='p-button-info' 
                />
              </Form.Group>

              {/* missingCutoffpf */}
              <Form.Group controlId="missingCutoffpf" style={sectionStyle}>
              <Form.Label className="missingCutoffpf">Missing Patients Cut Off/Feature</Form.Label>
              <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>Maximum percentage of missing samples allowed per feature.</p>
                <InputNumber
                    style={{width: "300px"}}
                    buttonLayout="horizontal"
                    value={data.setupParam.possibleSettings.defaultSettings.default.feature.continuous.missingCutoffpf}
                    onValueChange={(event) => {
                      data.setupParam.possibleSettings.defaultSettings.default.feature.continuous.missingCutoffpf = event.target.value;
                      updateHasWarning(data);
                      setReload(!reload);
                    }}
                    mode="decimal"
                    showButtons
                    min={0.01}
                    max={0.99}
                    step={0.01}
                    minFractionDigits={2}
                    incrementButtonClassName="p-button-info"
                    decrementButtonClassName='p-button-info' 
                />
              </Form.Group>

              {/* covCutoff */}
              <Form.Group controlId="covCutoff" style={sectionStyle}>
                <Form.Label className="covCutoff">Minimum Variation Percentage</Form.Label>
                <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>
                  Minimum coefficient of variation threshold to retain features.
                </p>
                <InputNumber
                    style={{width: "300px"}}
                    buttonLayout="horizontal"
                    value={data.setupParam.possibleSettings.defaultSettings.default.feature.continuous.covCutoff}
                    onValueChange={(event) => {
                      data.setupParam.possibleSettings.defaultSettings.default.feature.continuous.covCutoff = event.target.value;
                      updateHasWarning(data);
                      setReload(!reload);
                    }}
                    mode="decimal"
                    showButtons
                    min={0.01}
                    max={0.99}
                    step={0.01}
                    minFractionDigits={2}
                    incrementButtonClassName="p-button-info"
                    decrementButtonClassName='p-button-info' 
                />
              </Form.Group>

              {/* imputation */}
              <Form.Group controlId="imputation" style={lastSectionStyle}>
              <Form.Label className="imputation">Imputation Method</Form.Label>
              <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>Strategy for filling missing values in features.</p>
                <Dropdown 
                    style={{width: "300px"}}
                    value={data.setupParam.possibleSettings.defaultSettings.default.feature.continuous.imputation}
                    options={[{ name: 'random' }, { name: 'mean' }, {name: 'median'}]}
                    optionLabel="name" 
                    placeholder={data.setupParam.possibleSettings.defaultSettings.default.feature.continuous.imputation}
                    onChange={(event) => {
                      data.setupParam.possibleSettings.defaultSettings.default.feature.continuous.imputation = event.target.value.name;
                      updateHasWarning(data);
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

export default Cleaning
