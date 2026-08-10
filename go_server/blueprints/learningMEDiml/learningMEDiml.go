package learningMEDiml

import (
	Utils "go_module/src"
	"log"
)

var prePath = "learning_MEDiml"

// AddHandleFunc adds the specific module handle function to the server
func AddHandleFunc() {
	Utils.CreateHandleFunc(prePath+"/run_all/", handleRunExperiment)
	Utils.CreateHandleFunc(prePath+"/get_file_content/", handleGetFileContent)
	Utils.CreateHandleFunc(prePath+"/save_file_content/", handleSaveFileContent)
	Utils.CreateHandleFunc(prePath+"/progress/", handleProgress)
}

// handleRunExperiment handles the request to run an experiment
// It returns the response from the python script
func handleRunExperiment(jsonConfig string, id string) (string, error) {
	log.Println("Running MEDiml experiment...", id)
	response, err := Utils.StartPythonScripts(jsonConfig, "../pythonCode/modules/learning_MEDiml/run_all_learning.py", id)
	if err != nil {
		return "", err
	}
	return response, nil
}

// handleGetFileContent handles the request to get the content of a file
// It returns the content of the file
func handleGetFileContent(jsonConfig string, id string) (string, error) {
	log.Println("Getting file content for MEDiml learning...", id)
	response, err := Utils.StartPythonScripts(jsonConfig, "../pythonCode/modules/learning_MEDiml/get_file_content.py", id)
	if err != nil {
		return "", err
	}
	return response, nil
}

// handleSaveFileContent handles the request to save the content of a file
// It returns a success or error message
func handleSaveFileContent(jsonConfig string, id string) (string, error) {
	log.Println("Saving file content for MEDiml learning...", id)
	response, err := Utils.StartPythonScripts(jsonConfig, "../pythonCode/modules/learning_MEDiml/save_file_content.py", id)
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
