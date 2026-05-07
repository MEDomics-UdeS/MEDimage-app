import React from "react"
import Node from "../../flow/node"
import { Form, Row, Col } from "react-bootstrap"
import { InputText } from 'primereact/inputtext';
import {useState} from 'react';
import { Dropdown } from 'primereact/dropdown';
import { InputNumber } from 'primereact/inputnumber';
import { InputSwitch } from 'primereact/inputswitch';
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
const Design = ({ id, data, type }) => {  
  const [reload, setReload] = useState(false);

  return (
    <>
      <Node
        key={id}
        id={id}
        data={data}
        type={type}
        setupParam={data.setupParam}
        color={"#ffd36b"}
        nodeSpecific={
          <>
            <Row className="form-group-box" style={{ textAlign: "center", alignItems: "center", justifyContent: "center" }}>
              {/* Experiment Name */}
              <Form.Group controlId="expName">
              <Form.Label 
                  className="expName">
                      Experiment Name
              </Form.Label>
              <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>Unique identifier for the analysis experiment.</p>
                <InputText
                    style={{width: "300px", display: "block", margin: "0 auto"}}
                    value={data.internal.settings.expName || data.setupParam.possibleSettings.defaultSettings.expName}
                    placeholder="Ex: Problem_RadiomicsLevel_Modality"
                    onChange={(event) => {
                      data.setupParam.possibleSettings.defaultSettings.expName = event.target.value;
                      data.internal.settings.expName = event.target.value;
                      updateHasWarning(data);
                      setReload(!reload);
                    }}
                />
              </Form.Group>

              {/* Split Type */}
              <Form.Group controlId="splitType">
              <Form.Label 
                  className="splitType">
                      Split Type
              </Form.Label>
              <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>Choose method for splitting data into sets.</p>
                <Dropdown 
                    style={{width: "300px"}}
                    value={data.setupParam.possibleSettings.defaultSettings.active_method[0]}
                    options={[{ name: 'Random' }, { name: 'Institution' }, { name: 'Cross-Validation' }]}
                    optionLabel="name" 
                    placeholder={data.setupParam.possibleSettings.defaultSettings.active_method[0]}
                    onChange={(event) => {
                      if (event.target.value.name === "Cross-Validation") {
                        data.setupParam.possibleSettings.defaultSettings.active_method = ['cv'];
                        data.internal.settings.active_method = ['cv'];
                      } else {
                        data.setupParam.possibleSettings.defaultSettings.active_method = [event.target.value.name];
                        data.internal.settings.active_method = [event.target.value.name];
                      }
                      updateHasWarning(data);
                      setReload(!reload);
                    }} 
                />
              </Form.Group>

              {/* OTHER PARAMS IF SPLIT TYPE IS RANDOM */}
              {data.setupParam.possibleSettings.defaultSettings.active_method?.[0]?.toLowerCase() === "random" &&
              <>
              {/* Split Method */}
              <Form.Group controlId="splitMethod">
              <Form.Label 
                  className="splitMethod">
                      Split Method
              </Form.Label>
              <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>Algorithm for distributing samples into train/test sets.</p>
                <Dropdown 
                    style={{width: "300px", display: "block", margin: "0 auto"}}
                    value={data.setupParam.possibleSettings.defaultSettings.Random.method}
                    options={[{ name: 'SubSampling' }]}
                    optionLabel="name" 
                    placeholder={data.setupParam.possibleSettings.defaultSettings.Random.method}
                    onChange={(event) => {
                      data.setupParam.possibleSettings.defaultSettings.Random.method = event.target.value.name;
                      data.internal.settings.Random.method = event.target.value.name;
                      updateHasWarning(data);
                      setReload(!reload);
                    }} 
                        />
              </Form.Group>

              {/* Number of splits */}
              <Form.Group controlId="nSplits">
              <Form.Label 
                  className="nSplits">
                      Splits Number
              </Form.Label>
              <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>Total number of data partitions to create.</p>
                <InputNumber
                    style={{width: "300px", display: "block", margin: "0 auto"}}
                    buttonLayout="horizontal"
                    value={data.setupParam.possibleSettings.defaultSettings.Random.nSplits}
                    onValueChange={(event) => {
                      data.setupParam.possibleSettings.defaultSettings.Random.nSplits = event.target.value;
                      data.internal.settings.Random.nSplits = event.target.value;
                      updateHasWarning(data);
                      setReload(!reload);
                    }}
                    mode="decimal"
                    showButtons
                    min={1}
                    incrementButtonClassName="p-button-info"
                    decrementButtonClassName='p-button-info' 
                />

              </Form.Group>

              {/* Flag by institution or not */}
              <Form.Group controlId="stratifyInstitutions">
              <Form.Label 
                  className="stratifyInstitutions">
                      Flag by Institution
              </Form.Label>
              <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>Maintain institution representation in train/test.</p>
              <br></br>
                <InputSwitch 
                    checked={data.setupParam.possibleSettings.defaultSettings.Random.stratifyInstitutions} 
                    onChange={(event) => {
                        data.setupParam.possibleSettings.defaultSettings.Random.stratifyInstitutions = event.target.value;
                        data.internal.settings.Random.stratifyInstitutions = event.target.value;
                        updateHasWarning(data);
                        setReload(!reload);
                    }}
                />
              </Form.Group>

              {/* Test proportion */}
              <Form.Group controlId="testProportion">
              <Form.Label 
                  className="testProportion">
                      Train/Test Proportion
              </Form.Label>
              <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>Percentage of data allocated for testing.</p>
                <InputNumber
                    style={{width: "300px", display: "block", margin: "0 auto"}}
                    buttonLayout="horizontal"
                    value={data.setupParam.possibleSettings.defaultSettings.Random.testProportion}
                    onValueChange={(event) => {
                        data.setupParam.possibleSettings.defaultSettings.Random.testProportion = event.target.value;
                        data.internal.settings.Random.testProportion = event.target.value;
                        updateHasWarning(data);
                        setReload(!reload);
                    } }
                    mode="decimal"
                    showButtons
                    min={0.01}
                    max={0.99}
                    step={0.01}
                    incrementButtonClassName="p-button-info"
                    decrementButtonClassName='p-button-info' 
                />

              </Form.Group>

              {/* Seed */}
              <Form.Group controlId="seed">
              <Form.Label 
                  className="seed">
                      Random Seed
              </Form.Label>
              <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>Ensures reproducible random data splitting.</p>
                <InputNumber
                    style={{width: "300px", display: "block", margin: "0 auto"}}
                    buttonLayout="horizontal"
                    value={data.setupParam.possibleSettings.defaultSettings.Random.seed}
                    onValueChange={(event) => {
                        data.setupParam.possibleSettings.defaultSettings.Random.seed = event.target.value;
                        data.internal.settings.Random.seed = event.target.value;
                        updateHasWarning(data);
                        setReload(!reload);
                    } }
                    mode="decimal"
                    min={1}
                />

              </Form.Group>


              </>
            }

            {/* OTHER PARAMS IF SPLIT TYPE IS CV */}
            {data.setupParam.possibleSettings.defaultSettings.active_method?.[0]?.toLowerCase() === "cv" &&
              <>

              {/* Number of splits */}
              <Form.Group controlId="nSplits">
              <Form.Label 
                  className="nSplits">
                      Number of folds
              </Form.Label>
              <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>K value for cross-validation folds (K).</p>
                <InputNumber
                    style={{width: "300px"}}
                    buttonLayout="horizontal"
                    value={data.setupParam.possibleSettings.defaultSettings.cv.nFolds}
                    onValueChange={(event) => {
                      data.setupParam.possibleSettings.defaultSettings.cv.nFolds = event.target.value;
                      data.internal.settings.cv.nFolds = event.target.value;
                      updateHasWarning(data);
                      setReload(!reload);
                    }}
                    mode="decimal"
                    showButtons
                    min={1}
                    incrementButtonClassName="p-button-info"
                    decrementButtonClassName='p-button-info' 
                />

              </Form.Group>
              {/* Seed */}
              <Form.Group controlId="seed">
              <Form.Label 
                  className="seed">
                      Random Seed
              </Form.Label>
              <p style={{fontSize: "13px", fontStyle: "italic", fontWeight: "normal", margin: "0 0 8px 0"}}>Ensures reproducible random data splitting.</p>
                <InputNumber
                    style={{width: "300px", display: "block", margin: "0 auto"}}
                    buttonLayout="horizontal"
                    value={data.setupParam.possibleSettings.defaultSettings.cv.seed}
                    onValueChange={(event) => {
                        data.setupParam.possibleSettings.defaultSettings.cv.seed = event.target.value;
                        data.internal.settings.cv.seed = event.target.value;
                        updateHasWarning(data);
                        setReload(!reload);
                    } }
                    mode="decimal"
                    min={1}
                />

              </Form.Group>
              </>
            }
            </Row>
          </>
        }
      />
    </>
  )
}

export default Design
