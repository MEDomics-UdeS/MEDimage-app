import React from "react"
import Node from "../../flow/node"
import { Form, Row } from "react-bootstrap"
import { InputText } from 'primereact/inputtext';
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
              <Form.Group controlId="algo">
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
              <Form.Group controlId="varImportanceThreshold">
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

              {/* optimalThreshold */}
              <Form.Group controlId="optimalThreshold">
              <Form.Label className="optimalThreshold">Model's Optimal Threshold</Form.Label>
              <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>Decision threshold for predictions. Leave empty for automatic calculation.</p>
                <InputNumber
                    style={{width: "300px"}}
                    buttonLayout="horizontal"
                    value={data.setupParam.possibleSettings.defaultSettings.XGBoost.optimalThreshold}
                    onValueChange={(event) => {
                        data.setupParam.possibleSettings.defaultSettings.XGBoost.optimalThreshold = event.target.value;
                        data.internal.settings.XGBoost.optimalThreshold = event.target.value;
                        updateHasWarning(data);
                        setReload(!reload);
                    }}
                    placeholder="None"
                    mode="decimal"
                    showButtons
                    min={0.00}
                    max={0.99}
                    maxFractionDigits={2}
                    step={0.01}
                    incrementButtonClassName="p-button-info"
                    decrementButtonClassName='p-button-info'
                    allowEmpty={true}
                />
              </Form.Group>

              {/* nameSave */}
              <Form.Group controlId="nameSave">
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
              <Form.Group controlId="optimizationMetric">
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

              {/* method */}
              <Form.Group controlId="method">
              <Form.Label className="method">Parameters Tuning Method</Form.Label>
              <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>Strategy for hyperparameter optimization.</p>
                <Dropdown 
                    style={{width: "300px"}}
                    value={data.setupParam.possibleSettings.defaultSettings.XGBoost.method}
                    options={[{ name: 'PyCaret' }, { name: 'grid_search' }, { name: 'random_search' }]}
                    optionLabel="name" 
                    placeholder={data.setupParam.possibleSettings.defaultSettings.XGBoost.method}
                    onChange={(event) => {
                      data.setupParam.possibleSettings.defaultSettings.XGBoost.method = event.target.value.name;
                      data.internal.settings.XGBoost.method = event.target.value.name;
                      updateHasWarning(data);
                      setReload(!reload);
                    }} 
                />
              </Form.Group>


              {/* Seed */}
              <Form.Group controlId="seed">
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
