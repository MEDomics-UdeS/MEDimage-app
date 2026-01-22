import React, { useCallback } from "react"
import { Form, Row, Col } from "react-bootstrap"
import DocLink from "../../docLink"

/**
 * @param {Object} nodeForm form associated to the discretization node
 * @param {Function} changeNodeForm function to change the node form
 * @param {Object} data data of the node
 * @returns {JSX.Element} A DiscretizationForm to display in the modal of a discretization node
 *
 * @description
 * This component is used to display a DiscretizationForm.
 */
const DiscretizationForm = ({ nodeForm, changeNodeForm, data }) => {
  // Get default settings for the discretization node
  const defaultValues = data.setupParam.possibleSettings.defaultSettings

  /**
   * @param {Event} event event given change of a Value in the form
   *
   * @description
   * This function is used to handle the change of a Value in the form.
   */
  const handleChange = useCallback((algo, event) => {
      // Separate event in name and value
      const { name, value } = event.target

      let [nameFeature, nameType] = name.split("-")
      let newValue = null
      if (nameType !== "type"){
        if (algo === "FBN") {
          newValue = parseInt(value)
        } else {
          newValue = parseFloat(value)
        }
      } else {
        newValue = value
      }

      let newDict = { ...nodeForm[nameFeature] }
      if (nameFeature === "texture") {
        if (nameType === "type") {
          newDict[nameType] = [newValue]
        } else {
          newDict[nameType] = [[newValue]]
        }
      } else {
        newDict[nameType] = newValue
      }

      // Modify the event object
      const modifiedEvent = {
        ...event,
        target: {
          ...event.target,
          name: nameFeature,
          value: newDict
        }
      }

      // Pass the modified event to changeNodeForm
      changeNodeForm(modifiedEvent)
    },
    [nodeForm]
  )

  return (
    <Form className="standard-form">
      <DocLink
        linkString={"https://medimage.readthedocs.io/en/latest/configurations_file.html#discretisation"}
        name={"Discretization documentation"}
        image={"https://www.svgrepo.com/show/521262/warning-circle.svg"}
      />

      <Form.Group style={{ paddingTop: "10px" }}>
        <Form.Label>
          <b>Intensity Histogramm</b>
        </Form.Label>
        <Row>
          <Col>
            <Form.Label>Type</Form.Label>
            <Form.Control 
              as="select" 
              name="IH-type" 
              value={nodeForm.IH.type} 
              onChange={(e) => handleChange(nodeForm.IH.type, e)}
            >
              <option value="FBS">FBS</option>
              <option value="FBN">FBN</option>
            </Form.Control>
          </Col>
          <Col>
            <Form.Label>Value</Form.Label>
            <Form.Control 
              className="int" 
              name="IH-val" 
              type="number" 
              value={nodeForm.IH.type === "FBN" ? parseInt(nodeForm.IH.val) : parseFloat(nodeForm.IH.val)}
              placeholder={"Default: " + String(defaultValues.IH.val)} 
              onChange={(e) => handleChange(nodeForm.IH.type, e)} 
            />
          </Col>
        </Row>
      </Form.Group>

      <Form.Group style={{ paddingTop: "10px" }}>
        <Form.Label>
          <b>Intensity Volume Hist</b>
        </Form.Label>
        <Row>
          <Col>
            <Form.Label>Type</Form.Label>
            <Form.Control 
              as="select" 
              name="IVH-type" 
              value={nodeForm.IVH.type} 
              onChange={(e) => handleChange(nodeForm.IVH.type, e)}
            >
              <option value="FBS">FBS</option>
              <option value="FBN">FBN</option>
            </Form.Control>
          </Col>
          <Col>
            <Form.Label>Value</Form.Label>
            <Form.Control 
              className="int" 
              name="IVH-val" 
              type="number" 
              value={nodeForm.IVH.type === "FBN" ? parseInt(nodeForm.IVH.val) : parseFloat(nodeForm.IVH.val)}
              placeholder={"Default: " + String(defaultValues.IVH.val)} 
              onChange={(e) => handleChange(nodeForm.IVH.type, e)} 
            />
          </Col>
        </Row>
      </Form.Group>

      <Form.Group style={{ paddingTop: "10px" }}>
        <Form.Label>
          <b>Texture features</b>
        </Form.Label>
        <Row>
          <Col>
            <Form.Label>Type</Form.Label>
            <Form.Control 
              as="select" 
              name="texture-type" 
              value={nodeForm.texture.type[0]} 
              onChange={(e) => handleChange(nodeForm.texture.type[0], e)}
            >
              <option value="FBS">FBS</option>
              <option value="FBN">FBN</option>
            </Form.Control>
          </Col>
          <Col>
            <Form.Label>Value</Form.Label>
            <Form.Control
              className="int"
              name="texture-val"
              type="number"
              value={nodeForm.texture.type[0] === "FBN" ? parseInt(nodeForm.texture.val[0][0]) : parseFloat(nodeForm.texture.val[0][0])}
              placeholder={"Default: " + String(defaultValues.texture.val[0][0])}
              onChange={(e) => handleChange(nodeForm.texture.type[0], e)}
            />
          </Col>
        </Row>
      </Form.Group>
    </Form>
  )
}

export default DiscretizationForm