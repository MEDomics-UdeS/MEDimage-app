import { Dropdown } from 'primereact/dropdown';
import { InputNumber } from 'primereact/inputnumber';
import { InputSwitch } from 'primereact/inputswitch';
import { InputText } from 'primereact/inputtext';
import { useState } from 'react';
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
const RadiomicsLearner = ({ id, data, type }) => {
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
            {/* Show segmentation warning when there is no roisList or the roisList is empty */}
            <Row className="form-group-box" style={{ maxHeight: "400px", overflowY: "auto", overflowX: "hidden", paddingRight: "8px" }}>
              {/* Model type */}
              <Form.Group controlId="algo" style={{ marginBottom: "16px" }}>
              <Form.Label className="algo">Algorithm</Form.Label>
              <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>Learning algorithm for model training.</p>
                <Dropdown 
                    value={data.setupParam.possibleSettings.defaultSettings.model}
                    options={[{ name: 'XGBoost' }]}
                    optionLabel="name" 
                    placeholder={data.setupParam.possibleSettings.defaultSettings.model}
                    onChange={(event) => {
                      data.setupParam.possibleSettings.defaultSettings.model = event.target.value.name;
                      data.internal.settings.model = event.target.value.name;
                      updateHasWarning(data);
                      setReload(!reload);
                    }} 
                />
              </Form.Group>

              {/* varImportanceThreshold */}
              <Form.Group controlId="varImportanceThreshold" style={{ marginBottom: "16px" }}>
              <Form.Label className="varImportanceThreshold">Variable Importance Threshold</Form.Label>
              <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>Higher threshold keeps fewer important variables in the model.</p>
                <InputNumber
                    style={{width: "300px"}}
                    buttonLayout="horizontal"
                    value={data.setupParam.possibleSettings.defaultSettings.XGBoost.varImportanceThreshold}
                    onValueChange={(event) => {
                        data.setupParam.possibleSettings.defaultSettings.XGBoost.varImportanceThreshold = event.target.value;
                        data.internal.settings.XGBoost.varImportanceThreshold = event.target.value;
                        updateHasWarning(data);
                        setReload(!reload);
                    }}
                    mode="decimal"
                    showButtons
                    min={0.01}
                    max={0.99}
                    step={0.01}
                    maxFractionDigits={2}
                    incrementButtonClassName="p-button-info"
                    decrementButtonClassName='p-button-info'
                />
              </Form.Group>

              {/* optimizeThreshold */}
              <Form.Group controlId="optimizeThreshold" style={{ marginBottom: "16px" }}>
                <Form.Label className="optimizeThreshold">Model's Optimize Threshold</Form.Label>
                <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>
                  Identify the best probability cutoff.
                </p>
                <InputSwitch 
                  checked={data.setupParam.possibleSettings.defaultSettings.XGBoost.optimizeThreshold}
                  onChange={(event) => {
                    data.setupParam.possibleSettings.defaultSettings.XGBoost.optimizeThreshold = event.target.value;
                    data.internal.settings.XGBoost.optimizeThreshold = event.target.value;
                    updateHasWarning(data);
                    setReload(!reload);
                  }}
                />
              </Form.Group>

              {/* nameSave */}
              <Form.Group controlId="nameSave" style={{ marginBottom: "16px" }}>
              <Form.Label className="nameSave">Model's Save Name</Form.Label>
              <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>Name for saving the trained model.</p>
                <InputText
                    key="nameSaveModel"
                    style={{width: "300px"}}
                    value={data.setupParam.possibleSettings.defaultSettings.XGBoost.nameSave}
                    placeholder={data.setupParam.possibleSettings.defaultSettings.XGBoost.nameSave}
                    onChange={(event) => {
                      data.setupParam.possibleSettings.defaultSettings.XGBoost.nameSave = event.target.value;
                      console.log("data.internal.settings.XGBoost: ", data.internal.settings);
                      data.internal.settings.XGBoost.nameSave = event.target.value;
                      updateHasWarning(data);
                      setReload(!reload);
                    }}
                />
              </Form.Group>

              {/* optimizationMetric */}
              <Form.Group controlId="optimizationMetric" style={{ marginBottom: "16px" }}>
              <Form.Label className="optimizationMetric">Optimization Metric</Form.Label>
              <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>Performance metric used when tuning with PyCaret.</p>
              <InputText
                    key="optimizationMetric"
                    style={{width: "300px"}}
                    value={data.setupParam.possibleSettings.defaultSettings.XGBoost.optimizationMetric}
                    placeholder={data.setupParam.possibleSettings.defaultSettings.XGBoost.optimizationMetric}
                    onChange={(event) => {
                      data.setupParam.possibleSettings.defaultSettings.XGBoost.optimizationMetric = event.target.value;
                      data.internal.settings.XGBoost.optimizationMetric = event.target.value;
                      updateHasWarning(data);
                      setReload(!reload);
                    }} 
                />
              </Form.Group>

              {/* Seed */}
              <Form.Group controlId="seed" style={{ marginBottom: "16px" }}>
              <Form.Label className="seed">Random Seed</Form.Label>
              <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>Seed value for reproducible random number generation.</p>
                <InputNumber
                    style={{width: "300px"}}
                    buttonLayout="horizontal"
                    value={data.setupParam.possibleSettings.defaultSettings.XGBoost.seed}
                    onValueChange={(event) => {
                        data.setupParam.possibleSettings.defaultSettings.XGBoost.seed = event.target.value;
                        data.internal.settings.XGBoost.seed = event.target.value;
                        updateHasWarning(data);
                        setReload(!reload);
                    } }
                    mode="decimal"
                    min={1}
                />

              </Form.Group>
            </Row>
          </>
        }
      />
    </>
  )
}

export default RadiomicsLearner
