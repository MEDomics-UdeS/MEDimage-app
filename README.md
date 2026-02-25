# MEDiml-app - Develop branch 🛠️

[![GitHub issues](https://img.shields.io/github/issues/MEDomicsLab/MEDiml-app)]()
[![GitHub forks](https://img.shields.io/github/forks/MEDomicsLab/MEDiml-app)]()
[![GitHub stars](https://img.shields.io/github/stars/MEDomicsLab/MEDiml-app)]()
[![GitHub license](https://img.shields.io/github/license/MEDomicsLab/MEDomicsLab)]()

Here is the develop branch of the MEDiml app. This branch is used to develop new features and fix bugs. The main branch is used to publish the latest stable version of the project. The develop branch is merged into the main branch when a new stable version is ready to be published.

### Main documentation 👉 [here](https://medomicslab.gitbook.io/mediml-app-docs/). 👈

### Development documentation 👇

# Getting started - Development

## 1. Git clone the project

```
git clone -b develop git@github.com:MEDomicsLab/MEDiml-app.git      # via SSH (recommended)
git clone -b develop https://github.com/MEDomicsLab/MEDiml-app.git  # via HTTPS
```

## 2. Be sure to have the npm packages installed

```
cd <.../MEDiml-app/>
npm install
```

## 3. When you modify .go files, you need to rebuild the executable

- You can do it manually by running `go build main.go` in the `go_server` folder
- You can also use a script that you can run from the root folder of the project:
  - Windows : `.\utilScripts\pack_GO.bat`
  - Linux : `bash utilScripts/pack_GO_linux.sh`
  - MacOS : `bash utilScripts/pack_GO_mac.sh`

## 4. Python environment

The python environment is installed automatically once you download the app in your user folder under the folder `.mediml`. If you face any issue with the python environment, go to the applicaton settings page, click **Show first setup modal** and click **Start Setup**.


When developping python code, you may need to install new packages. To do so, you can open the terminal from the `.mediml` folder and install the packages using the following commands:

```
cd <USER_PATH>\.mediml\python
python -m pip install <package_name>
```

## 5. Run the Electron app in development mode

`npm run dev`

### Modify startup settings

1. Go to file `medomics.dev.js`
2. Here is a description of the Object:

```javascript
const config = {
  // If true, the server will be run automatically when the app is launched
  runServerAutomatically: true,
  // If true, use the react dev tools
  useRactDevTools: false,
  // the default port to use for the server, be sure that no programs use it by default
  defaultPort: 5000,
  // Either "FIX" or "AVAILABLE" (case sensitive)
  // FIX 		-­> if defaultPort is used, force terminate and use defaultPort
  // AVAILABLE 	-> if defaultPort is used, iterate to find next available port
  portFindingMethod: PORT_FINDING_METHOD.FIX
}
```
