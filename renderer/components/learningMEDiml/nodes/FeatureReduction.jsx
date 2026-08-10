import { Dropdown } from 'primereact/dropdown';
import { InputNumber } from 'primereact/inputnumber';
import { React, useEffect, useState } from "react";
import { Form, Row } from "react-bootstrap";
import Node, { updateHasWarning } from "../../flow/node";


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
const FeatureReduction = ({ id, data, type }) => {

  const [reload, setReload] = useState(false);
  const sectionStyle = {
    marginBottom: "16px",
    paddingBottom: "12px",
    borderBottom: "1px solid rgba(0, 0, 0, 0.08)"
  }
  const lastSectionStyle = { marginBottom: "16px" }

  useEffect(() => {
    if (!data.setupParam.possibleSettings.defaultSettings.FDA.minNfeat || 
      data.setupParam.possibleSettings.defaultSettings.FDA.minNfeat !== data.internal.settings.FDA.minNfeat
    ){
      data.setupParam.possibleSettings.defaultSettings.FDA.minNfeat = data.internal.settings.FDA.minNfeat
    }
    if (!data.setupParam.possibleSettings.defaultSettings.FDA.minNfeatInterCorr || 
      data.setupParam.possibleSettings.defaultSettings.FDA.minNfeatInterCorr !== data.internal.settings.FDA.minNfeatInterCorr
    ){
      data.setupParam.possibleSettings.defaultSettings.FDA.minNfeatInterCorr = data.internal.settings.FDA.minNfeatInterCorr
    }
    if (!data.setupParam.possibleSettings.defaultSettings.FDA.minNfeatStable || 
      data.setupParam.possibleSettings.defaultSettings.FDA.minNfeatStable !== data.internal.settings.FDA.minNfeatStable
    ){
      data.setupParam.possibleSettings.defaultSettings.FDA.minNfeatStable = data.internal.settings.FDA.minNfeatStable
    }
    if (!data.setupParam.possibleSettings.defaultSettings.FDA.nSplits || 
      data.setupParam.possibleSettings.defaultSettings.FDA.nSplits !== data.internal.settings.FDA.nSplits
    ){
      data.setupParam.possibleSettings.defaultSettings.FDA.nSplits = data.internal.settings.FDA.nSplits
    }
    if (!data.setupParam.possibleSettings.defaultSettings.FDA.corrType || 
      data.setupParam.possibleSettings.defaultSettings.FDA.corrType !== data.internal.settings.FDA.corrType
    ){
      data.setupParam.possibleSettings.defaultSettings.FDA.corrType = data.internal.settings.FDA.corrType
    }
    if (!data.setupParam.possibleSettings.defaultSettings.FDA.threshStableStart || 
      data.setupParam.possibleSettings.defaultSettings.FDA.threshStableStart !== data.internal.settings.FDA.threshStableStart
    ){
      data.setupParam.possibleSettings.defaultSettings.FDA.threshStableStart = data.internal.settings.FDA.threshStableStart
    }
    if (!data.setupParam.possibleSettings.defaultSettings.FDA.threshInterCorr || 
      data.setupParam.possibleSettings.defaultSettings.FDA.threshInterCorr !== data.internal.settings.FDA.threshInterCorr
    ){
      data.setupParam.possibleSettings.defaultSettings.FDA.threshInterCorr = data.internal.settings.FDA.threshInterCorr
    }
  }, [])

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
            <Row 
              className="form-group-box"
              style={{ maxHeight: "400px", overflowY: "auto", overflowX: "hidden", paddingRight: "8px" }}
            >
              {/* nSplits */}
              <Form.Group controlId="nSplits" style={sectionStyle}>
              <Form.Label className="nSplits">Number of Splits</Form.Label>
              <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>Number of splits for Feature Reduction.</p>
                <InputNumber
                    style={{width: "300px"}}
                    buttonLayout="horizontal"
                    value={data.setupParam.possibleSettings.defaultSettings.FDA.nSplits}
                    onValueChange={(event) => {
                      data.setupParam.possibleSettings.defaultSettings.FDA.nSplits = event.target.value;
                      data.internal.settings.FDA.nSplits = event.target.value;
                      updateHasWarning(data);
                      setReload(!reload);
                    }}
                    mode="decimal"
                    showButtons
                    min={1}
                    step={1}
                    incrementButtonClassName="p-button-info"
                    decrementButtonClassName='p-button-info' 
                />
              </Form.Group>

              {/* corrType */}
              <Form.Group controlId="corrType" style={sectionStyle}>
              <Form.Label className="corrType">Correlation Method</Form.Label>
              <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>Method to measure feature correlations.</p>
                <Dropdown 
                    style={{width: "300px"}}
                    value={data.setupParam.possibleSettings.defaultSettings.FDA.corrType}
                    options={[{ name: 'Spearman' }, { name: 'Pearson' }]}
                    optionLabel="name" 
                    placeholder={data.setupParam.possibleSettings.defaultSettings.FDA.corrType}
                    onChange={(event) => {
                      data.setupParam.possibleSettings.defaultSettings.FDA.corrType = event.target.value.name;
                      data.internal.settings.FDA.corrType = event.target.value.name;
                      updateHasWarning(data);
                      setReload(!reload);
                    }} 
                />
              </Form.Group>

              {/* threshStableStart */}
              <Form.Group controlId="threshStableStart" style={sectionStyle}>
              <Form.Label className="threshStableStart">Stability Threshold</Form.Label>
              <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>Minimum correlation threshold for features to be considered stable.</p>
                <InputNumber
                    style={{width: "300px"}}
                    buttonLayout="horizontal"
                    value={data.setupParam.possibleSettings.defaultSettings.FDA.threshStableStart}
                    onValueChange={(event) => {
                      data.setupParam.possibleSettings.defaultSettings.FDA.threshStableStart = event.target.value;
                      data.internal.settings.FDA.threshStableStart = event.target.value;
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
                    allowEmpty={false}
                />
              </Form.Group>

              {/* threshInterCorr */}
              <Form.Group controlId="threshInterCorr" style={sectionStyle}>
              <Form.Label className="threshInterCorr">Inter-Correlation Threshold</Form.Label>
              <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>Threshold for identifying redundant feature pairs.</p>
                <InputNumber
                    style={{width: "300px"}}
                    buttonLayout="horizontal"
                    value={data.setupParam.possibleSettings.defaultSettings.FDA.threshInterCorr}
                    onValueChange={(event) => {
                      data.setupParam.possibleSettings.defaultSettings.FDA.threshInterCorr = event.target.value;
                      data.internal.settings.FDA.threshInterCorr = event.target.value;
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
                    allowEmpty={false}
                />
              </Form.Group>

              {/* minNfeatStable */}
              <Form.Group controlId="minNfeatStable" style={sectionStyle}>
              <Form.Label className="minNfeatStable">Minimum Number of Stable Features</Form.Label>
              <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>Minimum stable features to retain after filtering.</p>
                <InputNumber
                    style={{width: "300px"}}
                    buttonLayout="horizontal"
                    value={data.setupParam.possibleSettings.defaultSettings.FDA.minNfeatStable}
                    onValueChange={(event) => {
                      data.setupParam.possibleSettings.defaultSettings.FDA.minNfeatStable = event.target.value;
                      data.internal.settings.FDA.minNfeatStable = event.target.value;
                      updateHasWarning(data);
                      setReload(!reload);
                    }}
                    mode="decimal"
                    showButtons
                    min={1}
                    step={1}
                    incrementButtonClassName="p-button-info"
                    decrementButtonClassName='p-button-info' 
                />
              </Form.Group>

              {/* minNfeatInterCorr */}
              <Form.Group controlId="minNfeatInterCorr" style={sectionStyle}>
              <Form.Label className="minNfeatInterCorr">Minimum Number of Inter-Correlated Features</Form.Label>
              <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>Minimum inter-correlated features to retain.</p>
                <InputNumber
                    style={{width: "300px"}}
                    buttonLayout="horizontal"
                    value={data.setupParam.possibleSettings.defaultSettings.FDA.minNfeatInterCorr}
                    onValueChange={(event) => {
                      data.setupParam.possibleSettings.defaultSettings.FDA.minNfeatInterCorr = event.target.value;
                      data.internal.settings.FDA.minNfeatInterCorr = event.target.value;
                      updateHasWarning(data);
                      setReload(!reload);
                    }}
                    mode="decimal"
                    showButtons
                    min={1}
                    step={1}
                    incrementButtonClassName="p-button-info"
                    decrementButtonClassName='p-button-info' 
                />
              </Form.Group>

              {/* minNfeat */}
              <Form.Group controlId="minNfeat" style={lastSectionStyle}>
              <Form.Label className="minNfeat">Final Number of Features</Form.Label>
              <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>Total features to use for model training.</p>
                <InputNumber
                    style={{width: "300px"}}
                    buttonLayout="horizontal"
                    value={data.setupParam.possibleSettings.defaultSettings.FDA.minNfeat}
                    onValueChange={(event) => {
                      data.setupParam.possibleSettings.defaultSettings.FDA.minNfeat = event.target.value;
                      data.internal.settings.FDA.minNfeat = event.target.value;
                      updateHasWarning(data);
                      setReload(!reload);
                    }}
                    mode="decimal"
                    showButtons
                    min={1}
                    step={1}
                    incrementButtonClassName="p-button-info"
                    decrementButtonClassName='p-button-info' 
                />
              </Form.Group>

            </Row>
          </>
        }
      />
    </>
  )
}

export default FeatureReduction
