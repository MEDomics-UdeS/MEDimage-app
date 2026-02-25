package extractionMEDiml

import (
	Utils "go_module/src"
	"log"
)

var prePath = "extraction_MEDiml"

// AddHandleFunc adds the specific module handle function to the server
func AddHandleFunc() {
	Utils.CreateHandleFunc(prePath+"/run_all/", handleRunAll)
	Utils.CreateHandleFunc(prePath+"/upload/", handleGetUpload)
	Utils.CreateHandleFunc(prePath+"/progress/", handleProgress)
	Utils.CreateHandleFunc(prePath+"/view/", handleGetView)
}

// handleRunAll handles the request to run extraction using all nodes
// It returns the response from the python script
func handleRunAll(jsonConfig string, id string) (string, error) {
	log.Println("Running all extraction MEDiml", id)
	response, err := Utils.StartPythonScripts(jsonConfig, "../pythonCode/modules/extraction_MEDiml/run_all_extraction.py", id)
	if err != nil {
		return "", err
	}
	return response, nil
}

// handleGetUpload handles the request to upload a scan/image to the server
// It returns the response from the python script
func handleGetUpload(jsonConfig string, id string) (string, error) {
	log.Println("Running get upload for MEDiml extraction", id)
	response, err := Utils.StartPythonScripts(jsonConfig, "../pythonCode/modules/extraction_MEDiml/get_upload.py", id)
	if err != nil {
		return "", err
	}
	return response, nil
}

// handleGetView handles the request to view the scan/image uploaded to the server
// It returns the response from the python script
func handleGetView(jsonConfig string, id string) (string, error) {
	log.Println("Running get view for MEDiml extraction")
	response, err := Utils.StartPythonScripts(jsonConfig, "../pythonCode/modules/extraction_MEDiml/get_view.py", "extractionMEDiml")
	if err != nil {
		return "", err
	}
	return response, nil
}

// handleProgress handles the request to get the progress of the experiment
// It returns the progress of the experiment
func handleProgress(jsonConfig string, id string) (string, error) {
	Utils.Mu.Lock()
	progress := Utils.Scripts[id].Progress
	Utils.Mu.Unlock()
	if progress != "" {
		return progress, nil
	} else {
		return "{\"now\":\"0\", \"currentLabel\":\"Warming up\"}", nil
	}
}
